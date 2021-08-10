from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Hour
from timetracker.models import Project
from timetracker import db
from flask_login import login_required, current_user
from .forms import HourForm
from datetime import datetime
from calendar import day_name


hours = Blueprint('hours', __name__)


@hours.route('/create', methods=['GET', 'POST'])
@login_required
def create_hour_view():
    form = HourForm()
    projects = Project.query.all()
    form.shortcut.choices = [project.shortcut for project in projects]
    if request.method == 'POST':
        amount = request.form.get('amount')
        project_shortcut = request.form.get('shortcut')
        user_id = current_user.id
        if request.form.get('work_date'):
            work_date = request.form.get('work_date')
            print(work_date)
            new_hours = Hour(amount=amount, work_date=work_date,
                              project_shortcut=project_shortcut,
                              user_id=user_id)
        else:
            new_hours = Hour(amount=amount,
                              project_shortcut=project_shortcut,
                              user_id=user_id)
        db.session.add(new_hours)
        db.session.commit()
        flash('Hours have been added!', category='success')
        return redirect(url_for('hours.list_hour_view'))
    return render_template('hour_create.html', user=current_user, form=form)


@hours.route('/', methods=['GET'])
@login_required
def list_hour_view():
    hours = Hour.query.filter_by(user_id=current_user.id)
    return render_template('hour_list.html', hours=hours, user=current_user)


@hours.route('/<hour_id>/update', methods=['GET', 'POST'])
@login_required
def update_hour_view(hour_id):
    hour = Hour.query.get_or_404(hour_id)
    form = HourForm()
    projects = Project.query.all()
    form.shortcut.choices = [project.shortcut for project in projects]
    if request.method == 'POST':
        hour.amount = request.form.get('amount')
        hour.project_shortcut = request.form.get('shortcut')
        hour.work_date = request.form.get('work_date')
        db.session.commit()
        flash('Hours have been updated!', category='success')
        return redirect(url_for('hours.list_hour_view'))
    elif request.method == 'GET':
        form.amount.data = hour.amount
        form.shortcut.data = hour.project_shortcut
        form.work_date.data = datetime.strptime(hour.work_date, '%Y-%m-%d').date()
    return render_template('hour_update.html', user=current_user, form=form, date=datetime.strptime(hour.work_date, '%Y-%m-%d').date())


@hours.route('/<hour_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_hour_view(hour_id):
    hour = Hour.query.get_or_404(hour_id)
    if request.method == 'POST':
        db.session.delete(hour)
        db.session.commit()
        flash('Hours deleted!', category='success')
        return redirect(url_for('hours.list_hour_view'))
    return render_template('hour_delete.html', user=current_user, hour=hour)


@hours.route('/overtime')
@login_required
def overtime_view():
    hours = Hour.query.filter_by(user_id=current_user.id).all()
    work_days = {}
    overtime_list = {}
    for hour in hours:
        try:
            work_days[hour.work_date] += hour.amount
        except KeyError:
            work_days[hour.work_date] = hour.amount
    for day, num in work_days.items():
        date = datetime.strptime(day, '%Y-%m-%d').weekday()
        if day_name[date] != 'Saturday' and day_name[date] != 'Sunday':
            if num > 8:
                try:
                    overtime_list[day] += num - 8
                except KeyError:
                    overtime_list[day] = num - 8
        else:
            try:
                overtime_list[day] += num
            except KeyError:
                overtime_list[day] = num
    overtime = sum([h for d, h in overtime_list.items()])
    working_hours = sum([h for d, h in work_days.items()])
    return render_template('overtime.html', user=current_user,
                           work_days=work_days, overtime_list=overtime_list,
                           overtime=overtime, working_hours=working_hours)