from timetracker_app import db


class Overtime(db.Model):
    __tablename__ = 'overtimes'
    id = db.Column(db.Integer, primary_key=True)
    work_date = db.Column(db.Date, nullable=False)
    overtimes_all_employees = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<{self.__class__.__name__}>: In {self.work_date} was {self.sum} overtimes'

