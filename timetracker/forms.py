from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, IntegerField
from wtforms import BooleanField, SelectField, SubmitField, StringField, \
    TextField, PasswordField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, Length, EqualTo
from .models import User


class VacationLengthForm(FlaskForm):
    seniority = IntegerField('Seniority', widget=NumberInput(min=0, max=60,
                                                             step=1))
    disability = BooleanField('Certificate of disability', false_values=(False, 'false', '',))
    school = SelectField('The type of school you graduated', choices=[
        ('Basic vocational school'), ('High vocational school'),
        ('High school'), ('Post-high school'),
        ('Bachelor/Masters degree')])
    position = SelectField('Job position', choices=[('Full-time'),
                                                    ('Half-time'),
                                                    ('1/3 time'), ('2/3 time'),
                                                    ('1/4 time'), ('3/4 time')])
    submit_button = SubmitField('Submit')


class VacationDayForm(FlaskForm):
    vacation_start_date = DateField('The start date of the vacation day', format='%YYYY-%m-%d')
    vacation_end_date = DateField('The end date of the vacation day', format='%YYYY-%m-%d')
    confirm_button = SubmitField('Confirm')


class ProjectForm(FlaskForm):
    name = StringField('Project name')
    shortcut = StringField('Project shortcut')
    start_date = DateField('Project start date', format='%YYYY-%m-%d')
    end_date = DateField('Project end date', format='%YYYY-%m-%d')
    phase = StringField('Project phase')
    confirm_button = SubmitField('Confirm')


class HourForm(FlaskForm):
    amount = IntegerField('Number of hours', widget=NumberInput(min=0, max=24, step=0.5))
    work_date = DateField('Date of work', format='%YYYY-%m-%d')
    shortcut = SelectField('Project shortcut')
    confirm_button = SubmitField('Confirm')


class RegisterForm(FlaskForm):
    username = TextField('Username',
            validators=[DataRequired(), Length(min=3, max=32)])

    password = PasswordField('Password',
            validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('Verify password',
            validators=[DataRequired(), EqualTo('password',
            message='Passwords must match')])
    confirm_button = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        return True


class LoginForm(FlaskForm):
    username = TextField('Username',
                      validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Unknown username')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        return True