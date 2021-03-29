from . import db
from sqlalchemy.sql import func


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=True)
    shortcut = db.Column(db.String(50), nullable=True, unique=True)
    hour = db.relationship('Hours')


class Hours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=True)
    work_date = db.Column(db.DateTime(timezone=True), default=func.now())
    project_shortcut = db.Column(db.String(50), db.ForeignKey(
        'projects.shortcut'), nullable=True)