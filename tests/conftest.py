import pytest

from timetracker import create_app, db


@pytest.fixture()
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()

    yield app

    app.config['DB_FILE_PATH'].unlink(missing_ok=True)


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def user(client):
    user = {
        "username": "test542",
        "password": "12345678",
        "confirm": "12345678"
    }
    client.post('/sign-up', data=user)

    return user