from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_, and_

from app import db
from app.forms import RegisterForm, LoginForm
from app.models import User, GameResult, PlayerLike, SocialPost, PostComment, PostLike, Follow, ChatMessage, ChatGroup, GroupMember, GroupMessage, GroupReadState, Notification

main = Blueprint("main", __name__)

def create_notification(user_id, type_name, title, body, link=None, actor_id=None):
    """Create a notification unless the receiver is the actor."""
    if actor_id is not None and user_id == actor_id:
        return None

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=type_name,
        title=title[:120],
        body=body[:300],
        link=link
    )
    db.session.add(notification)
    return notification

def is_group_member(group_id, user_id):
    return GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first() is not None

def get_direct_unread_count(user_id):
    return ChatMessage.query.filter_by(receiver_id=user_id, is_read=False).count()

def get_group_unread_count(user_id):
    memberships = GroupMember.query.filter_by(user_id=user_id).all()
    total = 0
    for membership in memberships:
        read_state = GroupReadState.query.filter_by(
            group_id=membership.group_id,
            user_id=user_id
        ).first()
        if read_state:
            total += GroupMessage.query.filter(
                GroupMessage.group_id == membership.group_id,
                GroupMessage.sender_id != user_id,
                GroupMessage.created_at > read_state.last_read_at
            ).count()
        else:
            total += GroupMessage.query.filter(
                GroupMessage.group_id == membership.group_id,
                GroupMessage.sender_id != user_id
            ).count()
    return total

def get_total_unread_count(user_id):
    return get_direct_unread_count(user_id) + get_group_unread_count(user_id)


MAX_LEVEL = 12

@main.route("/")
def index():
    recent_results = (
        GameResult.query
        .filter_by(result="win")
        .order_by(GameResult.created_at.desc())
        .limit(6)
        .all()
    )
    total_players = User.query.count()
    total_attempts = GameResult.query.count()
    total_clears = GameResult.query.filter_by(result="win").count()
    return render_template(
        "index.html",
        recent_results=recent_results,
        total_players=total_players,
        total_attempts=total_attempts,
        total_clears=total_clears
    )

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.game"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.game"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        login_user(user, remember=form.remember_me.data)
        flash("Welcome back, " + user.username + "!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.game"))

    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for("main.index"))

@main.route("/game")
@login_required
def game():
    return render_template("game.html")

@main.route("/history")
@login_required
def history():
    results = (
        GameResult.query
        .filter_by(user_id=current_user.id)
        .order_by(GameResult.created_at.desc())
        .limit(80)
        .all()
    )
    return render_template("history.html", results=results)

@main.route("/leaderboard")
def leaderboard():
    wins = (
        GameResult.query
        .filter_by(result="win")
        .order_by(GameResult.score.desc(), GameResult.time_seconds.asc())
        .all()
    )

    best_by_user = {}
    for result in wins:
        if result.user_id not in best_by_user:
            best_by_user[result.user_id] = result

    leaderboard_rows = list(best_by_user.values())[:25]
    return render_template("leaderboard.html", results=leaderboard_rows)

@main.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    best = user.best_result()
    recent = (
        GameResult.query
        .filter_by(user_id=user.id)
        .order_by(GameResult.created_at.desc())
        .limit(12)
        .all()
    )

    best_by_level = {}
    for result in (
        GameResult.query
        .filter_by(user_id=user.id, result="win")
        .order_by(GameResult.level.asc(), GameResult.score.desc())
        .all()
    ):
        if result.level not in best_by_level:
            best_by_level[result.level] = result

    liked_by_current_user = False
    is_following = False
    if current_user.is_authenticated:
        liked_by_current_user = (
            PlayerLike.query
            .filter_by(giver_id=current_user.id, receiver_id=user.id)
            .first()
            is not None
        )
        is_following = (
            Follow.query
            .filter_by(follower_id=current_user.id, followed_id=user.id)
            .first()
            is not None
        )

    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return render_template(
        "profile.html",
        user=user,
        best=best,
        recent=recent,
        best_by_level=best_by_level,
        liked_by_current_user=liked_by_current_user,
        is_following=is_following,
        followers_count=followers_count,
        following_count=following_count
    )

@main.route("/profile/<username>/like", methods=["POST"])
@login_required
def like_profile(username):
    receiver = User.query.filter_by(username=username).first_or_404()
    if receiver.id == current_user.id:
        flash("You cannot like your own profile.", "warning")
        return redirect(url_for("main.profile", username=username))

    existing = PlayerLike.query.filter_by(
        giver_id=current_user.id,
        receiver_id=receiver.id
    ).first()

    if existing:
        db.session.delete(existing)
        flash("Like removed.", "info")
    else:
        db.session.add(PlayerLike(giver_id=current_user.id, receiver_id=receiver.id))
        flash("Player liked.", "success")

    db.session.commit()
    return redirect(url_for("main.profile", username=username))

