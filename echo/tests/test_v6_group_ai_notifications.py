from app import db
from app.models import User, ChatGroup, GroupMember, GroupMessage, Notification
from tests.conftest import login

def test_create_group(client, app, user):
    with app.app_context():
        other = User(username="groupfriend", email="groupfriend@example.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()
        other_id = other.id

    login(client)
    response = client.post(
        "/groups/new",
        data={"name": "Test Group", "member_ids": [str(other_id)]},
        follow_redirects=True
    )
    assert response.status_code == 200

    with app.app_context():
        assert ChatGroup.query.count() == 1
        assert GroupMember.query.count() == 2
        assert Notification.query.count() >= 1

def test_group_message_api(client, app, user):
    with app.app_context():
        group = ChatGroup(name="API Group", owner_id=user)
        db.session.add(group)
        db.session.flush()
        db.session.add(GroupMember(group_id=group.id, user_id=user, role="owner"))
        db.session.commit()
        group_id = group.id

    login(client)
    response = client.post(f"/api/group/{group_id}", json={"content": "hello group"})
    assert response.status_code == 200
    assert response.json["ok"] is True

    response = client.get(f"/api/group/{group_id}")
    assert response.status_code == 200
    assert len(response.json["messages"]) == 1

def test_ai_chat_fallback(client, user):
    login(client)
    response = client.post("/api/ai/chat", json={"message": "How do I play?"})
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert "reply" in response.json

def test_notifications_api(client, user):
    login(client)
    response = client.get("/api/notifications")
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert "chat_unread" in response.json
