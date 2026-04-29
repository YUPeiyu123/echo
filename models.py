from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    """Application user account."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    results = db.relationship(
        "GameResult",
        backref="player",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes_received = db.relationship(
        "PlayerLike",
        foreign_keys="PlayerLike.receiver_id",
        backref="receiver",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes_given = db.relationship(
        "PlayerLike",
        foreign_keys="PlayerLike.giver_id",
        backref="giver",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def win_count(self):
        return GameResult.query.filter_by(user_id=self.id, result="win").count()

    def loss_count(self):
        return GameResult.query.filter_by(user_id=self.id, result="loss").count()

    def best_result(self):
        return (
            GameResult.query
            .filter_by(user_id=self.id, result="win")
            .order_by(GameResult.score.desc(), GameResult.time_seconds.asc())
            .first()
        )

    def total_likes(self):
        return PlayerLike.query.filter_by(receiver_id=self.id).count()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class GameResult(db.Model):
    """Saved game attempt."""

    __tablename__ = "game_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False, index=True)
    result = db.Column(db.String(12), nullable=False, index=True)  # win / loss
    time_seconds = db.Column(db.Float, nullable=False, default=0)
    echo_count = db.Column(db.Integer, nullable=False, default=0)
    death_count = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def calculate_score(self):
        if self.result != "win":
            return 0
        base = 12000
        level_bonus = max(0, self.level) * 850
        time_penalty = int(max(0, self.time_seconds) * 23)
        echo_penalty = max(0, self.echo_count) * 75
        death_penalty = max(0, self.death_count) * 350
        return max(100, base + level_bonus - time_penalty - echo_penalty - death_penalty)

class PlayerLike(db.Model):
    """A lightweight social interaction between users."""

    __tablename__ = "player_likes"

    id = db.Column(db.Integer, primary_key=True)
    giver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        db.UniqueConstraint("giver_id", "receiver_id", name="unique_player_like"),
    )
