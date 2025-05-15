from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(10))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attachment = db.Column(db.String(256))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'completed': self.completed,
            'owner': self.owner.username
        }

    def __repr__(self):
        return f'<Task {self.title}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
