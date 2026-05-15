
# Echo Escape

Echo Escape is a Flask-based web game and social interaction platform.

The core gameplay is inspired by dark echo-location mechanics. Players explore a dark maze, send echo probes to reveal walls and traps, avoid monsters, and reach the exit.

Beyond the game itself, Echo Escape includes a complete social module. Players can create posts, comment, like, follow other players, chat privately, create group chats, receive notifications, and use an optional AI Game Assistant.

The final version focuses on connecting gameplay with social interaction:

```text
Play game → save result → view leaderboard → interact with players → chat / follow / join groups
```

---

## Key Features

### 1. Gameplay Features

- Dark maze exploration game built with JavaScript Canvas.
- Echo probe mechanic for revealing the hidden map.
- Walking probes, strong probes and soft probes.
- Monsters that can be woken by strong probes or close player movement.
- Monster pathfinding through corridors.
- 12 playable levels.
- Level selector and difficulty labels.
- Pause, restart and sound toggle controls.
- Automatic game result saving.
- Score calculation based on time, echo count, deaths and result.
- Low-spec visual mode for smoother performance.

---

### 2. User Account Features

- User registration.
- User login and logout.
- Password hashing using Werkzeug.
- Session management using Flask-Login.
- CSRF protection using Flask-WTF.
- Public player profile pages.
- Personal game history.
- Per-level progress display.
- Best score and recent result summary.

---

### 3. Leaderboard and Player Profiles

- Global leaderboard.
- Player ranking by score.
- Public profile pages.
- Player win/loss summary.
- Best result display.
- Recent game result display.
- Like player profile.
- Follow and unfollow players.
- Chat shortcut from player profile.

---

## Social Interaction Module

The social module was upgraded from a simple community feed into a game-connected community system.

Players can:

- Create community posts.
- View posts as a public visitor.
- Comment on posts.
- Like and unlike posts.
- Follow and unfollow other players.
- View a following-based feed.
- See online users through AJAX heartbeat.
- Start direct chats with other players.
- Create group chats.
- Invite users into group chats.
- Receive notifications for social interactions.

The purpose of this module is to make the game feel more like a multiplayer community rather than a standalone single-player game.

The social interaction flow can be described as:

```text
Play game → save score → visit profiles → follow players → post/comment/like → chat or join groups
```

---

## Chat and Notification Features

### Direct Chat

- Private one-to-one chat between players.
- AJAX polling for new messages.
- Unread direct message count.
- Chat shortcut from player profiles and social pages.

### Group Chat

- Create group chats.
- Invite multiple registered users.
- Search users when creating groups.
- Group message polling.
- Group unread message count.
- Group invitation notifications.

### Notifications

Users receive notifications for:

- New comments.
- Post likes.
- New followers.
- Direct messages.
- Group invitations.
- Group messages.

The navigation bar displays unread message badges, and popup notifications appear in the top-right corner.

---

## AI Game Assistant

Echo Escape includes an optional AI Game Assistant.

The assistant can help players with:

- Game instructions.
- Strategy suggestions.
- Project explanation.
- General help about Echo Escape features.

If an `OPENAI_API_KEY` is configured, the assistant uses the OpenAI API.

If no API key is available, the system falls back to local predefined responses, so the project still works during marking.

---

## Final Feature Summary

| Area | Implemented Features |
|---|---|
| Authentication | Register, login, logout, password hashing |
| Game | Canvas maze game, echo probes, monsters, traps, level selector |
| Results | Automatic result saving, score calculation, history page |
| Leaderboard | Ranking by player score |
| Profile | Public player profile, likes, follow, chat shortcut |
| Social Feed | Posts, comments, likes, following feed |
| Chat | Direct chat and group chat |
| Notifications | Unread badges and popup notifications |
| AI Assistant | Optional OpenAI-based assistant with local fallback |
| Testing | Pytest tests and Selenium test template |

---

## Technology Stack

This project uses the allowed core technologies:

- HTML
- CSS
- JavaScript
- Bootstrap
- Flask
- SQLite
- SQLAlchemy
- Flask-Login
- Flask-WTF
- AJAX / Fetch API
- Pytest

No React, Angular or other banned frontend frameworks are used.

---

## Project Structure

```text
echo-escape/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   └── __init__.py
├── docs/
├── tests/
├── config.py
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Database Models

The final version uses the following main database tables:

| Model | Purpose |
|---|---|
| User | Stores account and profile information |
| GameResult | Stores saved game attempts and scores |
| PlayerLike | Stores profile likes |
| SocialPost | Stores community posts |
| PostComment | Stores post comments |
| PostLike | Stores post likes |
| Follow | Stores follow relationships |
| ChatMessage | Stores direct messages |
| ChatGroup | Stores group chat rooms |
| GroupMember | Stores group membership |
| GroupMessage | Stores group chat messages |
| GroupReadState | Tracks unread group messages |
| Notification | Stores social and chat notifications |

---

## Main Routes

| Route | Purpose |
|---|---|
| `/` | Homepage |
| `/register` | Register account |
| `/login` | Login |
| `/logout` | Logout |
| `/game` | Main game page |
| `/history` | Personal game history |
| `/leaderboard` | Leaderboard |
| `/profile/<username>` | Public player profile |
| `/social` | Community feed |
| `/social/post` | Create post |
| `/social/post/<post_id>/comment` | Comment on post |
| `/social/post/<post_id>/like` | Like or unlike post |
| `/follow/<username>` | Follow or unfollow player |
| `/chat` | Chat overview |
| `/chat/<username>` | Direct chat |
| `/group/new` | Create group chat |
| `/group/<group_id>` | Group chat page |
| `/api/chat/<username>` | Direct chat API |
| `/api/group/<group_id>` | Group chat API |
| `/api/notifications` | Notification polling API |
| `/api/heartbeat` | Online status heartbeat |
| `/api/ai-chat` | AI assistant API |

---

## How to Run

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py
```

