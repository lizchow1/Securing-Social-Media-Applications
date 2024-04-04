from flask import Flask, request, jsonify
from models import db, User, Group, Message
from werkzeug.security import generate_password_hash, check_password_hash
from key import encrypt_message, decrypt_message, generate_key_pair
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

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

    # Store keys as bytes in database
    new_user = User(username=username, password=generate_password_hash(password), public_key=private_key, private_key=public_key)
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
    
    private_key, public_key = generate_key_pair()

    # Create a new group with the generated keys
    new_group = Group(
        group_name="New Group",
        private_key=private_key,
        public_key=public_key
    )

    # Add the group to the database session and commit
    db.session.add(new_group)
    db.session.commit()

    return jsonify({'message': 'Group created successfully'}), 201

@app.route('/add_user', methods=['POST'])
def add_user_to_group():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:
        return jsonify({'error': 'Group or user not found'}), 404

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
        return jsonify({'group or user was not found'}), 404
    
    group.users.remove(user)
    db.session.commit()

    return jsonify({'message': 'User removed from group successfully'}), 200


@app.route('/send_message_to_group', methods=['POST'])
def send_message_to_group():
    data = request.get_json()
    sender_id = data.get('sender_id')
    group_id = data.get('group_id')
    message = data.get('message')

    sender = User.query.get(sender_id)
    group = Group.query.get(group_id)

    if not sender or not group:
        return jsonify({'error': 'Sender or group not found'}), 404

    key = group.public_key
    print(key)
    # Load the group's public key
    group_public_key = serialization.load_pem_public_key(group.public_key, backend=default_backend())

    # Encrypt the message
    encrypted_message = encrypt_message(group_public_key, message)

    # Create a new Message object
    new_message = Message(
        sender_id=sender_id,
        group_id=group_id,
        content=message,
        encrypted_content=encrypted_message,
    )

    # Add the message to the database session
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 200

@app.route('/receive_message', methods=['GET'])
def receive_message():
    sender_id = request.args.get('sender_id')
    recipient_id = request.args.get('recipient_id')

    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not sender or not recipient:
        return jsonify({'error': 'Sender or recipient not found'}), 404

    # Check if sender and recipient are in the same group
    sender_group_ids = {group.id for group in sender.groups}
    recipient_group_ids = {group.id for group in recipient.groups}
    common_group_ids = sender_group_ids.intersection(recipient_group_ids)

    if not common_group_ids:
        # Users are not in the same group, return encrypted message
        message = Message.query.filter_by(sender_id=sender_id, recipient_id=recipient_id).first()
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify({'message': message.encrypted_content}), 200

    # Users are in the same group, proceed with decryption
    message = Message.query.filter_by(sender_id=sender_id, recipient_id=recipient_id).first()
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    # Get recipient's private key (you might have it stored securely)
    recipient_private_key = recipient.private_key  # Adjust this based on your actual implementation

    # Decrypt the message
    decrypted_message = decrypt_message(recipient_private_key, message.encrypted_content)

    return jsonify({'message': decrypted_message}), 200

@app.route('/view_message', methods=['GET'])
def view_message():
    group_id = request.args.get('group_id')
    user_id = request.args.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:
        return jsonify({'error': 'Group or user not found'}), 404

    # Check if the user is a member of the group
    if user not in group.members:
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
