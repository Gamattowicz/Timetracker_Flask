from flask import Blueprint, render_template, request, flash
import sqlite3
from re import fullmatch
from .models import Projects, Hours
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print('<h1> Good </h1>')
    return render_template('home.html')


@views.route('/hours', methods=['GET', 'POST'])
def hours():
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
            if request.form['work-date']:
                if fullmatch(r'20[0-2][0-9]-[0-1][0-9]-[0-3][0-9]',
                             request.form['work-date']):
                    work_date = request.form['work-date']
                    new_hours = Hours(amount=amount, work_date=work_date,
                                      project_shortcut=project_shortcut)
                    db.session.add(new_hours)
                    db.session.commit()
                    flash('Hours have been added!', category='success')
                else:
                    flash('Format of date is incorrect. Must be YYYY-MM-DD',
                          category='error')
            else:
                new_hours = Hours(amount=amount,
                                  project_shortcut=project_shortcut)
                db.session.add(new_hours)
                db.session.commit()
                flash('Hours have been added!', category='success')

    results = Hours.query.all()
    projects = Projects.query.all()

    return render_template('hours.html', results=results, projects=projects)


@views.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        r = cur.execute('SELECT name from projects WHERE name = ?',
                        (request.form["name"], ))
        n = cur.execute('SELECT shortcut from projects WHERE shortcut = ?',
                        (request.form["shortcut"], ))
        if r.fetchone():
            flash(f"Project with name {request.form['name']} already exist!",
                  category='error')
        elif n.fetchone():
            flash(f"Project with shortcut {request.form['shortcut']} already "
                  f"exist!", category='error')
        else:
            name = request.form['name']
            shortcut = request.form['shortcut']

            cur.execute('INSERT INTO projects (name, shortcut) VALUES (?, ?)',
                        [name, shortcut])
            flash('Project have been added!', category='success')

    c = cur.execute('''SELECT p.id, p.name, p.shortcut, IFNULL(SUM(
                    h.amount), 0) as sum
                    FROM projects p
                    LEFT JOIN hours h ON p.shortcut = h.project_shortcut
                    GROUP BY p.id ''')
    results = c.fetchall()
    connection.commit()

    return render_template('projects.html', results=results)