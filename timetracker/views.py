from flask import Blueprint, render_template, request, flash, jsonify
from .models import Projects, Hours, User, Vacation
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
import json
from .forms import DatePicker, VacationLength, VacationDay, Project
from math import ceil
from datetime import date, datetime
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
import numpy as np
from calendar import day_name


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        print('<h1> Good </h1>')
    return render_template('home.html', user=current_user)


@views.route('/hours', methods=['GET', 'POST'])
@login_required
def hours():
    form = DatePicker()
    if request.method == 'POST':
        amount = request.form['amount']
        project_shortcut = request.form['shortcut']
        user_id = current_user.id
        if not (isinstance(float(amount), float) or isinstance(
                int(amount), int)):
            flash('Amount must be a number!', category='error')
        elif project_shortcut == 'Choose project shortcut':
            flash('You have to choose one of existing shortcut project!',
                  category='error')
        else:
            if request.form['work_date']:
                work_date = request.form['work_date']
                new_hours = Hours(amount=amount, work_date=work_date,
                                  project_shortcut=project_shortcut,
                                  user_id=user_id)
                db.session.add(new_hours)
                db.session.commit()
                flash('Hours have been added!', category='success')
            else:
                new_hours = Hours(amount=amount,
                                  project_shortcut=project_shortcut,
                                  user_id=user_id)
                db.session.add(new_hours)
                db.session.commit()
                flash('Hours have been added!', category='success')

    results = Hours.query.all()
    projects = Projects.query.all()
    return render_template('hours.html', results=results, projects=projects,
                           user=current_user, form=form)


@views.route('/delete-hour', methods=['POST'])
def delete_hour():
    hour = json.loads(request.data)
    hour_id = hour['hourId']
    hour = Hours.query.get(hour_id)
    if hour:
        db.session.delete(hour)
        db.session.commit()
        flash('Hours deleted!', category='success')
    return jsonify({})


@views.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = Project()
    if request.method == 'POST':
        name = request.form['name']
        shortcut = request.form['shortcut']
        end_date = request.form['end_date']
        phase = request.form['phase']
        if Projects.query.filter_by(name=name).first():
            flash(f'Project with name {name} already exist!',
                  category='error')
        elif Projects.query.filter_by(shortcut=shortcut).first():
            flash(f'Project with shortcut {shortcut} already'
                  f'exist!', category='error')
        elif request.form['start_date']:
            start_date = request.form['start_date']
            if start_date > end_date:
                flash(f'Invalid date of start and end project', category='error')
            else:
                new_project = Projects(name=name, shortcut=shortcut,
                                       phase=phase,
                                       start_date=start_date, end_date=end_date)
                db.session.add(new_project)
                db.session.commit()
                flash('Project have been added!', category='success')
        else:
            if end_date < date.today().strftime('%Y-%m-%d'):
                flash(f'Invalid date of end project', category='error')
            else:
                new_project = Projects(name=name, shortcut=shortcut,
                                       phase=phase,
                                       end_date=end_date)
                db.session.add(new_project)
                db.session.commit()
                flash('Project have been added!', category='success')
    results = db.session.query(Projects.id, Projects.name,
                               Projects.shortcut,
                               Projects.phase, Projects.start_date,
                               Projects.end_date,
                               func.ifnull(func.sum(Hours.amount), '0').label(
                                   'sum')).outerjoin(
                                    Hours, Projects.shortcut ==
                                    Hours.project_shortcut).group_by(Projects.id).all()

    return render_template('projects.html', results=results,
                           user=current_user, form=form)


@views.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    form_l = VacationLength()
    form_d = VacationDay()
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
    if request.method == 'POST':
        if form_l.submit_button.data:
            if not form_l.seniority.data:
                flash('Seniority must be complete!', category='error')
            else:
                seniority = form_l.seniority.data
                school = form_l.school.data
                position = form_l.position.data
                vacation_days = int(seniority) + school_years[school]
                if form_l.disability.data:
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
        elif form_d.confirm_button.data:
            if request.form['vacation_date']:
                vacation_date = request.form['vacation_date']
                new_vacation_day = Vacation(vacation_date=vacation_date, user_id=current_user.id)
                db.session.add(new_vacation_day)
                db.session.commit()
                flash('Vacation day have been added!', category='success')

    days = Vacation.query.all()
    used_days = Vacation.query.filter_by(user_id=current_user.id).count()
    worker.rem_vacation_days = worker.total_vacation_days - used_days

    return render_template('vacation.html', user=current_user, form_l=form_l, form_d=form_d,
                           total_vacation_days=worker.total_vacation_days,
                           rem_days_off=worker.rem_vacation_days,
                           days=days)


@views.route('/delete-vacation-day', methods=['POST'])
def delete_vacation_day():
    day = json.loads(request.data)
    day_id = day['dayId']
    day = Vacation.query.get(day_id)
    if day:
        db.session.delete(day)
        db.session.commit()
        flash('Day deleted!', category='success')
    return jsonify({})


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
    fig = Figure(figsize=(13, 6), dpi=100)
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