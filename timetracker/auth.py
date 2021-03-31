from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user


auth = Blueprint('auth', __name__)


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
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('User with that username does not exist!', category='error')

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
def logout():
    pass