from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


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
            flash('User has been created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('sign_up.html')


@auth.route('logout')
def logout():
    pass