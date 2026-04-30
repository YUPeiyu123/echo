from app.models import User, GameResult

def test_password_hashing(app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
        user.set_password("secret123")
        assert user.password_hash != "secret123"
        assert user.check_password("secret123")
        assert not user.check_password("wrong")

def test_game_result_score_for_win(app):
    with app.app_context():
        result = GameResult(level=3, result="win", time_seconds=40.0, echo_count=4, death_count=0)
        score = result.calculate_score()
        assert score > 0

def test_game_result_score_for_loss(app):
    with app.app_context():
        result = GameResult(level=3, result="loss", time_seconds=40.0, echo_count=4, death_count=1)
        assert result.calculate_score() == 0
