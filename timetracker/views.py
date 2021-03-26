from flask import Blueprint, render_template, request

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
        return f'<h1> Name: {request.form["project"]} </h1>'
    return render_template('projects.html')