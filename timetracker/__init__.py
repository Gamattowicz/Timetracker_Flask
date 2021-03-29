from flask import Flask
from config import Config, DB_NAME
from flask_sqlalchemy import SQLAlchemy
from os import path


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app


def create_database(app):
    if not path.exists('timetracker/' + DB_NAME):
        db.create_all(app=app)
        print('Database has been created!')