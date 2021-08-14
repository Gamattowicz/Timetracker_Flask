from flask import Blueprint, render_template
from flask_login import login_required, current_user


views = Blueprint("views", __name__)


@views.route("/", methods=["GET"])
def home():
    return render_template("home.html", user=current_user)


@views.route("/timer", methods=["GET"])
@login_required
def timer():
    return render_template("timer.html", user=current_user)