@main.route("/api/results", methods=["POST"])
@login_required
def save_result():
    data = request.get_json(silent=True) or {}

    try:
        level = int(data.get("level", 1))
        result_value = str(data.get("result", "")).lower()
        time_seconds = float(data.get("time_seconds", 0))
        echo_count = int(data.get("echo_count", 0))
        death_count = int(data.get("death_count", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid result payload."}), 400

    if result_value not in {"win", "loss"}:
        return jsonify({"ok": False, "error": "Result must be win or loss."}), 400

    if level < 1 or level > MAX_LEVEL:
        return jsonify({"ok": False, "error": "Level out of range."}), 400

    # Basic anti-cheat style sanity checks.
    if time_seconds < 1.0 or time_seconds > 3600:
        return jsonify({"ok": False, "error": "Invalid time value."}), 400

    if echo_count < 0 or echo_count > 999:
        return jsonify({"ok": False, "error": "Invalid echo count."}), 400

    game_result = GameResult(
        user_id=current_user.id,
        level=level,
        result=result_value,
        time_seconds=max(0, time_seconds),
        echo_count=max(0, echo_count),
        death_count=max(0, death_count)
    )
    game_result.score = game_result.calculate_score()

    db.session.add(game_result)
    db.session.commit()

    return jsonify({
        "ok": True,
        "score": game_result.score,
        "result_id": game_result.id,
        "message": "Result saved"
    })

@main.route("/api/me/summary")
@login_required
def my_summary():
    best = current_user.best_result()
    wins = current_user.win_count()
    losses = current_user.loss_count()

    best_by_level = {}
    level_results = (
        GameResult.query
        .filter_by(user_id=current_user.id, result="win")
        .order_by(GameResult.level.asc(), GameResult.score.desc())
        .all()
    )
    for result in level_results:
        if result.level not in best_by_level:
            best_by_level[result.level] = {
                "score": result.score,
                "time_seconds": result.time_seconds,
                "echo_count": result.echo_count
            }

    return jsonify({
        "ok": True,
        "username": current_user.username,
        "wins": wins,
        "losses": losses,
        "best_score": best.score if best else None,
        "best_by_level": best_by_level
    })


@main.route("/social")
def social():
    feed_type = request.args.get("feed", "all")
    query = SocialPost.query.order_by(SocialPost.created_at.desc())

    if current_user.is_authenticated and feed_type == "following":
        followed_ids = [
            row.followed_id for row in Follow.query.filter_by(follower_id=current_user.id).all()
        ]
        followed_ids.append(current_user.id)
        query = (
            SocialPost.query
            .filter(SocialPost.author_id.in_(followed_ids))
            .order_by(SocialPost.created_at.desc())
        )

    posts = query.limit(50).all()

    online_cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    online_users = (
        User.query
        .filter(User.last_seen_at >= online_cutoff)
        .order_by(User.last_seen_at.desc())
        .limit(12)
        .all()
    )

    suggested_users = []
    if current_user.is_authenticated:
        following_ids = {row.followed_id for row in Follow.query.filter_by(follower_id=current_user.id).all()}
        suggested_query = User.query.filter(User.id != current_user.id)
        if following_ids:
            suggested_query = suggested_query.filter(~User.id.in_(following_ids))
        suggested_users = suggested_query.order_by(User.created_at.desc()).limit(8).all()

    return render_template(
        "social.html",
        posts=posts,
        feed_type=feed_type,
        online_users=online_users,
        suggested_users=suggested_users,
    )

@main.route("/social/post", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content", "").strip()
    if not content:
        flash("Post content cannot be empty.", "warning")
        return redirect(url_for("main.social"))
    if len(content) > 800:
        flash("Post is too long. Please keep it under 800 characters.", "warning")
        return redirect(url_for("main.social"))

    db.session.add(SocialPost(author_id=current_user.id, content=content))
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    flash("Post published.", "success")
    return redirect(url_for("main.social"))

@main.route("/social/post/<int:post_id>/comment", methods=["POST"])
@login_required
def create_comment(post_id):
    post = SocialPost.query.get_or_404(post_id)
    content = request.form.get("content", "").strip()
    if not content:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("main.social"))
    if len(content) > 500:
        flash("Comment is too long.", "warning")
        return redirect(url_for("main.social"))

    db.session.add(PostComment(post_id=post.id, author_id=current_user.id, content=content))
    create_notification(
        user_id=post.author_id,
        actor_id=current_user.id,
        type_name="comment",
        title="New comment",
        body=current_user.username + " commented on your post: " + content[:80],
        link=url_for("main.social") + f"#post-{post.id}"
    )
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    flash("Comment added.", "success")
    return redirect(url_for("main.social") + f"#post-{post.id}")

@main.route("/social/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    post = SocialPost.query.get_or_404(post_id)
    existing = PostLike.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    if existing:
        db.session.delete(existing)
        flash("Like removed.", "info")
    else:
        db.session.add(PostLike(post_id=post.id, user_id=current_user.id))
        create_notification(
            user_id=post.author_id,
            actor_id=current_user.id,
            type_name="post_like",
            title="New like",
            body=current_user.username + " liked your post.",
            link=url_for("main.social") + f"#post-{post.id}"
        )
        flash("Post liked.", "success")

    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    return redirect(url_for("main.social") + f"#post-{post.id}")

@main.route("/follow/<username>", methods=["POST"])
@login_required
def follow_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.id == current_user.id:
        flash("You cannot follow yourself.", "warning")
        return redirect(url_for("main.profile", username=username))

    existing = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()

    if existing:
        db.session.delete(existing)
        flash("Unfollowed " + user.username + ".", "info")
    else:
        db.session.add(Follow(follower_id=current_user.id, followed_id=user.id))
        create_notification(
            user_id=user.id,
            actor_id=current_user.id,
            type_name="follow",
            title="New follower",
            body=current_user.username + " followed you.",
            link=url_for("main.profile", username=current_user.username)
        )
        flash("Now following " + user.username + ".", "success")

    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    return redirect(request.referrer or url_for("main.social"))

@main.route("/chat")
@login_required
def chat_index():
    users = (
        User.query
        .filter(User.id != current_user.id)
        .order_by(User.last_seen_at.desc())
        .limit(30)
        .all()
    )

    groups = (
        ChatGroup.query
        .join(GroupMember)
        .filter(GroupMember.user_id == current_user.id)
        .order_by(ChatGroup.created_at.desc())
        .all()
    )

    direct_unread_by_user = {}
    for user in users:
        count = ChatMessage.query.filter_by(
            sender_id=user.id,
            receiver_id=current_user.id,
            is_read=False
        ).count()
        direct_unread_by_user[user.id] = count

    group_unread_by_group = {}
    for group in groups:
        read_state = GroupReadState.query.filter_by(
            group_id=group.id,
            user_id=current_user.id
        ).first()
        if read_state:
            count = GroupMessage.query.filter(
                GroupMessage.group_id == group.id,
                GroupMessage.sender_id != current_user.id,
                GroupMessage.created_at > read_state.last_read_at
            ).count()
        else:
            count = GroupMessage.query.filter(
                GroupMessage.group_id == group.id,
                GroupMessage.sender_id != current_user.id
            ).count()
        group_unread_by_group[group.id] = count

    return render_template(
        "chat_index.html",
        users=users,
        groups=groups,
        direct_unread_by_user=direct_unread_by_user,
        group_unread_by_group=group_unread_by_group
    )

@main.route("/chat/<username>")
@login_required
def chat_with(username):
    other = User.query.filter_by(username=username).first_or_404()
    if other.id == current_user.id:
        flash("You cannot chat with yourself.", "warning")
        return redirect(url_for("main.chat_index"))
    return render_template("chat.html", other=other)

@main.route("/api/chat/<username>", methods=["GET", "POST"])
@login_required
def api_chat(username):
    other = User.query.filter_by(username=username).first_or_404()
    if other.id == current_user.id:
        return jsonify({"ok": False, "error": "Cannot chat with yourself."}), 400

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        content = str(data.get("content", "")).strip()
        if not content:
            return jsonify({"ok": False, "error": "Message cannot be empty."}), 400
        if len(content) > 1000:
            return jsonify({"ok": False, "error": "Message is too long."}), 400

        msg = ChatMessage(sender_id=current_user.id, receiver_id=other.id, content=content)
        current_user.last_seen_at = datetime.now(timezone.utc)
        db.session.add(msg)
        create_notification(
            user_id=other.id,
            actor_id=current_user.id,
            type_name="direct_message",
            title="New message",
            body=current_user.username + ": " + content[:100],
            link=url_for("main.chat_with", username=current_user.username)
        )
        db.session.commit()
        return jsonify({"ok": True, "message_id": msg.id})

    messages = (
        ChatMessage.query
        .filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == other.id),
                and_(ChatMessage.sender_id == other.id, ChatMessage.receiver_id == current_user.id)
            )
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(80)
        .all()
    )

    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "ok": True,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "receiver": msg.receiver.username,
                "content": msg.content,
                "is_mine": msg.sender_id == current_user.id,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for msg in messages
        ]
    })

