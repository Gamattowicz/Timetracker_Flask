from timetracker.models import User


def test_registration(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/sign-up").status_code == 200

    # test that successful registration redirects to the home page
    response = client.post("/sign-up", data={"username": "test1",
                                             "password": "12345678",
                                             "confirm": "12345678"})
    assert "http://localhost/" == response.headers["Location"]

    # test that the user was inserted into the database
    with app.app_context():
        assert (User.query.filter_by(username="test1").first()
                is not None
        )