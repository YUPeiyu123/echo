from app.models import User

def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create account" in response.data

def test_user_can_register(client, app):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="new@example.com").first() is not None

def test_user_can_login_and_logout(client, user):
    login_response = client.post(
        "/login",
        data={"email": "tester@example.com", "password": "password123"},
        follow_redirects=True
    )
    assert b"Welcome back" in login_response.data

    logout_response = client.get("/logout", follow_redirects=True)
    assert b"You have logged out" in logout_response.data
