from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.forms import RegisterForm, LoginForm
from app.models import User, GameResult, PlayerLike

main = Blueprint("main", __name__)

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
    if current_user.is_authenticated:
        liked_by_current_user = (
            PlayerLike.query
            .filter_by(giver_id=current_user.id, receiver_id=user.id)
            .first()
            is not None
        )

    return render_template(
        "profile.html",
        user=user,
        best=best,
        recent=recent,
        best_by_level=best_by_level,
        liked_by_current_user=liked_by_current_user
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
