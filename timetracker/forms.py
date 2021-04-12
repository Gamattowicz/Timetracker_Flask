from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, IntegerField
from wtforms import BooleanField, SelectField, SubmitField
from wtforms.widgets.html5 import NumberInput
from datetime import datetime


class DatePicker(FlaskForm):
    work_date = DateField('Date', format='%YYYY-%m-%d')


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