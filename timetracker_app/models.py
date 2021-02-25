from timetracker_app import db


class Overtimes(db.model):
    __tablename__ = 'overtimes'
    id = db.Column(db.Integer, primary_key=True)
    work_date = db.Column(db.Date, nullable=False)
    sum = db.Column(db.Integer, default=0)

