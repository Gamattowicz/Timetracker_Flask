from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shortcut = db.Column(db.String(50), nullable=False, unique=True)
    hour = db.relationship('Hours')


class Hours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    work_date = db.Column(db.String(50), default=func.current_date())
    project_shortcut = db.Column(db.String(50), db.ForeignKey(
        'projects.shortcut'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50))
    vacation_days = db.Column(db.Integer, default=0)
    hour = db.relationship('Hours')
    vacation = db.relationship('Vacation')


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacation_date = db.Column(db.String(50), default=func.current_date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))