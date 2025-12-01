# Would You Rather Discord Bot

A fun Discord bot that asks "Would You Rather" questions with an economy system, streaks, and leaderboards!

## Features

- Random Would You Rather questions with interactive button voting
- **Multi-user voting** - Everyone in the server can vote on the same question!
- **Live results** - See vote percentages update in real-time as people vote
- **Scheduled daily questions** - Automatically post a question every day at 12:00 PM UTC
- **User-submitted questions** - Anyone can submit questions for admin approval
- **Approval system** - Admins can easily approve/reject submissions with buttons
- Economy system with coins awarded for voting
- Daily streak tracking with bonus rewards
- Leaderboard to compete with friends
- Easy question management (admins can add questions directly)
- Prevents double-voting on the same question (one vote per user per question)
- Modern Discord slash commands

## Setup Instructions

### 1. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and add a bot
4. Copy your bot token (you'll need this later)
5. Enable these intents under "Privileged Gateway Intents":
   - Message Content Intent
   - Server Members Intent (optional)
6. Go to OAuth2 > URL Generator
7. Select scopes: `bot` and `applications.commands`
8. Select permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`
9. Copy the generated URL and invite the bot to your server

### 2. Development Environment Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Bot Token

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your bot token
# DISCORD_BOT_TOKEN=your_actual_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Commands

All commands use Discord's slash command system. Just type `/` in Discord to see all available commands!

### User Commands
- `/wyr` - Get a random Would You Rather question
- `/balance` - Check your coin balance and streak
- `/leaderboard` - View the top 10 users by coins
- `/submit` - Submit your own Would You Rather question for approval
- `/mysubmissions` - View the status of your submitted questions
- `/ping` - Check bot latency
- `/help` - Show all available commands

### Admin Commands
- `/pending` - View and approve/reject pending question submissions
  - Displays submissions with ✅ Approve and ❌ Reject buttons
  - Submitters get notified via DM when their question is reviewed
- `/addquestion` - Add a new question directly (bypasses approval)
  - `question`: The main question text
  - `option_a`: First option
  - `option_b`: Second option
  - `category`: Question category (optional, defaults to "General")
- `/setdaily` - Enable daily questions in a specific channel
  - Posts a question automatically every day at 12:00 PM UTC
  - Use `/testdaily` to preview how it works
- `/disabledaily` - Disable automatic daily questions
- `/testdaily` - Post a daily question immediately (for testing)

## How It Works

1. **Anyone** can use `/wyr` to post a question
2. **Everyone** in the server can click 👈 **Option A** or 👉 **Option B** to vote
3. Watch the results update live as more people vote!
4. Each person earns 10 coins for voting (one vote per question per user)
5. Build your streak by voting on consecutive days for bonus coins (up to 50 bonus)
6. Compete on the leaderboard with your friends!

### Example Voting Flow:
- Alice runs `/wyr` and gets a question about superpowers
- Alice votes, Bob votes, Charlie votes - all on the same question!
- The message updates to show live percentages
- Everyone earns coins and builds their streak

### Example Submission Flow:
- Charlie has a great question idea and uses `/submit`
- The question goes into the approval queue
- Admin Alice uses `/pending` and sees Charlie's submission
- Alice clicks ✅ Approve - the question is added to the database
- Charlie gets a DM notification that his question was approved!
- Next time someone uses `/wyr`, Charlie's question might appear!

### Example Daily Questions Setup:
- Admin Alice uses `/setdaily #general`
- Bot confirms daily questions are enabled for that channel
- Alice uses `/testdaily` to see a test question post immediately
- Every day at 12:00 PM UTC, a new question posts automatically with @here ping
- Server members get engaged daily without anyone needing to manually post!

## Database

The bot uses SQLite to store:
- User data (coins, streaks, stats)
- Questions (question text, options, categories)
- Votes (who voted for what)
- Submitted questions (pending/approved/rejected submissions)
- Server settings (daily question channel, enabled status)

The database is automatically initialized with 10 starter questions when you first run the bot.

## Development

### Running Tests

This project includes comprehensive tests for all database operations:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=term-missing

# Or use the Makefile
make test
make test-cov
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with Black
make format

# Run linting checks
make lint

# Clean up generated files
make clean
```

### GitHub Actions

The project includes a CI/CD pipeline that runs on every push and pull request:

- ✅ **Tests** - Runs on Python 3.9, 3.10, 3.11, and 3.12
- ✅ **Linting** - Checks code style with flake8 and black
- ✅ **Security** - Scans for security issues with bandit
- ✅ **Coverage** - Reports test coverage to Codecov

See `.github/workflows/test.yml` for details.

## Project Structure

```
WYRDiscordBot/
├── bot.py                   # Main bot code with commands and events
├── database.py              # Database operations and queries
├── test_database.py         # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── pytest.ini              # Pytest configuration
├── pyproject.toml          # Black and coverage configuration
├── .flake8                 # Flake8 linting configuration
├── Makefile                # Convenient development commands
├── .env                    # Your bot token (DO NOT COMMIT THIS)
├── .env.example            # Example env file
├── .gitignore              # Git ignore rules
├── .github/
│   └── workflows/
│       └── test.yml        # GitHub Actions CI/CD pipeline
├── wyr_bot.db              # SQLite database (auto-generated)
├── README.md               # This file
└── CONTRIBUTING.md         # Contribution guidelines
```

## Troubleshooting

- **Bot won't start**: Make sure you've added your bot token to the `.env` file
- **Slash commands don't appear**: Wait a few minutes after starting the bot for Discord to sync commands, or try kicking and re-inviting the bot with the updated OAuth2 URL
- **Buttons don't work**: Make sure the bot has "Send Messages" and "Use Slash Commands" permissions
- **Commands say "Application did not respond"**: The bot might be offline or experiencing connection issues

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Running tests
- Code style and formatting
- Submitting pull requests

Quick start for contributors:
```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/WYRDiscordBot.git
cd WYRDiscordBot

# Install dev dependencies
pip install -r requirements-dev.txt

# Make your changes and test
make test
make lint

# Submit a pull request!
```

## License

MIT License - feel free to use and modify as you wish!
