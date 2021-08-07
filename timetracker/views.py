from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Projects, Hours, User, Vacation
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
from .forms import HourForm, VacationLength, VacationDay, ProjectForm
from math import ceil
from datetime import date, datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
import numpy as np
from calendar import day_name


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)


@views.route('/hours', methods=['GET', 'POST'])
@login_required
def hours():
    form = HourForm()
    projects = Projects.query.all()
    form.shortcut.choices = [project.shortcut for project in projects]
    if request.method == 'POST':
        amount = request.form.get('amount')
        project_shortcut = request.form.get('shortcut')
        user_id = current_user.id
        if request.form.get('work_date'):
            work_date = request.form.get('work_date')
            new_hours = Hours(amount=amount, work_date=work_date,
                              project_shortcut=project_shortcut,
                              user_id=user_id)
        else:
            new_hours = Hours(amount=amount,
                              project_shortcut=project_shortcut,
                              user_id=user_id)
        db.session.add(new_hours)
        db.session.commit()
        flash('Hours have been added!', category='success')
        return redirect(url_for('views.hour_list'))

    return render_template('hours.html', user=current_user, form=form)


@views.route('/hour-list', methods=['GET'])
@login_required
def hour_list():
    hours = Hours.query.filter_by(user_id=current_user.id)
    return render_template('hour_list.html', hours=hours, user=current_user)


@views.route('/delete-hour/<hour_id>')
def delete_hour(hour_id):
    hour = Hours.query.filter_by(id=hour_id).first()
    if not hour:
        flash('Hours do not exist', category='error')
    else:
        db.session.delete(hour)
        db.session.commit()
        flash('Hours deleted!', category='success')
    return redirect(url_for('views.hour_list'))


@views.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if request.method == 'POST':
        name = request.form.get('name')
        shortcut = request.form.get('shortcut')
        end_date = request.form.get('end_date')
        phase = request.form.get('phase')
        if Projects.query.filter_by(name=name).first():
            flash(f'Project with name {name} already exist!',
                  category='error')
            return redirect(url_for('views.projects'))
        elif Projects.query.filter_by(shortcut=shortcut).first():
            flash(f'Project with shortcut {shortcut} already '
                  f'exist!', category='error')
            return redirect(url_for('views.projects'))
        elif request.form.get('start_date'):
            start_date = request.form.get('start_date')
            if start_date > end_date:
                flash(f'Invalid date of start and end project', category='error')
                return redirect(url_for('views.projects'))
        elif end_date < date.today().strftime('%Y-%m-%d'):
            flash(f'Invalid date of end project', category='error')
            return redirect(url_for('views.projects'))
        new_project = Projects(name=name, shortcut=shortcut,
                               phase=phase,
                               end_date=end_date)
        db.session.add(new_project)
        db.session.commit()
        flash('Project have been added!', category='success')
        return redirect(url_for('views.projects'))
    projects = db.session.query(Projects.id, Projects.name,
                                Projects.shortcut,
                                Projects.phase, Projects.start_date,
                                Projects.end_date,
                                func.ifnull(func.sum(Hours.amount), '0').label(
                                   'sum')).outerjoin(
                                    Hours, Projects.shortcut ==
                                    Hours.project_shortcut).group_by(Projects.id).all()

    return render_template('projects.html', projects=projects,
                           user=current_user, form=form)


@views.route('/delete-project/<project_id>')
def delete_project(project_id):
    project = Projects.query.filter_by(id=project_id).first()
    if not project:
        flash('Project does not exist', category='error')
    else:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted!', category='success')
    return redirect(url_for('views.projects'))


