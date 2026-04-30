from app.models import GameResult
from tests.conftest import login

def test_game_page_requires_login(client):
    response = client.get("/game")
    assert response.status_code == 302

def test_api_saves_win_result(client, app, user):
    login(client)
    response = client.post(
        "/api/results",
        json={
            "level": 2,
            "result": "win",
            "time_seconds": 30.5,
            "echo_count": 5,
            "death_count": 0
        }
    )
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert response.json["score"] > 0

    with app.app_context():
        result = GameResult.query.first()
        assert result is not None
        assert result.level == 2
        assert result.result == "win"

def test_api_rejects_bad_result(client, user):
    login(client)
    response = client.post("/api/results", json={"level": 1, "result": "bad"})
    assert response.status_code == 400

def test_api_rejects_impossible_time(client, user):
    login(client)
    response = client.post("/api/results", json={
        "level": 1,
        "result": "win",
        "time_seconds": 0.1,
        "echo_count": 1,
        "death_count": 0
    })
    assert response.status_code == 400

def test_summary_api_requires_login(client):
    response = client.get("/api/me/summary")
    assert response.status_code == 302
