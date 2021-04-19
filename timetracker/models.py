from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Projects(db.Model):
    __tablename__ == 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shortcut = db.Column(db.String(50), nullable=False, unique=True)
    start_date = db.Column(db.String(50), nullable=False, default=func.current_date())
    end_date = db.Column(db.String(50), nullable=False)
    phase = db.Column(db.String(50), nullable=False)
    hour = db.relationship('Hours')

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.name} {self.shortcut}'


class Hours(db.Model):
    __tablename__ == 'hours'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    work_date = db.Column(db.String(50), default=func.current_date())
    project_shortcut = db.Column(db.String(50), db.ForeignKey(
        'projects.shortcut'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.amount} ' \
               f'{self.project_shortcut} {self.user_id}'


class User(db.Model, UserMixin):
    __tablename__ == 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(50))
    total_vacation_days = db.Column(db.Integer, default=0)
    rem_vacation_days = db.Column(db.Integer, default=0)
    hour = db.relationship('Hours')
    vacation = db.relationship('Vacation')

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.username}'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Vacation(db.Model):
    __tablename__ == 'users'
    id = db.Column(db.Integer, primary_key=True)
    vacation_date = db.Column(db.String(50), default=func.current_date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.vacation_date} {self.user_id}'