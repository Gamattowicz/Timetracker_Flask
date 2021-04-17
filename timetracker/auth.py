from flask import Blueprint, render_template, request, flash, redirect, \
    url_for, g
from .models import User
from . import db
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegisterForm, LoginForm


auth = Blueprint('auth', __name__)


@auth.before_request
def before_request():
    g.user = current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            redirect_url = request.args.get('next') or url_for('views.home')
            return redirect(redirect_url)
    return render_template('login.html', form=form, user=current_user)


@auth.route('sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('views.home'))
    return render_template('sign_up.html', form=form, user=current_user)


@auth.route('logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', category='success')
    return redirect(url_for('auth.login'))