from timetracker import db
from sqlalchemy.sql import func


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacation_date = db.Column(db.String(50), default=func.current_date())
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return f"Vacation day in {self.vacation_date}"
