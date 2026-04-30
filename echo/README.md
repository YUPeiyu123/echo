# Echo Escape V3.1 Fixed + Optimised

Echo Escape is a Dark Echo-inspired web game project built with Flask, SQLite and JavaScript Canvas.

The player explores a dark maze. The map is not fully visible. The player sends echo pulses to reveal walls, traps and the exit. Results are saved to the server and shown on a leaderboard.

## V3.1 fix

- Fixed the Start Game button issue caused by using a decimal radius in the tile reveal loop.
- The reveal loop now converts radius values to safe integer tile ranges before reading map arrays.

## V3.2 improvements

This version improves almost every part of the previous prototype:

### Game improvements

- 12 playable levels instead of 10.
- Levels are generated and validated as solvable before being written into the game file.
- Better level names and difficulty labels.
- Level selector on the game page.
- Server summary panel showing wins, losses and best score.
- Per-level best result display.
- Pause key added.
- Smoother movement and better player collision.
- Stronger echo effects, particles, wall memory traces and dark visual atmosphere.

### Web app improvements

- Cleaner route structure.
- More complete profile page with level progress.
- Better homepage statistics.
- Stronger result validation on the server.
- Improved README and project explanation.
- More test coverage.

## Why this fits the CITS3403/CITS5505 project brief

| Requirement | Implementation |
|---|---|
| Client-server architecture | Flask backend + HTML/CSS/JavaScript frontend |
| Login/logout | Flask-Login registration, login and logout |
| User data persisted | SQLite database using SQLAlchemy |
| Users can view other users' data | Leaderboard, public player profiles and likes |
| Engaging design | Dark echo-location Canvas game with glow and particle effects |
| JavaScript | Canvas rendering, game logic and AJAX result saving |
| Flask code | Routes for auth, game, leaderboard, profile and API |
| Data models | User, GameResult and PlayerLike models |
| Security | Werkzeug salted password hashes and Flask-WTF CSRF |
| Testing | Pytest unit tests and Selenium test template included |

## Technology

Allowed core technologies:

- HTML
- CSS
- JavaScript
- Bootstrap
- Flask
- SQLite
- SQLAlchemy
- AJAX/fetch

No React, Angular or other banned core frameworks are used.

## How to run

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

## How to initialise database with migrations

