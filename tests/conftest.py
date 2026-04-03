import pytest

from app import app as flask_app
from utils.db import create_user, get_user_by_username, init_db

TEST_USER = "testuser"
TEST_PASSWORD = "testpass123456"


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(app):
    init_db()
    if not get_user_by_username(TEST_USER):
        create_user(TEST_USER, TEST_PASSWORD)
    c = app.test_client()
    c.post(
        "/login",
        data={"username": TEST_USER, "password": TEST_PASSWORD},
        follow_redirects=True,
    )
    return c
