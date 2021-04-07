from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField


class DatePicker(FlaskForm):
    work_date = DateField('Pick Date', format='%YYYY-%m-%d')