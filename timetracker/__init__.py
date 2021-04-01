from flask import Flask
from config import Config, DB_NAME
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_user import UserManager


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Projects, Hours, User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    user_manager = UserManager(app, db, User)
    user_manager.login_manager = login


    return app


def create_database(app):
    if not path.exists('timetracker/' + DB_NAME):
        db.create_all(app=app)
        print('Database has been created!')