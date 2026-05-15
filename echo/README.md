# Echo Escape

Echo Escape is a Flask-based web game and social interaction platform.  
The core gameplay is inspired by dark echo-location mechanics: players explore a dark maze, send echo probes to reveal walls and traps, avoid monsters, and reach the exit.

Beyond the game itself, Echo Escape includes a complete social module. Players can create posts, comment, like, follow other players, chat privately, create group chats, receive notifications, and use an optional AI Game Assistant.

The final version focuses on connecting gameplay with social interaction:

```text
Play game → save result → view leaderboard → interact with players → chat / follow / join groups
Key Features
1. Gameplay Features
Dark maze exploration game built with JavaScript Canvas.
Echo probe mechanic for revealing the hidden map.
Walking probes, strong probes and soft probes.
Monsters that can be woken by strong probes or close player movement.
Monster pathfinding through corridors.
12 playable levels.
Level selector and difficulty labels.
Pause, restart and sound toggle controls.
Automatic game result saving.
Score calculation based on time, echo count, deaths and result.
Low-spec visual mode for smoother performance.
2. User Account Features
User registration.
User login and logout.
Password hashing using Werkzeug.
Session management using Flask-Login.
CSRF protection using Flask-WTF.
Public player profile pages.
Personal game history.
Per-level progress display.
Best score and recent result summary.
3. Leaderboard and Player Profiles
Global leaderboard.
Player ranking by score.
Public profile pages.
Player win/loss summary.
Best result display.
Recent game result display.
Like player profile.
Follow/unfollow players.
Chat shortcut from player profile.
Social Interaction Module

The social module was upgraded from a simple community feed into a game-connected community system.

Players can:

Create community posts.
View posts as a public visitor.
Comment on posts.
Like and unlike posts.
Follow and unfollow other players.
View a following-based feed.
See online users through AJAX heartbeat.
Start direct chats with other players.
Create group chats.
Invite users into group chats.
Receive notifications for social interactions.

The purpose of this module is to make the game feel more like a multiplayer community rather than a standalone single-player game.

Chat and Notification Features
Direct Chat
Private one-to-one chat between players.
AJAX polling for new messages.
Unread direct message count.
Chat shortcut from profile and social pages.
Group Chat
Create group chats.
Invite multiple registered users.
Search users when creating groups.
Group message polling.
Group unread message count.
Group invitation notifications.
Notifications

Users receive notifications for:

New comments.
Post likes.
New followers.
Direct messages.
Group invitations.
Group messages.

The navigation bar displays unread message badges, and popup notifications appear in the top-right corner.

AI Game Assistant

Echo Escape includes an optional AI Game Assistant.

The assistant can help players with:

Game instructions.
Strategy suggestions.
Project explanation.
General help about Echo Escape features.

If an OPENAI_API_KEY is configured, the assistant uses the OpenAI API.
If no API key is available, the system falls back to local predefined responses, so the project still works during marking.

Final Feature Summary
Area	Implemented Features
Authentication	Register, login, logout, password hashing
Game	Canvas maze game, echo probes, monsters, traps, level selector
Results	Automatic result saving, score calculation, history page
Leaderboard	Ranking by player score
Profile	Public player profile, likes, follow, chat shortcut
Social Feed	Posts, comments, likes, following feed
Chat	Direct chat and group chat
Notifications	Unread badges and popup notifications
AI Assistant	Optional OpenAI-based assistant with local fallback
Testing	Pytest tests and Selenium test template
Technology Stack

This project uses the allowed core technologies:

HTML
CSS
JavaScript
Bootstrap
Flask
SQLite
SQLAlchemy
Flask-Login
Flask-WTF
AJAX / Fetch API
Pytest

No React, Angular or other banned frontend frameworks are used.

Project Structure
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
Database Models

The final version uses the following main database tables:

Model	Purpose
User	Stores account and profile information
GameResult	Stores saved game attempts and scores
PlayerLike	Stores profile likes
SocialPost	Stores community posts
PostComment	Stores post comments
PostLike	Stores post likes
Follow	Stores follow relationships
ChatMessage	Stores direct messages
ChatGroup	Stores group chat rooms
GroupMember	Stores group membership
GroupMessage	Stores group chat messages
GroupReadState	Tracks unread group messages
Notification	Stores social and chat notifications
Main Routes
Route	Purpose
/	Homepage
/register	Register account
/login	Login
/logout	Logout
/game	Main game page
/history	Personal game history
/leaderboard	Leaderboard
/profile/<username>	Public player profile
/social	Community feed
/social/post	Create post
/social/post/<post_id>/comment	Comment on post
/social/post/<post_id>/like	Like or unlike post
/follow/<username>	Follow or unfollow player
/chat	Chat overview
/chat/<username>	Direct chat
/group/new	Create group chat
/group/<group_id>	Group chat page
/api/chat/<username>	Direct chat API
/api/group/<group_id>	Group chat API
/api/notifications	Notification polling API
/api/heartbeat	Online status heartbeat
/api/ai-chat	AI assistant API
How to Run

Create a virtual environment:

python -m venv venv

Activate it.

Windows:

venv\Scripts\activate

macOS / Linux:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run the application:

python run.py

Open the project in the browser:

http://127.0.0.1:5000
Environment Variables

This project supports a local .env file.

First, copy the example file:

Windows PowerShell:

copy .env.example .env

macOS / Linux:

cp .env.example .env

Then edit .env:

SECRET_KEY=change_this_to_a_random_secret_key
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini

The OpenAI API key is optional.
If no API key is provided, the AI assistant will use local fallback responses.

Do not commit .env to GitHub.

How to Play
Key	Action
WASD / Arrow Keys	Move player
Space / E	Send echo probe
P	Pause
R	Restart
M	Toggle sound

Gameplay goal:

Explore the dark maze.
Use echo probes to reveal the environment.
Avoid traps and monsters.
Find the exit.
Save your result and compare your score with other players.
Testing

Run all tests:

pytest

Selenium tests are included as a template.
To run Selenium tests, install the required browser driver and set RUN_SELENIUM=1.

Windows:

set RUN_SELENIUM=1
pytest tests/test_selenium.py

macOS / Linux:

RUN_SELENIUM=1 pytest tests/test_selenium.py
Why This Project Fits the CITS3403/CITS5505 Brief
Requirement	Implementation
Client-server architecture	Flask backend with HTML/CSS/JavaScript frontend
Database-backed application	SQLite database with SQLAlchemy models
Login/logout system	Flask-Login authentication
User-generated data	Game results, posts, comments, likes, messages
Users can view other users' data	Leaderboard, profiles, social feed
JavaScript interaction	Canvas game, AJAX result saving, chat polling, notifications
Meaningful application logic	Game scoring, social interaction, unread counts
Security considerations	Password hashing, CSRF protection, environment variables
Testing	Pytest tests and Selenium template
GitHub Development Plan

Suggested GitHub issues:

Set up Flask project structure.
Implement user registration and login.
Build database models for users and game results.
Implement Canvas maze gameplay.
Add echo probe mechanics.
Add monsters, traps and exit detection.
Save game results through AJAX.
Build leaderboard page.
Build public player profile page.
Add community feed.
Add post comments and likes.
Add follow and unfollow system.
Add direct chat between players.
Add group chat system.
Add notification popup and unread badges.
Add optional AI Game Assistant.
Add social module tests.
Polish README and final documentation.

Suggested pull requests:

PR 1: Project setup and base templates.
PR 2: Authentication and user models.
PR 3: Canvas game implementation.
PR 4: Result saving and leaderboard.
PR 5: Player profile and social feed.
PR 6: Direct chat and group chat.
PR 7: Notifications and AI assistant.
PR 8: Tests, documentation and final polish.
Security Notes

Before uploading to GitHub, make sure these files are not committed:

.env
instance/
*.sqlite
*.db
venv/
__pycache__/
.pytest_cache/

The repository should include .env.example, but not the real .env file.

Final Version Summary

The final version of Echo Escape combines a dark echo-location game with a social interaction platform. The game provides the core play experience, while the social module allows players to share activity, follow others, chat, join groups, and receive notifications.

This creates a complete user flow:

Register → Play game → Save score → View leaderboard → Visit profiles → Follow players → Post/comment/like → Chat or join groups

Echo Escape is therefore not only a browser game, but also a small community platform built around player interaction.
