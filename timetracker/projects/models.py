from timetracker import db
from sqlalchemy.sql import func


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shortcut = db.Column(db.String(50), nullable=False, unique=True)
    start_date = db.Column(db.String(50), nullable=False, default=func.current_date())
    end_date = db.Column(db.String(50), nullable=False)
    phase = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    hour = db.relationship("Hour", backref="project", passive_deletes=True)

    def __repr__(self):
        return f"Project: {self.name}"
