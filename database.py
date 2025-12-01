import aiosqlite
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    coins INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    last_vote_date TEXT,
                    total_votes INTEGER DEFAULT 0
                )
            ''')

            # Questions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    category TEXT DEFAULT 'General'
                )
            ''')

            # Votes table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    user_id INTEGER,
                    question_id INTEGER,
                    choice TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, question_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            ''')

            # Submitted questions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS submitted_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submitter_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    status TEXT DEFAULT 'pending',
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by INTEGER,
                    reviewed_at TEXT
                )
            ''')

            # Settings table for daily questions and other config
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id INTEGER PRIMARY KEY,
                    daily_channel_id INTEGER,
                    daily_enabled INTEGER DEFAULT 0,
                    daily_time TEXT DEFAULT '12:00'
                )
            ''')

            await db.commit()

            # Add starter questions if table is empty
            await self._add_starter_questions(db)

    async def _add_starter_questions(self, db):
        """Add some starter questions if the database is empty"""
        cursor = await db.execute('SELECT COUNT(*) FROM questions')
        count = await cursor.fetchone()

        if count[0] == 0:
            starter_questions = [
                ("Would you rather have the ability to fly or be invisible?",
                 "Fly through the sky", "Become invisible", "Superpowers"),
                ("Would you rather live in the past or the future?",
                 "Live in the past", "Live in the future", "Time"),
                ("Would you rather be able to talk to animals or speak all languages?",
                 "Talk to animals", "Speak all languages", "Communication"),
                ("Would you rather have unlimited money or unlimited time?",
                 "Unlimited money", "Unlimited time", "Life"),
                ("Would you rather explore space or the deep ocean?",
                 "Explore space", "Explore the ocean", "Adventure"),
                ("Would you rather never have to sleep or never have to eat?",
                 "Never sleep", "Never eat", "Life"),
                ("Would you rather be famous or be the best friend of someone famous?",
                 "Be famous", "Friend of famous person", "Fame"),
                ("Would you rather live without music or without movies?",
                 "No music", "No movies", "Entertainment"),
                ("Would you rather be really good at one thing or average at everything?",
                 "Expert at one thing", "Average at everything", "Skills"),
                ("Would you rather know when you'll die or how you'll die?",
                 "Know when", "Know how", "Life"),
            ]

            for question, option_a, option_b, category in starter_questions:
                await db.execute(
                    'INSERT INTO questions (question, option_a, option_b, category) VALUES (?, ?, ?, ?)',
                    (question, option_a, option_b, category)
                )

            await db.commit()
            print(f"Added {len(starter_questions)} starter questions to database")

    async def get_random_question(self):
        """Get a random question from the database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id, question, option_a, option_b, category FROM questions ORDER BY RANDOM() LIMIT 1'
            )
            return await cursor.fetchone()

    async def get_question_by_id(self, question_id):
        """Get a specific question by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id, question, option_a, option_b, category FROM questions WHERE id = ?',
                (question_id,)
            )
            return await cursor.fetchone()

    async def has_user_voted(self, user_id, question_id):
        """Check if a user has already voted on a question"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT 1 FROM votes WHERE user_id = ? AND question_id = ?',
                (user_id, question_id)
            )
            result = await cursor.fetchone()
            return result is not None

    async def record_vote(self, user_id, question_id, choice):
        """Record a user's vote"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO votes (user_id, question_id, choice) VALUES (?, ?, ?)',
                (user_id, question_id, choice)
            )

            # Update user's total votes
            await db.execute(
                'UPDATE users SET total_votes = total_votes + 1 WHERE user_id = ?',
                (user_id,)
            )

            await db.commit()

    async def get_question_results(self, question_id):
        """Get voting results for a question"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT choice, COUNT(*) FROM votes WHERE question_id = ? GROUP BY choice',
                (question_id,)
            )
            results = await cursor.fetchall()

            a_votes = 0
            b_votes = 0

            for choice, count in results:
                if choice == 'a':
                    a_votes = count
                elif choice == 'b':
                    b_votes = count

            return {'a_votes': a_votes, 'b_votes': b_votes}

    async def get_user(self, user_id):
        """Get or create user data"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT user_id, coins, streak, last_vote_date, total_votes FROM users WHERE user_id = ?',
                (user_id,)
            )
            user = await cursor.fetchone()

            if user is None:
                # Create new user
                await db.execute(
                    'INSERT INTO users (user_id, coins, streak, total_votes) VALUES (?, 0, 0, 0)',
                    (user_id,)
                )
                await db.commit()
                return {'user_id': user_id, 'coins': 0, 'streak': 0, 'last_vote_date': None, 'total_votes': 0}

            return {
                'user_id': user[0],
                'coins': user[1],
                'streak': user[2],
                'last_vote_date': user[3],
                'total_votes': user[4]
            }

    async def award_coins(self, user_id, amount):
        """Award coins to a user"""
        async with aiosqlite.connect(self.db_path) as db:
            # Ensure user exists
            await self.get_user(user_id)

            await db.execute(
                'UPDATE users SET coins = coins + ? WHERE user_id = ?',
                (amount, user_id)
            )
            await db.commit()

    async def update_streak(self, user_id):
        """Update user's streak based on voting"""
        async with aiosqlite.connect(self.db_path) as db:
            user = await self.get_user(user_id)

            today = datetime.now().date()
            last_vote = user['last_vote_date']

            if last_vote:
                last_vote_date = datetime.fromisoformat(last_vote).date()
                days_diff = (today - last_vote_date).days

                if days_diff == 1:
                    # Consecutive day, increment streak
                    new_streak = user['streak'] + 1
                    # Award bonus coins for streak
                    bonus = min(new_streak * 2, 50)  # Cap at 50 bonus coins
                    await db.execute(
                        'UPDATE users SET streak = ?, last_vote_date = ?, coins = coins + ? WHERE user_id = ?',
                        (new_streak, today.isoformat(), bonus, user_id)
                    )
                elif days_diff > 1:
                    # Streak broken, reset to 1
                    await db.execute(
                        'UPDATE users SET streak = 1, last_vote_date = ? WHERE user_id = ?',
                        (today.isoformat(), user_id)
                    )
                # If days_diff == 0, already voted today, don't update
            else:
                # First vote ever
                await db.execute(
                    'UPDATE users SET streak = 1, last_vote_date = ? WHERE user_id = ?',
                    (today.isoformat(), user_id)
                )

            await db.commit()

    async def get_leaderboard(self, limit=10):
        """Get top users by coins"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT user_id, coins, streak FROM users ORDER BY coins DESC LIMIT ?',
                (limit,)
            )
            return await cursor.fetchall()

    async def add_question(self, question, option_a, option_b, category="General"):
        """Add a new question to the database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO questions (question, option_a, option_b, category) VALUES (?, ?, ?, ?)',
                (question, option_a, option_b, category)
            )
            await db.commit()

    async def submit_question(self, submitter_id, question, option_a, option_b, category="General"):
        """Submit a question for approval"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO submitted_questions (submitter_id, question, option_a, option_b, category) VALUES (?, ?, ?, ?, ?)',
                (submitter_id, question, option_a, option_b, category)
            )
            await db.commit()

    async def get_pending_submissions(self, limit=10):
        """Get pending question submissions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id, submitter_id, question, option_a, option_b, category, submitted_at FROM submitted_questions WHERE status = ? ORDER BY submitted_at ASC LIMIT ?',
                ('pending', limit)
            )
            return await cursor.fetchall()

    async def get_submission_by_id(self, submission_id):
        """Get a specific submission by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id, submitter_id, question, option_a, option_b, category, status FROM submitted_questions WHERE id = ?',
                (submission_id,)
            )
            return await cursor.fetchone()

    async def approve_submission(self, submission_id, reviewer_id):
        """Approve a submission and add it to questions"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get the submission
            cursor = await db.execute(
                'SELECT question, option_a, option_b, category FROM submitted_questions WHERE id = ?',
                (submission_id,)
            )
            submission = await cursor.fetchone()

            if submission:
                question, option_a, option_b, category = submission

                # Add to questions table
                await db.execute(
                    'INSERT INTO questions (question, option_a, option_b, category) VALUES (?, ?, ?, ?)',
                    (question, option_a, option_b, category)
                )

                # Update submission status
                await db.execute(
                    'UPDATE submitted_questions SET status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?',
                    ('approved', reviewer_id, datetime.now().isoformat(), submission_id)
                )

                await db.commit()
                return True
            return False

    async def reject_submission(self, submission_id, reviewer_id):
        """Reject a submission"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE submitted_questions SET status = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?',
                ('rejected', reviewer_id, datetime.now().isoformat(), submission_id)
            )
            await db.commit()

    async def get_user_submissions(self, user_id):
        """Get all submissions from a user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT id, question, option_a, option_b, category, status, submitted_at FROM submitted_questions WHERE submitter_id = ? ORDER BY submitted_at DESC',
                (user_id,)
            )
            return await cursor.fetchall()

    async def set_daily_channel(self, guild_id, channel_id):
        """Set the channel for daily questions"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO settings (guild_id, daily_channel_id, daily_enabled) VALUES (?, ?, 1)',
                (guild_id, channel_id)
            )
            await db.commit()

    async def get_daily_channel(self, guild_id):
        """Get the daily question channel for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT daily_channel_id, daily_enabled FROM settings WHERE guild_id = ?',
                (guild_id,)
            )
            result = await cursor.fetchone()
            if result:
                return {'channel_id': result[0], 'enabled': bool(result[1])}
            return None

    async def disable_daily_questions(self, guild_id):
        """Disable daily questions for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE settings SET daily_enabled = 0 WHERE guild_id = ?',
                (guild_id,)
            )
            await db.commit()

    async def get_all_daily_channels(self):
        """Get all guilds with daily questions enabled"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT guild_id, daily_channel_id FROM settings WHERE daily_enabled = 1'
            )
            return await cursor.fetchall()