@views.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    form_vacation_length = VacationLength()
    form_vacation_day = VacationDay()
    school_years = {
        'Basic vocational school': 3,
        'High vocational school': 5,
        'High school': 4,
        'Post-high school': 6,
        'Bachelor/Masters degree': 8
    }
    job_position = {
        'Full-time': 1,
        'Half-time': 0.5,
        '1/3 time': (1/3),
        '2/3 time': (2/3),
        '1/4 time': 0.25,
        '3/4 time': 0.75
    }
    worker = User.query.filter_by(id=current_user.id).first()
    days = Vacation.query.filter_by(user_id=current_user.id)
    used_days = days.count()
    worker.rem_vacation_days = worker.total_vacation_days - used_days
    if request.method == 'POST':
        if form_vacation_length.submit_button.data:
            if not form_vacation_length.seniority.data:
                flash('Seniority must be complete!', category='error')
            else:
                seniority = form_vacation_length.seniority.data
                school = form_vacation_length.school.data
                position = form_vacation_length.position.data
                vacation_days = int(seniority) + school_years[school]
                if form_vacation_length.disability.data:
                    if vacation_days > 10:
                        total_vacation_days = ceil(36 * job_position[position])
                    else:
                        total_vacation_days = ceil(30 * job_position[position])
                else:
                    if vacation_days > 10:
                        total_vacation_days = ceil(26 * job_position[position])
                    else:
                        total_vacation_days = ceil(20 * job_position[position])
                worker.total_vacation_days = total_vacation_days
                db.session.commit()
                return redirect(url_for('views.vacation'))
        elif form_vacation_day.confirm_button.data:
            if request.form.get('vacation_start_date') and request.form.get('vacation_end_date'):
                end_date = datetime.strptime(request.form.get('vacation_end_date'), '%Y-%m-%d').date()
                vacation_date = datetime.strptime(request.form.get('vacation_start_date'), '%Y-%m-%d').date() - timedelta(days=1)
                vacation_length = (end_date - vacation_date).days
                if vacation_length < 0:
                    flash(f'Incorrect vacation dates!', category='error')
                    return redirect(url_for('views.vacation'))
                for day in range(vacation_length):
                    vacation_date += timedelta(days=1)
                    if Vacation.query.filter_by(user_id=current_user.id, vacation_date=vacation_date).first():
                        flash(f'Vacation day with date {vacation_date} already exist!',
                              category='error')
                        return redirect(url_for('views.vacation'))
                    elif worker.rem_vacation_days < vacation_length:
                        flash(f'You do not have enough vacation days in this year.', category='error')
                        return redirect(url_for('views.vacation'))
                    new_vacation_day = Vacation(vacation_date=vacation_date, user_id=current_user.id)
                    db.session.add(new_vacation_day)
            else:
                if Vacation.query.filter_by(user_id=current_user.id, vacation_date=date.today()).first():
                    flash(f'Vacation day with date {date.today()} already exist!',
                          category='error')
                    return redirect(url_for('views.vacation'))
                else:
                    new_vacation_day = Vacation(user_id=current_user.id)
                    db.session.add(new_vacation_day)
            db.session.commit()
            flash('Vacation day have been added!', category='success')
            return redirect(url_for('views.vacation'))

    return render_template('vacation.html', user=current_user, form_vacation_length=form_vacation_length,
                           form_vacation_day=form_vacation_day, total_vacation_days=worker.total_vacation_days,
                           remaining_vacation_days=worker.rem_vacation_days, days=days)


@views.route('/delete-vacation-day/<vacation_day_id>')
def delete_vacation_day(vacation_day_id):
    vacation_day = Vacation.query.filter_by(id=vacation_day_id).first()
    if not vacation_day:
        flash('Vacation day does not exist', category='error')
    else:
        db.session.delete(vacation_day)
        db.session.commit()
        flash('Vacation day deleted!', category='success')
    return redirect(url_for('views.vacation'))


@views.route('/overtime')
@login_required
def overtime():
    hours = Hours.query.filter_by(user_id=current_user.id).all()
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


@views.route('/schedule')
@login_required
def schedule():
    projects_list = Projects.query.all()
    fig = Figure(figsize=(13, 4.4), dpi=100)
    ax = fig.add_subplot()
    y_ticks = []
    y_tick_value = 10
    colors = list(np.random.rand(len(projects_list), 3))
    for project in projects_list:
        start_date = datetime.strptime(project.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(project.end_date, '%Y-%m-%d').date()
        delta = end_date - start_date
        ax.broken_barh([(start_date, delta)], (y_tick_value, 9),
                       facecolors=colors.pop())
        y_ticks.append(y_tick_value + 5)
        y_tick_value += 10
    ax.grid(True)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([project.name for project in projects_list])
    fmt_month = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_month)
    fig.autofmt_xdate()
    fig.suptitle('Projects start and end dates', fontsize=20)
    fig.supxlabel('Start and end dates', fontsize=14)
    fig.supylabel('Names of projects', fontsize=14)

    png_image = io.BytesIO()
    FigureCanvas(fig).print_png(png_image)

    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(png_image.getvalue()).decode('utf8')

    return render_template('schedule.html', user=current_user, image=pngImageB64String)