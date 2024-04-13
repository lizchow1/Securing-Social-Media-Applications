from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Group, Message, RevokedCertificate, user_groups
from werkzeug.security import generate_password_hash, check_password_hash
from key import encrypt_message, decrypt_message, create_certificate, validate_certificate, get_certificate_serial_number_for_user, generate_key_pair
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or not data['username'].strip() or 'password' not in data or not data['password'].strip():
        return jsonify({"message": "Username and password are required"}), 400

    username = data['username'].strip()  
    password = data['password'].strip()

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already taken"}), 400

    private_key, public_key, certificate = create_certificate(username)

    new_user = User(
        username=username, 
        password=generate_password_hash(password), 
        public_key=public_key, 
        private_key=private_key, 
        certificate=certificate
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        return jsonify({"userid": user.id})
    else:
        return jsonify({"message": "Invalid username or password"}), 401
    
@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = data.get('group_name')

    if not group_name:
        return jsonify({'error': 'Group name is required'}), 400

    if Group.query.filter_by(group_name=group_name).first():
        return jsonify({'error': 'Group name already exists'}), 400
    
    private_key, public_key = generate_key_pair()

    new_group = Group(
        group_name=group_name,
        public_key=public_key,
        private_key=private_key
    )

    try:
        db.session.add(new_group)
        db.session.commit()
        return jsonify({'message': 'Group created successfully', 'group_id': new_group.id}), 201
    except Exception as e:
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
    
    if user not in group.users:
        return jsonify({'message': 'User is not a member of the group'}), 400
    
    group.users.remove(user)
    db.session.commit()

    return jsonify({'message': 'User removed from group successfully'}), 200


@app.route('/send_message_to_group', methods=['POST'])
def send_message_to_group():
    data = request.get_json()
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    message_content = data.get('message')

    if not user_id or not group_id or not message_content:
        return jsonify({'error': 'Missing data for sending a message'}), 400

    user = User.query.get(user_id)
    group = Group.query.get(group_id)

    if not user or not group:
        return jsonify({'error': 'User or Group not found'}), 404

    if not validate_certificate(user.certificate):
        return jsonify({'error': 'User\'s certificate is invalid'}), 403

    try:
        encrypted_message = encrypt_message(group.public_key, message_content)
    except Exception as e:
        return jsonify({'error': 'Failed to encrypt message', 'details': str(e)}), 500

    new_message = Message(
        sender_id=user.id,
        group_id=group.id,
        content=message_content,  
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

    if not user_id:
        return jsonify({'error': 'Missing user ID'}), 400

    user = User.query.get(user_id)
    group = Group.query.get(group_id)

    if not user or not group:
        return jsonify({'error': 'User or group not found'}), 404

    is_member = db.session.query(user_groups).filter_by(user_id=user.id, group_id=group.id).first() is not None

    messages = Message.query.filter_by(group_id=group_id).all()

    if is_member:
        decrypted_messages = [decrypt_message(group.private_key, msg.encrypted_content) for msg in messages]  # Assuming a decrypt_message function exists
        messages_data = [{'content': msg} for msg in decrypted_messages]
    else:
        messages_data = [{'content': msg.content} for msg in messages]

    return jsonify({'messages': messages_data}), 200


@app.route('/revoke_certificate', methods=['POST'])
def revoke_certificate():
    data = request.get_json()
    user_id = data.get('user_id')  

    serial_number = get_certificate_serial_number_for_user(user_id)

    if not serial_number:
        return jsonify({'error': 'Certificate serial number not found'}), 404

    revoked_entry = RevokedCertificate(user_id=serial_number, revocation_date=datetime.utcnow())
    db.session.add(revoked_entry)
    db.session.commit()

    return jsonify({'message': 'Certificate revoked successfully'}), 200

@app.route('/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    group_list = [{'id': group.id, 'group_name': group.group_name} for group in groups]
    return jsonify({'groups': group_list}), 200

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        users_list = [{'id': user.id, 'username': user.username} for user in users]
        return jsonify({'users': users_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/groups/<int:group_id>/users', methods=['GET'])
def get_users_in_group(group_id):
    try:
        group = Group.query.get(group_id)
        if group:
            users = User.query.filter(User.groups.any(id=group_id)).all()
            user_data = [{'id': user.id, 'username': user.username} for user in users]
            return jsonify({'users': user_data}), 200
        else:
            return jsonify({'error': 'Group not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    username = request.args.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'user_id': user.id}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Username parameter is missing'}), 400
