## Quick Checklist

**1. Setup & Prerequisites**
- [ ] Create a Discord account (if needed)
- [ ] Go to [Discord Developer Portal](https://discord.com/developers/applications)
- [ ] Create a new application
- [ ] Add a bot to your application
- [ ] Copy the bot token (keep this secret!)
- [ ] Enable necessary intents (Message Content Intent for reading messages)
- [ ] Generate OAuth2 invite link with proper permissions (Send Messages, Add Reactions, Manage Messages)
- [ ] Invite bot to your test server

**2. Development Environment**
- [ ] Install Python 3.8+ 
- [ ] Create a virtual environment: `python -m venv venv`
- [ ] Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
- [ ] Install discord.py: `pip install discord.py`
- [ ] Install database library: `pip install aiosqlite` (async SQLite)
- [ ] Set up `.env` file for your bot token (use `python-dotenv`)

**3. Basic Bot Structure**
- [ ] Create main bot file with connection test
- [ ] Set up command prefix or slash commands
- [ ] Test basic ping/pong command
- [ ] Set up event listeners (on_ready, on_message, on_reaction_add)

**4. Database Design**
- [ ] Design schema for users table (user_id, coins, streak, stats)
- [ ] Design schema for questions table (id, question, option_a, option_b, category)
- [ ] Design schema for votes table (user_id, question_id, choice, timestamp)
- [ ] Create database initialization script
- [ ] Add some starter questions

**5. Would You Rather Core**
- [ ] Command to fetch and display random question
- [ ] Add reaction buttons (👈/👉) automatically
- [ ] Listen for user reactions
- [ ] Record votes in database
- [ ] Show results after user votes
- [ ] Prevent double voting on same question

**6. Economy System**
- [ ] Award coins for voting
- [ ] Daily streak tracking and bonus
- [ ] Balance check command
- [ ] Leaderboard command
- [ ] Basic shop framework

**7. Advanced Features**
- [ ] Scheduled daily questions (using tasks.loop)
- [ ] User-submitted questions with approval queue
- [ ] Prediction/betting system
- [ ] Stats and analytics commands

**8. Polish & Deploy**
- [ ] Error handling and logging
- [ ] Help command with feature explanations
- [ ] Test thoroughly
- [ ] Deploy to hosting service (Heroku, Railway, VPS, etc.)

Want me to help you start coding any specific part of this?