@main.route("/api/heartbeat", methods=["POST"])
@login_required
def heartbeat():
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"ok": True})

@main.route("/api/online")
def api_online():
    online_cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    users = (
        User.query
        .filter(User.last_seen_at >= online_cutoff)
        .order_by(User.last_seen_at.desc())
        .limit(20)
        .all()
    )
    return jsonify({
        "ok": True,
        "users": [
            {
                "username": user.username,
                "last_seen_at": user.last_seen_at.strftime("%Y-%m-%d %H:%M:%S") if user.last_seen_at else None
            }
            for user in users
        ]
    })


@main.route("/groups/new", methods=["GET", "POST"])
@login_required
def create_group():
    search = request.args.get("q", "").strip()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        member_ids = request.form.getlist("member_ids")

        if not name:
            flash("Group name cannot be empty.", "warning")
            return redirect(url_for("main.create_group"))

        group = ChatGroup(name=name[:80], owner_id=current_user.id)
        db.session.add(group)
        db.session.flush()

        db.session.add(GroupMember(group_id=group.id, user_id=current_user.id, role="owner"))
        db.session.add(GroupReadState(group_id=group.id, user_id=current_user.id))

        added = set()
        for raw_id in member_ids:
            try:
                user_id = int(raw_id)
            except ValueError:
                continue
            if user_id == current_user.id or user_id in added:
                continue
            user = db.session.get(User, user_id)
            if not user:
                continue
            added.add(user_id)
            db.session.add(GroupMember(group_id=group.id, user_id=user.id, role="member"))
            db.session.add(GroupReadState(group_id=group.id, user_id=user.id))
            create_notification(
                user_id=user.id,
                actor_id=current_user.id,
                type_name="group_invite",
                title="Added to group",
                body=current_user.username + " added you to group: " + group.name,
                link=url_for("main.group_chat", group_id=group.id)
            )

        current_user.last_seen_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Group created.", "success")
        return redirect(url_for("main.group_chat", group_id=group.id))

    following_ids = [row.followed_id for row in Follow.query.filter_by(follower_id=current_user.id).all()]
    following_users = User.query.filter(User.id.in_(following_ids)).order_by(User.username.asc()).all() if following_ids else []

    all_query = User.query.filter(User.id != current_user.id)
    if search:
        all_query = all_query.filter(User.username.ilike(f"%{search}%"))
    all_users = all_query.order_by(User.username.asc()).limit(50).all()

    return render_template(
        "group_new.html",
        following_users=following_users,
        all_users=all_users,
        search=search
    )

