from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Project, User, Vacation
from timetracker.hours.models import Hour
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
from .forms import VacationLengthForm, VacationDayForm, ProjectForm
from math import ceil
from datetime import date, datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
import numpy as np


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)


@views.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if request.method == 'POST':
        name = request.form.get('name')
        shortcut = request.form.get('shortcut')
        end_date = request.form.get('end_date')
        phase = request.form.get('phase')
        if Project.query.filter_by(name=name).first():
            flash(f'Project with name {name} already exist!',
                  category='error')
            return redirect(url_for('views.projects'))
        elif Project.query.filter_by(shortcut=shortcut).first():
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
        new_project = Project(name=name, shortcut=shortcut,
                               phase=phase,
                               end_date=end_date)
        db.session.add(new_project)
        db.session.commit()
        flash('Project have been added!', category='success')
        return redirect(url_for('views.project_list'))

    return render_template('projects.html', user=current_user, form=form)


@views.route('/project-list', methods=['GET'])
@login_required
def project_list():
    projects = db.session.query(Project.id, Project.name,
                                Project.shortcut,
                                Project.phase, Project.start_date,
                                Project.end_date,
                                func.ifnull(func.sum(Hour.amount), '0').label(
                                    'sum')).outerjoin(
                                                      Hour, Project.shortcut ==
                                                      Hour.project_shortcut).group_by(Project.id).all()
    return render_template('project_list.html', projects=projects, user=current_user)


@views.route('/update-project/<project_id>', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm()
    if request.method == 'POST':
        if request.form.get('name') != project.name:
            if Project.query.filter_by(name=request.form.get('name')).first():
                flash(f'Project with name {project.name} already exist!',
                      category='error')
                return redirect(url_for('views.update_project', project_id=project.id))
        if request.form.get('shortcut') != project.shortcut:
            if Project.query.filter_by(shortcut=request.form.get('shortcut')).first():
                flash(f'Project with shortcut {project.shortcut} already '
                      f'exist!', category='error')
                return redirect(url_for('views.update_project', project_id=project.id))
        hours = Hour.query.filter_by(project_shortcut=project.shortcut)
        project.name = request.form.get('name')
        project.shortcut = request.form.get('shortcut')
        project.phase = request.form.get('phase')
        project.end_date = request.form.get('end_date')
        print(Project.query.filter_by(name=project.name).first().name)
        if request.form.get('start_date'):
            project.start_date = request.form.get('start_date')
            if project.start_date > project.end_date:
                flash(f'Invalid date of start and end project', category='error')
                return redirect(url_for('views.projects'))
        elif project.end_date < date.today().strftime('%Y-%m-%d'):
            flash(f'Invalid date of end project', category='error')
            return redirect(url_for('views.projects'))
        for hour in hours:
            hour.project_shortcut = project.shortcut
        db.session.commit()
        flash('Project have been updated!', category='success')
        return redirect(url_for('views.project_list'))
    elif request.method == 'GET':
        form.name.data = project.name
        form.shortcut.data = project.shortcut
        form.phase.data = project.phase
        form.end_date.data = datetime.strptime(project.end_date, '%Y-%m-%d').date()
        form.start_date.data = datetime.strptime(project.start_date, '%Y-%m-%d').date()

    return render_template('project_update.html', user=current_user, form=form,
                           start_date=datetime.strptime(project.start_date, '%Y-%m-%d').date(),
                           end_date=datetime.strptime(project.end_date, '%Y-%m-%d').date())


@views.route('/delete-project/<project_id>', methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted!', category='success')
        return redirect(url_for('views.projects'))
    return render_template('project_delete.html', user=current_user, project=project)


@views.route('/vacation-calculation', methods=['GET', 'POST'])
@login_required
def vacation_calculation():
    form = VacationLengthForm()
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
        if not form.seniority.data:
            flash('Seniority must be complete!', category='error')
        else:
            seniority = form.seniority.data
            school = form.school.data
            position = form.position.data
            vacation_days = int(seniority) + school_years[school]
            if form.disability.data:
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
            return redirect(url_for('views.vacation_calculation'))

    return render_template('vacation_calculation.html', user=current_user, form=form,
                           total_vacation_days=worker.total_vacation_days,
                           remaining_vacation_days=worker.rem_vacation_days)


@views.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    form = VacationDayForm()
    worker = User.query.filter_by(id=current_user.id).first()
    days = Vacation.query.filter_by(user_id=current_user.id)
    used_days = days.count()
    worker.rem_vacation_days = worker.total_vacation_days - used_days
    if request.method == 'POST':
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
        return redirect(url_for('views.vacation_list'))

    return render_template('vacation.html', user=current_user, form=form)


@views.route('/vacation-list', methods=['GET'])
@login_required
def vacation_list():
    days = Vacation.query.filter_by(user_id=current_user.id)
    return render_template('vacation_list.html', days=days, user=current_user)


@views.route('/update-vacation/<vacation_day_id>', methods=['GET', 'POST'])
@login_required
def update_vacation_day(vacation_day_id):
    vacation = Vacation.query.get_or_404(vacation_day_id)
    form = VacationDayForm()
    if request.method == 'POST':
        if Vacation.query.filter_by(user_id=current_user.id, vacation_date=request.form.get('vacation_end_date')).first():
            flash(f'Vacation day with date {request.form.get("vacation_end_date")} already exist!',
                  category='error')
            return redirect(url_for('views.update_vacation_day'))
        else:
            vacation.vacation_date = request.form.get('vacation_end_date')
            db.session.commit()
            flash('Vacation day have been updated!', category='success')
            return redirect(url_for('views.vacation_list'))
    elif request.method == 'GET':
        form.vacation_end_date.data = datetime.strptime(vacation.vacation_date, '%Y-%m-%d').date()
    return render_template('vacation_update.html', user=current_user, form=form, date=datetime.strptime(vacation.vacation_date, '%Y-%m-%d').date())


@views.route('/delete-vacation-day/<vacation_day_id>', methods=['GET', 'POST'])
@login_required
def delete_vacation_day(vacation_day_id):
    vacation_day = Vacation.query.get_or_404(vacation_day_id)
    if request.method == 'POST':
        db.session.delete(vacation_day)
        db.session.commit()
        flash('Vacation day deleted!', category='success')
        return redirect(url_for('views.vacation'))
    return render_template('vacation_delete.html', user=current_user, vacation_day=vacation_day)


@views.route('/schedule')
@login_required
def schedule():
    projects_list = Project.query.all()
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