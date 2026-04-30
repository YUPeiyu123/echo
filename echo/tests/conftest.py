import pytest

from app import create_app, db
from app.models import User

@pytest.fixture()
def app():
    app = create_app("config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def user(app):
    with app.app_context():
        u = User(username="tester", email="tester@example.com")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        return u.id

def login(client, email="tester@example.com", password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True
    )
