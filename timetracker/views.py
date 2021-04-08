from flask import Blueprint, render_template, request, flash, jsonify
from re import fullmatch
from .models import Projects, Hours
from . import db
from sqlalchemy.sql import func
from flask_login import login_required, current_user
import json
from .forms import DatePicker


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


@views.route('/vacation')
@login_required
def vacation():
    return render_template('vacation.html', user=current_user)


@views.route('/overtime')
@login_required
def overtime():
    return render_template('overtime.html', user=current_user)