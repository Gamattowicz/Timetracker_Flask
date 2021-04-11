from flask import Blueprint, render_template, request, flash, jsonify
from re import fullmatch
from .models import Projects, Hours
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
import json
from .forms import DatePicker, VacationLength
from math import ceil


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
        if not (isinstance(float(request.form['amount']), float) or isinstance(
                int(request.form['amount']), int)):
            flash('Amount must be a number!', category='error')
        elif request.form['shortcut'] == 'Choose project shortcut':
            flash('You have to choose one of existing shortcut project!',
                  category='error')
        else:
            amount = request.form['amount']
            project_shortcut = request.form['shortcut']
            user_id = current_user.id
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
    hourId = hour['hourId']
    hour = Hours.query.get(hourId)
    if hour:
        db.session.delete(hour)
        db.session.commit()
        flash('Hours deleted!', category='success')
    return jsonify({})


@views.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        if Projects.query.filter_by(name=request.form['name']).first():
            flash(f"Project with name {request.form['name']} already exist!",
                  category='error')
        elif Projects.query.filter_by(shortcut=request.form['shortcut']).first():
            flash(f"Project with shortcut {request.form['shortcut']} already "
                  f"exist!", category='error')
        else:
            name = request.form['name']
            shortcut = request.form['shortcut']

            new_project = Projects(name=name, shortcut=shortcut)
            db.session.add(new_project)
            db.session.commit()
            flash('Project have been added!', category='success')
    results = db.session.query(Projects.id, Projects.name,
                               Projects.shortcut,
                               func.ifnull(func.sum(Hours.amount), '0').label(
                                   'sum')).outerjoin(
                                    Hours, Projects.shortcut ==
                                    Hours.project_shortcut).group_by(Projects.id).all()

    return render_template('projects.html', results=results, user=current_user)


@views.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    form = VacationLength()
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
    total_vacation_days = 0
    if request.method == 'POST':
        if form.seniority.data:
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
    return render_template('vacation.html', user=current_user, form=form,
                           total_vacation_days=total_vacation_days)


@views.route('/overtime')
@login_required
def overtime():
    return render_template('overtime.html', user=current_user)