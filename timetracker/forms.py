from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, IntegerField
from wtforms import BooleanField, SelectField, SubmitField, StringField
from wtforms.widgets.html5 import NumberInput


class VacationLength(FlaskForm):
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


class VacationDay(FlaskForm):
    vacation_date = DateField('The date of the vacation day', format='%YYYY-%m-%d')
    confirm_button = SubmitField('Confirm')


class Project(FlaskForm):
    name = StringField('Project name')
    shortcut = StringField('Project shortcut')
    start_date = DateField('Project start date', format='%YYYY-%m-%d')
    end_date = DateField('Project end date', format='%YYYY-%m-%d')
    phase = StringField('Project phase')
    confirm_button = SubmitField('Confirm')


class Hour(FlaskForm):
    amount = IntegerField('Number of hours', widget=NumberInput(min=0,
                                                                   max=24,
                                                                   step=0.5))
    work_date = DateField('Date of work', format='%YYYY-%m-%d')
    shortcut = SelectField('Project shortcut')
    confirm_button = SubmitField('Confirm')