Open the project in the browser:

```text
http://127.0.0.1:5000
```

---

## Environment Variables

This project supports a local `.env` file.

First, copy the example file.

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
SECRET_KEY=change_this_to_a_random_secret_key
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

The OpenAI API key is optional.

If no API key is provided, the AI assistant will use local fallback responses.

Do not commit `.env` to GitHub.

---

## How to Play

| Key | Action |
|---|---|
| WASD / Arrow Keys | Move player |
| Space / E | Send echo probe |
| P | Pause |
| R | Restart |
| M | Toggle sound |

Gameplay goal:

1. Explore the dark maze.
2. Use echo probes to reveal the environment.
3. Avoid traps and monsters.
4. Find the exit.
5. Save your result and compare your score with other players.

---

## Testing

Run all tests:

```bash
pytest
```

Selenium tests are included as a template.

To run Selenium tests, install the required browser driver and set `RUN_SELENIUM=1`.

Windows:

```bash
set RUN_SELENIUM=1
pytest tests/test_selenium.py
```

macOS / Linux:

```bash
RUN_SELENIUM=1 pytest tests/test_selenium.py
```

---

## Why This Project Fits the CITS3403/CITS5505 Brief

| Requirement | Implementation |
|---|---|
| Client-server architecture | Flask backend with HTML/CSS/JavaScript frontend |
| Database-backed application | SQLite database with SQLAlchemy models |
| Login/logout system | Flask-Login authentication |
| User-generated data | Game results, posts, comments, likes, messages |
| Users can view other users' data | Leaderboard, profiles, social feed |
| JavaScript interaction | Canvas game, AJAX result saving, chat polling, notifications |
| Meaningful application logic | Game scoring, social interaction, unread counts |
| Security considerations | Password hashing, CSRF protection, environment variables |
| Testing | Pytest tests and Selenium template |

---

## Version Summary

### V3 Gameplay Foundation

The earlier version focused on building the core game system:

- Canvas-based maze game.
- Echo reveal mechanic.
- Result saving.
- Leaderboard.
- Player profiles.
- Level selector.
- Improved movement and collision.
- Initial test coverage.

### V4 Gameplay Redesign

The V4 redesign improved the core game mechanics:

- Walking automatically emits small probe particles.
- Space / E emits stronger probe balls.
- Strong probes can wake monsters.
- Soft probes reveal less but do not wake monsters.
- Monsters chase the player through corridors.
- Low-spec mode reduces visual effects for smoother performance.

### V5 Social Features

The V5 version shifted the project toward social interaction:

- Community feed.
- Posts.
- Comments.
- Likes.
- Follow and unfollow.
- Online user panel.
- Direct chat.
- Player profile chat actions.

### V6 Group Chat, Notifications and AI Assistant

The V6 version added advanced social features:

- Group chat.
- Group invitations.
- Direct and group unread counts.
- Notification popup system.
- Notifications for comments, likes, follows, direct messages and group messages.
- AI Game Assistant.
- Local fallback response when no API key is configured.

---

## GitHub Development Plan

Suggested GitHub issues:

1. Set up Flask project structure.
2. Implement user registration and login.
3. Build database models for users and game results.
4. Implement Canvas maze gameplay.
5. Add echo probe mechanics.
6. Add monsters, traps and exit detection.
7. Save game results through AJAX.
8. Build leaderboard page.
9. Build public player profile page.
10. Add community feed.
11. Add post comments and likes.
12. Add follow and unfollow system.
13. Add direct chat between players.
14. Add group chat system.
15. Add notification popup and unread badges.
16. Add optional AI Game Assistant.
17. Add social module tests.
18. Polish README and final documentation.

Suggested pull requests:

- PR 1: Project setup and base templates.
- PR 2: Authentication and user models.
- PR 3: Canvas game implementation.
- PR 4: Result saving and leaderboard.
- PR 5: Player profile and social feed.
- PR 6: Direct chat and group chat.
- PR 7: Notifications and AI assistant.
- PR 8: Tests, documentation and final polish.

---

## Security Notes

Before uploading to GitHub, make sure these files are not committed:

```text
.env
instance/
*.sqlite
*.db
venv/
__pycache__/
.pytest_cache/
```

The repository should include `.env.example`, but not the real `.env` file.

---

## Final Version Summary

The final version of Echo Escape combines a dark echo-location game with a social interaction platform.

The game provides the core play experience, while the social module allows players to share activity, follow others, chat, join groups, and receive notifications.

This creates a complete user flow:

```text
Register → Play game → Save score → View leaderboard → Visit profiles → Follow players → Post/comment/like → Chat or join groups
```

Echo Escape is therefore not only a browser game, but also a small community platform built around player interaction.
