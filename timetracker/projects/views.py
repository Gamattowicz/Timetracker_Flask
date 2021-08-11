from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Project
from timetracker.hours.models import Hour
from timetracker import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
from .forms import ProjectForm
from datetime import date, datetime
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
import numpy as np


projects = Blueprint('projects', __name__)


@projects.route('/create', methods=['GET', 'POST'])
@login_required
def create_project_view():
    form = ProjectForm()
    if request.method == 'POST':
        name = request.form.get('name')
        shortcut = request.form.get('shortcut')
        end_date = request.form.get('end_date')
        phase = request.form.get('phase')
        if Project.query.filter_by(name=name).first():
            flash(f'Project with name {name} already exist!',
                  category='error')
            return redirect(url_for('projects.create_project_view'))
        elif Project.query.filter_by(shortcut=shortcut).first():
            flash(f'Project with shortcut {shortcut} already '
                  f'exist!', category='error')
            return redirect(url_for('projects.create_project_view'))
        if request.form.get('start_date'):
            start_date = request.form.get('start_date')
            if start_date > end_date:
                flash(f'Invalid date of start and end project', category='error')
                return redirect(url_for('projects.create_project_view'))
            new_project = Project(name=name, shortcut=shortcut,
                                   phase=phase, start_date=start_date,
                                   end_date=end_date)
        else:
            start_date = date.today().strftime('%Y-%m-%d')
            if end_date < start_date:
                flash(f'Invalid date of end project', category='error')
                return redirect(url_for('projects.create_project_view'))
            new_project = Project(name=name, shortcut=shortcut,
                                   phase=phase,
                                   end_date=end_date)
        db.session.add(new_project)
        db.session.commit()
        flash('Project have been added!', category='success')
        return redirect(url_for('projects.list_project_view'))
    return render_template('project_create.html', user=current_user, form=form)


@projects.route('/', methods=['GET'])
@login_required
def list_project_view():
    projects = db.session.query(Project.id, Project.name,
                                Project.shortcut,
                                Project.phase, Project.start_date,
                                Project.end_date, Project.active,
                                func.ifnull(func.sum(Hour.amount), '0').label(
                                    'sum')).outerjoin(
                                                      Hour, Project.shortcut ==
                                                      Hour.project_shortcut).group_by(Project.id).all()
    return render_template('project_list.html', projects=projects, user=current_user)


@projects.route('/<project_id>/update', methods=['GET', 'POST'])
@login_required
def update_project_view(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm()
    if request.method == 'POST':
        if request.form.get('name') != project.name:
            if Project.query.filter_by(name=request.form.get('name')).first():
                flash(f'Project with name {project.name} already exist!',
                      category='error')
                return redirect(url_for('projects.update_project_view', project_id=project.id))
        if request.form.get('shortcut') != project.shortcut:
            if Project.query.filter_by(shortcut=request.form.get('shortcut')).first():
                flash(f'Project with shortcut {project.shortcut} already '
                      f'exist!', category='error')
                return redirect(url_for('projects.update_project_view', project_id=project.id))
        hours = Hour.query.filter_by(project_shortcut=project.shortcut)
        project.name = request.form.get('name')
        project.shortcut = request.form.get('shortcut')
        project.phase = request.form.get('phase')
        project.end_date = request.form.get('end_date')
        project.active = bool(request.form.get('active'))
        if request.form.get('start_date'):
            project.start_date = request.form.get('start_date')
            if project.start_date > project.end_date:
                flash(f'Invalid date of start and end project', category='error')
                return redirect(url_for('projects.update_project_view', project_id=project.id))
        elif project.end_date < date.today().strftime('%Y-%m-%d'):
            flash(f'Invalid date of end project', category='error')
            return redirect(url_for('projects.update_project_view', project_id=project_id))
        for hour in hours:
            hour.project_shortcut = project.shortcut
        db.session.commit()
        flash('Project have been updated!', category='success')
        return redirect(url_for('projects.list_project_view'))
    elif request.method == 'GET':
        form.name.data = project.name
        form.shortcut.data = project.shortcut
        form.phase.data = project.phase
        form.end_date.data = datetime.strptime(project.end_date, '%Y-%m-%d').date()
        form.start_date.data = datetime.strptime(project.start_date, '%Y-%m-%d').date()
        form.active.data = project.active

    return render_template('project_update.html', user=current_user, form=form,
                           start_date=datetime.strptime(project.start_date, '%Y-%m-%d').date(),
                           end_date=datetime.strptime(project.end_date, '%Y-%m-%d').date())


@projects.route('/<project_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_project_view(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted!', category='success')
        return redirect(url_for('projects.list_project_view'))
    return render_template('project_delete.html', user=current_user, project=project)


@projects.route('/schedule')
@login_required
def schedule_view():
    projects_list = Project.query.filter_by(active=True).all()
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