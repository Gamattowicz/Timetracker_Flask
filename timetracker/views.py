from flask import Blueprint, render_template, request
import sqlite3

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print('<h1> Good </h1>')
    return render_template('home.html')


@views.route('/hours')
def hours():
    return render_template('hours.html')


@views.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        name = request.form['name']
        shortcut = request.form['shortcut']

        connection = sqlite3.connect(r'timetracker\time_tracker.db')
        cur = connection.cursor()
        cur.execute('INSERT INTO projects (name, shortcut) VALUES (?, ?)', \
                    [name, shortcut])
        connection.commit()
        connection.close()

    return render_template('projects.html')