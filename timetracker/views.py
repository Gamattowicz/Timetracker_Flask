from flask import Blueprint, render_template

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html')


@views.route('/hours')
def hours():
    return render_template('hours.html')


@views.route('/projects')
def projects():
    return render_template('projects.html')