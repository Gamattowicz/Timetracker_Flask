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
    work_date = db.Column(db.DateTime(timezone=True), default=func.now())
    project_shortcut = db.Column(db.String(50), db.ForeignKey(
        'projects.shortcut'), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50))