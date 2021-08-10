from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, IntegerField
from wtforms import SelectField, SubmitField
from wtforms.widgets.html5 import NumberInput


class HourForm(FlaskForm):
    amount = IntegerField('Number of hours', widget=NumberInput(min=0, max=24, step=0.5))
    work_date = DateField('Date of work', format='%YYYY-%m-%d')
    shortcut = SelectField('Project shortcut')
    confirm_button = SubmitField('Confirm')