from app import create_app, db
from app.models import User, GameResult, PlayerLike, SocialPost, PostComment, PostLike, Follow, ChatMessage, ChatGroup, GroupMember, GroupMessage, GroupReadState, Notification

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "GameResult": GameResult,
        "PlayerLike": PlayerLike,
    }

if __name__ == "__main__":
    app.run(debug=True)