@main.route("/groups/<int:group_id>")
@login_required
def group_chat(group_id):
    group = ChatGroup.query.get_or_404(group_id)
    if not is_group_member(group.id, current_user.id):
        flash("You are not a member of this group.", "danger")
        return redirect(url_for("main.chat_index"))

    members = (
        GroupMember.query
        .filter_by(group_id=group.id)
        .join(User)
        .order_by(User.username.asc())
        .all()
    )

    following_ids = [row.followed_id for row in Follow.query.filter_by(follower_id=current_user.id).all()]
    following_users = User.query.filter(User.id.in_(following_ids)).order_by(User.username.asc()).all() if following_ids else []

    return render_template(
        "group_chat.html",
        group=group,
        members=members,
        following_users=following_users
    )

@main.route("/groups/<int:group_id>/invite", methods=["POST"])
@login_required
def invite_group_members(group_id):
    group = ChatGroup.query.get_or_404(group_id)
    if not is_group_member(group.id, current_user.id):
        flash("You are not a member of this group.", "danger")
        return redirect(url_for("main.chat_index"))

    member_ids = request.form.getlist("member_ids")
    added_count = 0

    for raw_id in member_ids:
        try:
            user_id = int(raw_id)
        except ValueError:
            continue

        if user_id == current_user.id:
            continue

        user = db.session.get(User, user_id)
        if not user:
            continue

        existing = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
        if existing:
            continue

        db.session.add(GroupMember(group_id=group.id, user_id=user.id, role="member"))
        db.session.add(GroupReadState(group_id=group.id, user_id=user.id))
        create_notification(
            user_id=user.id,
            actor_id=current_user.id,
            type_name="group_invite",
            title="Group invitation",
            body=current_user.username + " invited you to group: " + group.name,
            link=url_for("main.group_chat", group_id=group.id)
        )
        added_count += 1

    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(str(added_count) + " member(s) added.", "success")
    return redirect(url_for("main.group_chat", group_id=group.id))

