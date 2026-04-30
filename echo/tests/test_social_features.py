from app import db
from app.models import User, SocialPost, PostComment, PostLike, Follow
from tests.conftest import login

def test_social_page_public(client):
    response = client.get("/social")
    assert response.status_code == 200
    assert b"Echo Circle" in response.data

def test_logged_in_user_can_create_post(client, app, user):
    login(client)
    response = client.post("/social/post", data={"content": "Hello community"}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert SocialPost.query.count() == 1

def test_comment_and_like_post(client, app, user):
    with app.app_context():
        post = SocialPost(author_id=user, content="Test post")
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    login(client)
    comment_response = client.post(f"/social/post/{post_id}/comment", data={"content": "Nice"}, follow_redirects=True)
    like_response = client.post(f"/social/post/{post_id}/like", follow_redirects=True)
    assert comment_response.status_code == 200
    assert like_response.status_code == 200

    with app.app_context():
        assert PostComment.query.count() == 1
        assert PostLike.query.count() == 1

def test_follow_other_user(client, app, user):
    with app.app_context():
        other = User(username="friend", email="friend@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

    login(client)
    response = client.post("/follow/friend", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert Follow.query.count() == 1

def test_chat_api(client, app, user):
    with app.app_context():
        other = User(username="chatfriend", email="chat@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

    login(client)
    response = client.post("/api/chat/chatfriend", json={"content": "hello"})
    assert response.status_code == 200
    assert response.json["ok"] is True

    response = client.get("/api/chat/chatfriend")
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert len(response.json["messages"]) == 1
