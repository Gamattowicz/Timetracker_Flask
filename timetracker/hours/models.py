from timetracker import db
from sqlalchemy.sql import func


class Hour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    work_date = db.Column(db.String(50), default=func.current_date())
    project_shortcut = db.Column(db.String(50), db.ForeignKey(
        'project.shortcut'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"{self.amount} hours"