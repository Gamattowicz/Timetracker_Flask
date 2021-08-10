from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shortcut = db.Column(db.String(50), nullable=False, unique=True)
    start_date = db.Column(db.String(50), nullable=False, default=func.current_date())
    end_date = db.Column(db.String(50), nullable=False)
    phase = db.Column(db.String(50), nullable=False)
    hour = db.relationship('Hour', backref='project', passive_deletes=True)

    def __repr__(self):
        return f"Project: {self.name}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(50))
    total_vacation_days = db.Column(db.Integer, default=0)
    rem_vacation_days = db.Column(db.Integer, default=0)
    hour = db.relationship('Hour', backref='user', passive_deletes=True)
    vacation = db.relationship('Vacation', backref='user', passive_deletes=True)

    def __repr__(self):
        return f"{self.username}"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacation_date = db.Column(db.String(50), default=func.current_date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Vacation day in {self.vacation_date}"