from flask import Blueprint, render_template, request, flash, redirect, \
    url_for, session
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse, urljoin


auth = Blueprint('auth', __name__)


def is_safe_url(target):
    """
    Function that checks if the url address entered by the user if safe
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('You have logged in correctly', category='success')
                login_user(user, remember=True)
                if 'next' in session and session['next']:
                    if is_safe_url(session['next']):
                        return redirect(session['next'])
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('User with that username does not exist!', category='error')

    session['next'] = request.args.get('next')
    return render_template('login.html', user=current_user)


@auth.route('sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('User with that username already exists!', category='error')
        elif len(username) < 2:
            flash('Username is too short! Must be greater than 2 '
                  'characters', category='error')
        elif password1 != password2:
            flash('Passwords are not the same!', category='error')
        elif len(password1) < 5:
            flash('Password is too short! Must be greater than 4 '
                  'characters', category='error')
        else:
            new_user = User(username=username,
                            password=generate_password_hash(password1,
                                                            method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User has been created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)


@auth.route('logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='success')
    return redirect(url_for('auth.login'))