The development version creates tables automatically. For the final GitHub submission, use Flask-Migrate:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial database"
flask --app run.py db upgrade
```

Then commit the generated `migrations/` folder.

## How to play

- WASD / Arrow keys: move
- Space / E: send echo
- P: pause
- R: restart
- M: toggle echo sound

## Web app features

- Register account
- Login/logout
- Play 12 levels
- Save game result automatically
- View leaderboard
- View player profile
- Like another player
- View personal game history
- See per-level progress

## Run tests

```bash
pytest
```

Selenium tests are included as a template. To run them, install a browser driver and set:

Windows:

```bash
set RUN_SELENIUM=1
pytest tests/test_selenium.py
```

macOS/Linux:

```bash
RUN_SELENIUM=1 pytest tests/test_selenium.py
```

## Suggested GitHub issues

1. Build registration and login pages
2. Build user database models
3. Implement Canvas game movement
4. Implement echo reveal mechanic
5. Add traps and exit detection
6. Save results through AJAX
7. Build leaderboard page
8. Build player profile page
9. Add level selector and level progress panel
10. Add unit tests for auth and result saving
11. Add Selenium tests for key user flows
12. Polish README and final presentation

## Suggested pull requests

- PR 1: Project setup and base templates
- PR 2: Authentication system
- PR 3: Canvas game implementation
- PR 4: Result API and database persistence
- PR 5: Leaderboard, profile and likes
- PR 6: Level selector and summary panel
- PR 7: Tests and README polish


## V3.2 black-screen fix

This version fixes the common "black screen after clicking Start" problem by:

- making the player much brighter;
- revealing the nearby area at the start of every level;
- drawing an initial visible preview before Start is clicked;
- adding defensive JavaScript error handling;
- showing an on-screen error message if Canvas or JavaScript fails;
- fixing float-radius reveal logic with integer-safe loops.

If the page still appears black, open the browser console with F12 and check for a red JavaScript error.


## V3.3 canvas fix

This version fixes the JavaScript error:

`canvas is not defined`

The Canvas element and 2D context are now declared inside the game module and assigned after the DOM is loaded.


## V4 gameplay redesign

This version changes the core game mechanic based on the new design direction:

- Walking automatically emits small probe particles.
- The main sound effect is no longer a circular radar wave.
- Space / E emits many small probe balls in different directions.
- Probe balls travel through corridors, bounce off walls, and leave glowing trails.
- Monsters are placed in multiple levels.
- Strong probes can wake monsters if they touch them.
- Walking too close to a monster can also wake it.
- Woken monsters chase the player at roughly the same speed.
- Rapid Space / E taps produce dim soft probes.
- Soft probes reveal less but do not wake monsters.


## Low-spec mode

This package uses `game_v4_lite_low_spec.js` settings:

- Canvas DPR capped at 1
- Fewer walking probes
- Fewer strong and soft probes
- Shorter probe trails
- Fewer particles
- Reduced glow/shadow blur
- Scanlines disabled
- Active probes and particles capped

Use this version if the normal V4 version is laggy on your computer.


## V4.1 white probe visual update

This version changes the probe visual style:

- probe balls are bright white;
- probe trails are white lines;
- walking probes are softer white-grey;
- rapid soft probes are dimmer white-grey;
- walls are revealed with white/grey glow instead of blue;
- monster danger remains red;
- exit remains green for clear gameplay feedback.


## V4.2 minimal low-spec + monster fix

This version reduces visual effects and fixes monster behaviour:

- no heavy glow;
- no scanlines;
- no particle burst system;
- no large radar circle;
- only white probe balls and white probe lines;
- fewer walking probes;
- capped active probes;
- strong probes wake monsters reliably when they pass near them;
- rapid E/Space soft probes are dim and do not wake monsters;
- walking too close to monsters wakes them;
- monsters use grid pathfinding to chase the player through corridors.


## V5 social features

This version shifts the project focus toward communication and social interaction.

### New social features

- Community feed similar to a simple Moments/Facebook-style timeline.
- Visitors who are not logged in can read posts only.
- Logged-in users can create posts.
- Logged-in users can comment on posts.
- Logged-in users can like/unlike posts.
- Logged-in users can follow/unfollow other players.
- Following feed shows posts from followed players.
- Online user panel uses AJAX heartbeat.
- Private chat uses AJAX polling.
- Player profile includes follow/chat actions.

### New database tables

- social_posts
- post_comments
- post_likes
- follows
- chat_messages

### New routes

- /social
- /social/post
- /social/post/<post_id>/comment
- /social/post/<post_id>/like
- /follow/<username>
- /chat
- /chat/<username>
- /api/chat/<username>
- /api/heartbeat
- /api/online


## V6 group chat, notifications and AI assistant

### New features

- Create group chats.
- Invite multiple users into a group.
- Invite from followed users and all registered users.
- Search registered users when creating a group.
- Group chat messages use AJAX polling.
- Direct chat and group chat unread counts.
- Chat nav red badge: shows unread count, 9+ if over 9.
- Notification popup in the top-right corner for around 3 seconds.
- Notifications for comments, post likes, follows, direct messages, group invitations and group messages.
- AI Game Assistant pinned at the top of the chat page.
- AI assistant uses OpenAI API if OPENAI_API_KEY is configured.
- AI assistant falls back to a local answer if no API key exists, so the project still works during marking.

### OpenAI API setup

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-4.1-mini"
python run.py
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4.1-mini"
python run.py
```

The API key is read from environment variables. Do not commit your API key to GitHub.

### New database tables

- chat_groups
- group_members
- group_messages
- group_read_states
- notifications


## V6.1 environment file setup

This version supports a local `.env` file.

### Step 1: copy `.env.example`

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### Step 2: edit `.env`

Put your real API key inside `.env`:

```env
OPENAI_API_KEY=your_real_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
SECRET_KEY=change_this_to_a_random_secret_key
```

### Step 3: run the project

```bash
pip install -r requirements.txt
python run.py
```

### Security reminder

Do not upload `.env` to GitHub. The `.gitignore` file already includes `.env`, `instance/`, virtual environments and SQLite files.
