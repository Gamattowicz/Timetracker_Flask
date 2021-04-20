from timetracker.models import User
import pytest


def test_registration(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/sign-up").status_code == 200

    # test that successful registration redirects to the home page
    response = client.post("/sign-up", data={"username": "test1",
                                             "password": "12345678",
                                             "confirm": "12345678"})
    assert response.headers["Location"] == "http://localhost/"
    assert response.status_code == 302
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    # test that the user was inserted into the database
    with app.app_context():
        assert (User.query.filter_by(username="test1").first()
                is not None)


@pytest.mark.parametrize(
    'data',
    [
        ({'username': 'test', 'password': '12345678', 'confirm':
            '12345667'}),  # not match confirm password
        ({'username': 'test', 'password': '1234', 'confirm':
            '1234'}),  # too short password
        ({'username': 't', 'password': '12345678', 'confirm':
            '12345678'}),  # too short username
    ]
)
def test_registration_invalid_data(client, data, app):
    # test that viewing the page renders without template errors
    assert client.get("/sign-up").status_code == 200

    # test that registration not redirects to the home page
    response = client.post("/sign-up", data=data)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    # test that the user was not inserted into the database
    with app.app_context():
        assert (User.query.filter_by(username=data['username']).first() is None)


def test_registration_already_used_username(client, user, app):
    # test that viewing the page renders without template errors
    assert client.get("/sign-up").status_code == 200

    # test that registration not redirects to the home page
    response = client.post("/sign-up", data={"username": user['username'],
                                             "password": "12345678",
                                             "confirm": "12345678"})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    # test that the user is in the database
    with app.app_context():
        assert (User.query.filter_by(username=user['username']).first()
                is not None)