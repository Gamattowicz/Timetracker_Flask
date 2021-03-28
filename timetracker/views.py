from flask import Blueprint, render_template, request, flash
import sqlite3
from re import fullmatch

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print('<h1> Good </h1>')
    return render_template('home.html')


@views.route('/hours', methods=['GET', 'POST'])
def hours():
    connection = sqlite3.connect(r'timetracker\time_tracker.db')
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

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
                    cur.execute('INSERT INTO hours (amount, work_date, '
                                'project_shortcut) VALUES (?, ?, ?)', [amount,
                                                                   work_date, project_shortcut])
                    flash('Hours have been added!', category='success')
                else:
                    flash('Format of date is incorrect. Must be YYYY-MM-DD',
                          category='error')
            else:
                cur.execute('INSERT INTO hours (amount, project_shortcut) VALUES (?, ?)',
                            [amount, project_shortcut])
                flash('Hours have been added!', category='success')

    c = cur.execute('select * from hours order by work_date desc')
    results = c.fetchall()
    p = cur.execute('select * from projects')
    projects = p.fetchall()
    connection.commit()
    connection.close()

    return render_template('hours.html', results=results, projects=projects)


@views.route('/projects', methods=['GET', 'POST'])
def projects():
    connection = sqlite3.connect(r'timetracker\time_tracker.db')
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        shortcut = request.form['shortcut']

        cur.execute('INSERT INTO projects (name, shortcut) VALUES (?, ?)', \
                    [name, shortcut])

    c = cur.execute('SELECT p.id, p.name, p.shortcut, SUM(h.amount) as sum '
                    'FROM projects p '
                    'JOIN hours h ON p.shortcut = h.project_shortcut '
                    'GROUP BY p.id ')
    results = c.fetchall()
    connection.commit()
    connection.close()

    return render_template('projects.html', results=results)