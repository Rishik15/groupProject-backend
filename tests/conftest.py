import pytest
from unittest.mock import patch
from app.main import create_app


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    flask_app.config["WTF_CSRF_ENABLED"] = False
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    #Logged in as Alex user_id=2, role=client
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["role"] = "client"
    return client


@pytest.fixture
def coach_client(client):
    #Logged in as Sam user_id=3, role=coach
    with client.session_transaction() as sess:
        sess["user_id"] = 3
        sess["role"] = "coach"
    return client


@pytest.fixture
def admin_client(client):
    #Logged in as Liam user_id=12, role=admin
    with client.session_transaction() as sess:
        sess["user_id"] = 12
        sess["role"] = "admin"
    return client


@pytest.fixture
def mock_run_query():
    #fakes run querys results -  no real DB calls ever happen
    with patch("app.services.run_query") as mock:
        yield mock