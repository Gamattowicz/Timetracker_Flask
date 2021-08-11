from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Hour
from timetracker.projects.models import Project
from timetracker import db
from flask_login import login_required, current_user
from .forms import HourForm
from datetime import datetime, date
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
        hour_num = int(amount)
        project = Project.query.filter_by(shortcut=project_shortcut).first()
        project_start_date = datetime.strptime(project.start_date, '%Y-%m-%d').date()
        project_end_date = datetime.strptime(project.end_date, '%Y-%m-%d').date()
        if request.form.get('work_date'):
            work_date = request.form.get('work_date')
            work_date_formatted = datetime.strptime(work_date, '%Y-%m-%d').date()
            # Check if working hours date is within the project date range
            if (work_date_formatted - project_start_date).days < 0 or (work_date_formatted - project_end_date).days > 0:
                flash(f'Your working hours date is out of the date range of selected project!', category='error')
                return redirect(url_for('hours.create_hour_view'))
            # Check if user exceeds 24 hours of work during one day
            hours = Hour.query.filter_by(work_date=work_date, user_id=user_id)
            for hour in hours:
                hour_num += hour.amount
            if hour_num > 24:
                flash(f'Your numbers of hours in {work_date} exceeds 24!', category='error')
                return redirect(url_for('hours.create_hour_view'))
            else:
                new_hours = Hour(amount=amount, work_date=work_date,
                                  project_shortcut=project_shortcut,
                                  user_id=user_id)
        else:
            # Check if working hours date is within the project date range
            if (date.today() - project_start_date).days < 0 or (date.today() - project_end_date).days > 0:
                flash(f'Your working hours date is out of the date range of selected project!', category='error')
                return redirect(url_for('hours.create_hour_view'))
            # Check if user exceeds 24 hours of work during one day
            hours = Hour.query.filter_by(work_date=date.today(), user_id=user_id)
            for hour in hours:
                hour_num += hour.amount
            if hour_num > 24:
                flash(f'Your numbers of hours in {date.today()} exceeds 24!', category='error')
                return redirect(url_for('hours.create_hour_view'))
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
        project = Project.query.filter_by(shortcut=hour.project_shortcut).first()
        project_start_date = datetime.strptime(project.start_date, '%Y-%m-%d').date()
        project_end_date = datetime.strptime(project.end_date, '%Y-%m-%d').date()
        work_date_formatted = datetime.strptime(hour.work_date, '%Y-%m-%d').date()
        # Check if working hours date is within the project date range
        if (work_date_formatted - project_start_date).days < 0 or (work_date_formatted - project_end_date).days > 0:
            flash(f'Your working hours date is out of the date range of selected project!', category='error')
            return redirect(url_for('hours.update_hour_view', hour_id=hour_id))
        # Check if user exceeds 24 hours of work during one day
        hour_num = int(hour.amount)
        hours = Hour.query.filter_by(work_date=hour.work_date, user_id=current_user.id)
        for hour in hours:
            hour_num += int(hour.amount)
        if hour_num > 24:
            flash(f'Your numbers of hours in {hour.work_date} exceeds 24!', category='error')
            return redirect(url_for('hours.update_hour_view', hour_id=hour_id))
        else:
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