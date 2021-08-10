from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms import SubmitField, StringField


class ProjectForm(FlaskForm):
    name = StringField('Project name')
    shortcut = StringField('Project shortcut')
    start_date = DateField('Project start date', format='%YYYY-%m-%d')
    end_date = DateField('Project end date', format='%YYYY-%m-%d')
    phase = StringField('Project phase')
    confirm_button = SubmitField('Confirm')