from flask import Flask
from config import config, DB_NAME
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)

    from timetracker.views import views
    from timetracker.users.auth import auth
    from timetracker.hours.views import hours
    from timetracker.projects.views import projects
    from timetracker.vacation.views import vacation

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(hours, url_prefix="/hour")
    app.register_blueprint(projects, url_prefix="/project")
    app.register_blueprint(vacation, url_prefix="/vacation")

    from timetracker.users.models import User
    from timetracker.hours.models import Hour
    from timetracker.projects.models import Project
    from timetracker.vacation.models import Vacation

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("timetracker/" + DB_NAME):
        db.create_all(app=app)
        print("Database has been created!")
