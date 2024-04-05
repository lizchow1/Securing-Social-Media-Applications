from flask import Flask, request, jsonify
from models import db, User, Group, Message, RevokedCertificate
from werkzeug.security import generate_password_hash, check_password_hash
from key import encrypt_message, decrypt_message, generate_key_pair, create_certificate, load_ca_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400

    username = data['username']
    password = data['password']  

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already taken"}), 400

    # Generate key pair
    private_key, public_key = generate_key_pair()
    
    # Assuming ca_private_key is available somehow, e.g., loaded from a secure location
    ca_private_key = load_ca_private_key()

    # Create a certificate for the user's public key
    certificate = create_certificate(username, private_key, ca_private_key)

    # Store keys and certificate as bytes in database
    new_user = User(username=username, password=generate_password_hash(password), public_key=public_key, private_key=private_key, certificate=certificate)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid username or password"}), 401
    
@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = data.get('group_name')

    if not group_name:
        return jsonify({'error': 'Group name is required'}), 400

    # Check if the group name already exists
    if Group.query.filter_by(group_name=group_name).first():
        return jsonify({'error': 'Group name already exists'}), 400
    
    private_key, public_key = generate_key_pair()

    # Create a new group with the generated keys
    new_group = Group(
        group_name=group_name,
        public_key=public_key,
        private_key=private_key
    )

    try:
        # Add the group to the database session and commit
        db.session.add(new_group)
        db.session.commit()
        return jsonify({'message': 'Group created successfully', 'group_id': new_group.id}), 201
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify({'error': 'Failed to create group', 'details': str(e)}), 500


@app.route('/add_user', methods=['POST'])
def add_user_to_group():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:
        return jsonify({'error': 'Group or user not found'}), 404

    revoked_certificate = RevokedCertificate.query.filter_by(user_id=user_id).first()
    if revoked_certificate:
        return jsonify({'error': 'User\'s certificate has been revoked and is therefore invalid'}), 403
    
    is_member = User.query.join(User.groups).filter(User.id == user_id, Group.id == group_id).first()
    if is_member:
        return jsonify({'message': 'User is already a member of the group'}), 200

    group.users.append(user)
    db.session.commit()

    return jsonify({'message': 'User added to group successfully'}), 200

@app.route('/remove_user', methods=['POST'])
def remove_user_to_group():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:  
        return jsonify({'message':'group or user was not found'}), 404
    
    group.users.remove(user)
    db.session.commit()

    return jsonify({'message': 'User removed from group successfully'}), 200


@app.route('/send_message_to_group', methods=['POST'])
def send_message_to_group():
    # Retrieve data from the request
    data = request.get_json()
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    message_content = data.get('message')

    # Validate data presence
    if not user_id or not group_id or not message_content:
        return jsonify({'error': 'Missing data for sending a message'}), 400

    # Fetch the sender (user) and the recipient group from the database
    user = User.query.get(user_id)
    group = Group.query.get(group_id)

    if not user or not group:
        return jsonify({'error': 'User or Group not found'}), 404

    # Check if the user's certificate has been revoked
    revoked_certificate = RevokedCertificate.query.filter_by(user_id=user_id).first()
    if revoked_certificate:
        return jsonify({'error': 'User\'s certificate has been revoked'}), 403

    # Proceed with encryption using the group's public key
    try:
        group_public_key = serialization.load_pem_public_key(
            group.public_key,
            backend=default_backend()
        )
        encrypted_message = encrypt_message(group_public_key, message_content)
    except Exception as e:
        return jsonify({'error': 'Failed to encrypt message', 'details': str(e)}), 500

    # Create and save the message instance
    new_message = Message(
        sender_id=user.id,
        group_id=group.id,
        content=message_content,  # Storing both for demonstration; in practice, might only store encrypted
        encrypted_content=encrypted_message
    )
    
    try:
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

    return jsonify({'message_content': message_content}, {'message':'message sent successfully'}), 200

@app.route('/view_message_in_group', methods=['GET'])
def view_message_in_group():
    group_id = request.args.get('group_id')
    user_id = request.args.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:
        return jsonify({'error': 'Group or user not found'}), 404

    # Check if the user is a member of the group
    if user not in group.users:
        return jsonify({'error': 'User is not a member of the group'}), 403

    # Retrieve all messages for the group
    messages = Message.query.filter_by(group_id=group_id).all()

    decrypted_messages = []
    for message in messages:
        # If the user is the sender, show the original message
        if message.sender_id == user_id:
            decrypted_messages.append({'message': message.content})
        else:
            # If the user is not the sender, show the decrypted message if available
            if message.encrypted_content:
                # Get group's private key
                group_private_key = group.private_key
                # Decrypt the message
                decrypted_message = decrypt_message(group_private_key, message.encrypted_content)
                decrypted_messages.append({'message': decrypted_message})
            else:
                decrypted_messages.append({'message': '[Encrypted]'})

    return jsonify({'messages': decrypted_messages}), 200

def revoke_certificate(user_id, reason=None):
    revocation_entry = RevokedCertificate(
        user_id=user_id,
        revocation_date=datetime.utcnow(),
        reason=reason
    )
    db.session.add(revocation_entry)
    db.session.commit()
