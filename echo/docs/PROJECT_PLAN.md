# Echo Escape Project Plan

## Project idea

Echo Escape is a web-based echo-navigation puzzle game. The player cannot see the full maze. They use sound pulses to reveal nearby walls, traps and exits.

## Main user stories

1. As a new player, I want to register so that my game progress can be saved.
2. As a returning player, I want to log in so that I can continue competing.
3. As a player, I want to play a dark maze game with multiple levels.
4. As a player, I want my result to be saved automatically after each attempt.
5. As a player, I want to view a leaderboard so that I can compare my performance with others.
6. As a player, I want to view other player profiles so that I can see their progress.
7. As a player, I want to like another player so that there is a simple social interaction.

## Database tables

### User

Stores account information.

### GameResult

Stores each game attempt.

### PlayerLike

Stores simple user-to-user likes.

## Suggested team split

### Member 1

Authentication, forms, user model and route tests.

### Member 2

Canvas game mechanics, levels and JavaScript.

### Member 3

Leaderboard, profile, history and result API.

### Member 4

UI polish, README, Selenium tests and presentation.
