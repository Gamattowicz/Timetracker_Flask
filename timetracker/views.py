from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Vacation
from . import db
from flask_login import login_required, current_user
from .forms import VacationLengthForm, VacationDayForm
from math import ceil
from datetime import date, datetime, timedelta


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)


@views.route('/vacation-calculation', methods=['GET', 'POST'])
@login_required
def vacation_calculation():
    form = VacationLengthForm()
    school_years = {
        'Basic vocational school': 3,
        'High vocational school': 5,
        'High school': 4,
        'Post-high school': 6,
        'Bachelor/Masters degree': 8
    }
    job_position = {
        'Full-time': 1,
        'Half-time': 0.5,
        '1/3 time': (1/3),
        '2/3 time': (2/3),
        '1/4 time': 0.25,
        '3/4 time': 0.75
    }
    worker = User.query.filter_by(id=current_user.id).first()
    days = Vacation.query.filter_by(user_id=current_user.id)
    used_days = days.count()
    worker.rem_vacation_days = worker.total_vacation_days - used_days
    if request.method == 'POST':
        if not form.seniority.data:
            flash('Seniority must be complete!', category='error')
        else:
            seniority = form.seniority.data
            school = form.school.data
            position = form.position.data
            vacation_days = int(seniority) + school_years[school]
            if form.disability.data:
                if vacation_days > 10:
                    total_vacation_days = ceil(36 * job_position[position])
                else:
                    total_vacation_days = ceil(30 * job_position[position])
            else:
                if vacation_days > 10:
                    total_vacation_days = ceil(26 * job_position[position])
                else:
                    total_vacation_days = ceil(20 * job_position[position])
            worker.total_vacation_days = total_vacation_days
            db.session.commit()
            return redirect(url_for('views.vacation_calculation'))

    return render_template('vacation_calculation.html', user=current_user, form=form,
                           total_vacation_days=worker.total_vacation_days,
                           remaining_vacation_days=worker.rem_vacation_days)


@views.route('/vacation', methods=['GET', 'POST'])
@login_required
def vacation():
    form = VacationDayForm()
    worker = User.query.filter_by(id=current_user.id).first()
    days = Vacation.query.filter_by(user_id=current_user.id)
    used_days = days.count()
    worker.rem_vacation_days = worker.total_vacation_days - used_days
    if request.method == 'POST':
        if request.form.get('vacation_start_date') and request.form.get('vacation_end_date'):
            end_date = datetime.strptime(request.form.get('vacation_end_date'), '%Y-%m-%d').date()
            vacation_date = datetime.strptime(request.form.get('vacation_start_date'), '%Y-%m-%d').date() - timedelta(days=1)
            vacation_length = (end_date - vacation_date).days
            if vacation_length < 0:
                flash(f'Incorrect vacation dates!', category='error')
                return redirect(url_for('views.vacation'))
            for day in range(vacation_length):
                vacation_date += timedelta(days=1)
                if Vacation.query.filter_by(user_id=current_user.id, vacation_date=vacation_date).first():
                    flash(f'Vacation day with date {vacation_date} already exist!',
                          category='error')
                    return redirect(url_for('views.vacation'))
                elif worker.rem_vacation_days < vacation_length:
                    flash(f'You do not have enough vacation days in this year.', category='error')
                    return redirect(url_for('views.vacation'))
                new_vacation_day = Vacation(vacation_date=vacation_date, user_id=current_user.id)
                db.session.add(new_vacation_day)
        else:
            if Vacation.query.filter_by(user_id=current_user.id, vacation_date=date.today()).first():
                flash(f'Vacation day with date {date.today()} already exist!',
                      category='error')
                return redirect(url_for('views.vacation'))
            else:
                new_vacation_day = Vacation(user_id=current_user.id)
                db.session.add(new_vacation_day)
        db.session.commit()
        flash('Vacation day have been added!', category='success')
        return redirect(url_for('views.vacation_list'))

    return render_template('vacation.html', user=current_user, form=form)


@views.route('/vacation-list', methods=['GET'])
@login_required
def vacation_list():
    days = Vacation.query.filter_by(user_id=current_user.id)
    return render_template('vacation_list.html', days=days, user=current_user)


@views.route('/update-vacation/<vacation_day_id>', methods=['GET', 'POST'])
@login_required
def update_vacation_day(vacation_day_id):
    vacation = Vacation.query.get_or_404(vacation_day_id)
    form = VacationDayForm()
    if request.method == 'POST':
        if Vacation.query.filter_by(user_id=current_user.id, vacation_date=request.form.get('vacation_end_date')).first():
            flash(f'Vacation day with date {request.form.get("vacation_end_date")} already exist!',
                  category='error')
            return redirect(url_for('views.update_vacation_day'))
        else:
            vacation.vacation_date = request.form.get('vacation_end_date')
            db.session.commit()
            flash('Vacation day have been updated!', category='success')
            return redirect(url_for('views.vacation_list'))
    elif request.method == 'GET':
        form.vacation_end_date.data = datetime.strptime(vacation.vacation_date, '%Y-%m-%d').date()
    return render_template('vacation_update.html', user=current_user, form=form, date=datetime.strptime(vacation.vacation_date, '%Y-%m-%d').date())


@views.route('/delete-vacation-day/<vacation_day_id>', methods=['GET', 'POST'])
@login_required
def delete_vacation_day(vacation_day_id):
    vacation_day = Vacation.query.get_or_404(vacation_day_id)
    if request.method == 'POST':
        db.session.delete(vacation_day)
        db.session.commit()
        flash('Vacation day deleted!', category='success')
        return redirect(url_for('views.vacation'))
    return render_template('vacation_delete.html', user=current_user, vacation_day=vacation_day)