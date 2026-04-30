from app import db
from app.models import User
from tests.conftest import login

def test_leaderboard_page_loads(client):
    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert b"Leaderboard" in response.data

def test_profile_page_shows_player(client, user):
    response = client.get("/profile/tester")
    assert response.status_code == 200
    assert b"tester" in response.data

def test_like_other_player(client, app, user):
    with app.app_context():
        other = User(username="other", email="other@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

    login(client)
    response = client.post("/profile/other/like", follow_redirects=True)
    assert response.status_code == 200
    assert b"Player liked" in response.data

def test_cannot_like_self(client, user):
    login(client)
    response = client.post("/profile/tester/like", follow_redirects=True)
    assert response.status_code == 200
    assert b"cannot like your own profile" in response.data
