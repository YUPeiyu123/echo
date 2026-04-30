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
    last_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

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
    last_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

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
    last_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        db.UniqueConstraint("giver_id", "receiver_id", name="unique_player_like"),
    )


class SocialPost(db.Model):
    """A public social post shown in the community feed."""

    __tablename__ = "social_posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    author = db.relationship("User", backref=db.backref("social_posts", lazy=True, cascade="all, delete-orphan"))

    def like_count(self):
        return PostLike.query.filter_by(post_id=self.id).count()

    def comment_count(self):
        return PostComment.query.filter_by(post_id=self.id).count()

class PostComment(db.Model):
    """A comment under a social post."""

    __tablename__ = "post_comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("social_posts.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    post = db.relationship("SocialPost", backref=db.backref("comments", lazy=True, cascade="all, delete-orphan"))
    author = db.relationship("User", backref=db.backref("post_comments", lazy=True, cascade="all, delete-orphan"))

class PostLike(db.Model):
    """A like on a social post."""

    __tablename__ = "post_likes"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("social_posts.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    post = db.relationship("SocialPost", backref=db.backref("likes", lazy=True, cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("post_likes", lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("post_id", "user_id", name="unique_post_like"),
    )

class Follow(db.Model):
    """A follow relationship between two users."""

    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    follower = db.relationship("User", foreign_keys=[follower_id], backref=db.backref("following_rows", lazy=True, cascade="all, delete-orphan"))
    followed = db.relationship("User", foreign_keys=[followed_id], backref=db.backref("follower_rows", lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("follower_id", "followed_id", name="unique_follow"),
    )

class ChatMessage(db.Model):
    """A private message between two users."""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    sender = db.relationship("User", foreign_keys=[sender_id], backref=db.backref("sent_messages", lazy=True, cascade="all, delete-orphan"))
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref=db.backref("received_messages", lazy=True, cascade="all, delete-orphan"))


class ChatGroup(db.Model):
    """A group chat room created by users."""

    __tablename__ = "chat_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    owner = db.relationship("User", backref=db.backref("owned_chat_groups", lazy=True, cascade="all, delete-orphan"))

class GroupMember(db.Model):
    """Membership of a user in a group chat."""

    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("chat_groups.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(20), default="member", nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    group = db.relationship("ChatGroup", backref=db.backref("members", lazy=True, cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("group_memberships", lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("group_id", "user_id", name="unique_group_member"),
    )

class GroupMessage(db.Model):
    """A message sent inside a group chat."""

    __tablename__ = "group_messages"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("chat_groups.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    group = db.relationship("ChatGroup", backref=db.backref("messages", lazy=True, cascade="all, delete-orphan"))
    sender = db.relationship("User", backref=db.backref("group_messages", lazy=True, cascade="all, delete-orphan"))

class GroupReadState(db.Model):
    """Tracks the last time a user read a group chat."""

    __tablename__ = "group_read_states"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("chat_groups.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    last_read_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    group = db.relationship("ChatGroup", backref=db.backref("read_states", lazy=True, cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("group_read_states", lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.UniqueConstraint("group_id", "user_id", name="unique_group_read_state"),
    )

class Notification(db.Model):
    """A notification for social interaction, comments, likes, follows and chat events."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    type = db.Column(db.String(40), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(300), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User", foreign_keys=[user_id], backref=db.backref("notifications", lazy=True, cascade="all, delete-orphan"))
    actor = db.relationship("User", foreign_keys=[actor_id])
