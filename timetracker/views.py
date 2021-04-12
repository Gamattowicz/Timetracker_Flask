from flask import Blueprint, render_template, request, flash, jsonify
from re import fullmatch
from .models import Projects, Hours, User, Vacation
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
import json
from .forms import DatePicker, VacationLength, VacationDay
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
    dayId = day['dayId']
    day = Vacation.query.get(dayId)
    if day:
        db.session.delete(day)
        db.session.commit()
        flash('Day deleted!', category='success')
    return jsonify({})


@views.route('/overtime')
@login_required
def overtime():
    return render_template('overtime.html', user=current_user)