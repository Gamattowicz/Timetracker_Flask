from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from datetime import datetime


class DatePicker(FlaskForm):
    work_date = DateField('Date', format='%YYYY-%m-%d')