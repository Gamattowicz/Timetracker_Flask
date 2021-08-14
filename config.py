import os
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
env_file = base_dir / ".env"
load_dotenv(env_file)
DB_NAME = "timetracker.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"


class TestingConfig(Config):
    DB_FILE_PATH = base_dir / "tests" / "tests.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE_PATH}"
    DEBUG = True
    TESTING = True


config = {"development": DevelopmentConfig, "testing": TestingConfig}
