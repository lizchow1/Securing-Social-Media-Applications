from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=True)  
    private_key = db.Column(db.LargeBinary, nullable=True)
    certificate = db.Column(db.LargeBinary, nullable=True)  
    groups = db.relationship('Group', secondary='user_groups', backref='users')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False, unique=True)
    public_key = db.Column(db.LargeBinary, nullable=True)
    private_key = db.Column(db.LargeBinary, nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    encrypted_content = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    group = db.relationship('Group', foreign_keys=[group_id], backref='group_messages')

class RevokedCertificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    revocation_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=True)

user_groups = db.Table('user_groups',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                       db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
                       )