@main.route("/api/group/<int:group_id>", methods=["GET", "POST"])
@login_required
def api_group_chat(group_id):
    group = ChatGroup.query.get_or_404(group_id)
    if not is_group_member(group.id, current_user.id):
        return jsonify({"ok": False, "error": "Not a group member."}), 403

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        content = str(data.get("content", "")).strip()

        if not content:
            return jsonify({"ok": False, "error": "Message cannot be empty."}), 400
        if len(content) > 1000:
            return jsonify({"ok": False, "error": "Message is too long."}), 400

        msg = GroupMessage(group_id=group.id, sender_id=current_user.id, content=content)
        db.session.add(msg)

        read_state = GroupReadState.query.filter_by(group_id=group.id, user_id=current_user.id).first()
        if not read_state:
            read_state = GroupReadState(group_id=group.id, user_id=current_user.id)
            db.session.add(read_state)
        read_state.last_read_at = datetime.now(timezone.utc)

        members = GroupMember.query.filter_by(group_id=group.id).all()
        for member in members:
            if member.user_id != current_user.id:
                create_notification(
                    user_id=member.user_id,
                    actor_id=current_user.id,
                    type_name="group_message",
                    title="New group message",
                    body=group.name + " · " + current_user.username + ": " + content[:90],
                    link=url_for("main.group_chat", group_id=group.id)
                )

        current_user.last_seen_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"ok": True, "message_id": msg.id})

    messages = (
        GroupMessage.query
        .filter_by(group_id=group.id)
        .order_by(GroupMessage.created_at.asc())
        .limit(120)
        .all()
    )

    read_state = GroupReadState.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if not read_state:
        read_state = GroupReadState(group_id=group.id, user_id=current_user.id)
        db.session.add(read_state)
    read_state.last_read_at = datetime.now(timezone.utc)
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "ok": True,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "content": msg.content,
                "is_mine": msg.sender_id == current_user.id,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for msg in messages
        ]
    })

@main.route("/api/notifications")
@login_required
def api_notifications():
    notifications = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(15)
        .all()
    )

    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    direct_unread = get_direct_unread_count(current_user.id)
    group_unread = get_group_unread_count(current_user.id)
    total_chat_unread = direct_unread + group_unread

    return jsonify({
        "ok": True,
        "unread_notifications": unread_notifications,
        "direct_unread": direct_unread,
        "group_unread": group_unread,
        "chat_unread": total_chat_unread,
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "body": n.body,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for n in notifications
        ]
    })

@main.route("/api/notifications/read", methods=["POST"])
@login_required
def api_mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"ok": True})

@main.route("/api/users/search")
@login_required
def api_users_search():
    q = request.args.get("q", "").strip()
    query = User.query.filter(User.id != current_user.id)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    users = query.order_by(User.username.asc()).limit(30).all()
    return jsonify({
        "ok": True,
        "users": [
            {"id": user.id, "username": user.username}
            for user in users
        ]
    })

@main.route("/chat/ai")
@login_required
def ai_chat():
    return render_template("ai_chat.html")

@main.route("/api/ai/chat", methods=["POST"])
@login_required
def api_ai_chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"ok": False, "error": "Message cannot be empty."}), 400
    if len(message) > 1000:
        return jsonify({"ok": False, "error": "Message is too long."}), 400

    current_user.last_seen_at = datetime.now(timezone.utc)

    api_key = current_app.config.get("OPENAI_API_KEY", "")
    model = current_app.config.get("OPENAI_MODEL", "gpt-4.1-mini")

    # Safe fallback so the project still works during offline marking or without an API key.
    fallback_reply = (
        "I am the AI Game Assistant. My suggestion is: keep your message short, "
        "use soft probes near monsters, use strong probes only when you need map information, "
        "and check the community feed for other players' strategies."
    )

    if not api_key:
        db.session.commit()
        return jsonify({
            "ok": True,
            "reply": fallback_reply,
            "source": "local_fallback"
        })

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are AI Game Assistant inside a student web game. "
                        "Answer briefly, normally, and helpfully. "
                        "Do not roleplay as a romantic partner. "
                        "Keep answers under 80 words unless the user asks for detail."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        reply = getattr(response, "output_text", None) or fallback_reply
        db.session.commit()
        return jsonify({
            "ok": True,
            "reply": reply,
            "source": "openai"
        })
    except Exception as exc:
        db.session.commit()
        return jsonify({
            "ok": True,
            "reply": fallback_reply + " API note: " + str(exc)[:120],
            "source": "fallback_after_error"
        })
