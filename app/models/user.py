from .. import db  # Go up one level to app/__init__.py
from flask_login import UserMixin
from enum import Enum
from datetime import datetime

class UserPrivilege(Enum):
    READ = 'Read'
    WRITE = 'Write'
    ADMIN = 'Admin'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    privilege = db.Column(db.Enum(UserPrivilege), default=None, nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'