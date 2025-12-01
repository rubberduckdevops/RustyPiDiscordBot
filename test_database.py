import pytest
import aiosqlite
import os
from database import Database
from datetime import datetime

# Test database path
TEST_DB = "test_wyr_bot.db"


@pytest.fixture
async def db():
    """Create a test database instance"""
    # Remove test database if it exists
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    test_db = Database(TEST_DB)
    await test_db.initialize()
    yield test_db

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_database_initialization(db):
    """Test that database initializes with starter questions"""
    question = await db.get_random_question()
    assert question is not None
    assert len(question) == 5  # id, question, option_a, option_b, category


@pytest.mark.asyncio
async def test_add_question(db):
    """Test adding a new question"""
    await db.add_question("Test question?", "Option A", "Option B", "Test Category")

    # Verify question was added
    async with aiosqlite.connect(TEST_DB) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM questions WHERE question = ?", ("Test question?",))
        count = await cursor.fetchone()
        assert count[0] == 1


@pytest.mark.asyncio
async def test_user_creation(db):
    """Test user creation and retrieval"""
    user_id = 123456789
    user = await db.get_user(user_id)

    assert user["user_id"] == user_id
    assert user["coins"] == 0
    assert user["streak"] == 0
    assert user["total_votes"] == 0


@pytest.mark.asyncio
async def test_award_coins(db):
    """Test awarding coins to a user"""
    user_id = 123456789

    # Award coins
    await db.award_coins(user_id, 50)

    # Verify coins were awarded
    user = await db.get_user(user_id)
    assert user["coins"] == 50

    # Award more coins
    await db.award_coins(user_id, 25)
    user = await db.get_user(user_id)
    assert user["coins"] == 75


@pytest.mark.asyncio
async def test_record_vote(db):
    """Test recording a vote"""
    user_id = 123456789
    question_id = 1

    # Record vote
    await db.record_vote(user_id, question_id, "a")

    # Verify vote was recorded
    has_voted = await db.has_user_voted(user_id, question_id)
    assert has_voted is True

    # Verify user can't vote twice
    has_voted_again = await db.has_user_voted(user_id, question_id)
    assert has_voted_again is True


@pytest.mark.asyncio
async def test_question_results(db):
    """Test getting voting results"""
    question_id = 1

    # Record some votes
    await db.record_vote(111, question_id, "a")
    await db.record_vote(222, question_id, "a")
    await db.record_vote(333, question_id, "b")

    # Get results
    results = await db.get_question_results(question_id)
    assert results["a_votes"] == 2
    assert results["b_votes"] == 1


@pytest.mark.asyncio
async def test_leaderboard(db):
    """Test leaderboard functionality"""
    # Create users with different coin amounts
    await db.award_coins(111, 100)
    await db.award_coins(222, 200)
    await db.award_coins(333, 150)

    # Get leaderboard
    leaderboard = await db.get_leaderboard(3)

    assert len(leaderboard) == 3
    assert leaderboard[0][1] == 200  # User 222 should be first
    assert leaderboard[1][1] == 150  # User 333 should be second
    assert leaderboard[2][1] == 100  # User 111 should be third


@pytest.mark.asyncio
async def test_streak_tracking(db):
    """Test daily streak tracking"""
    user_id = 123456789

    # First vote - should set streak to 1
    await db.update_streak(user_id)
    user = await db.get_user(user_id)
    assert user["streak"] == 1

    # Same day vote - streak should stay 1
    await db.update_streak(user_id)
    user = await db.get_user(user_id)
    assert user["streak"] == 1


@pytest.mark.asyncio
async def test_submit_question(db):
    """Test submitting a question for approval"""
    submitter_id = 123456789

    await db.submit_question(submitter_id, "Submitted question?", "Sub Option A", "Sub Option B", "Submitted")

    # Get pending submissions
    pending = await db.get_pending_submissions(10)
    assert len(pending) >= 1

    # Verify submission details
    submission = pending[0]
    assert submission[1] == submitter_id
    assert submission[2] == "Submitted question?"


@pytest.mark.asyncio
async def test_approve_submission(db):
    """Test approving a submitted question"""
    submitter_id = 123456789
    reviewer_id = 987654321

    # Submit a question
    await db.submit_question(submitter_id, "Approve me?", "Yes", "No", "Test")

    # Get submission ID
    pending = await db.get_pending_submissions(1)
    submission_id = pending[0][0]

    # Approve it
    success = await db.approve_submission(submission_id, reviewer_id)
    assert success is True

    # Verify it's in the questions table
    async with aiosqlite.connect(TEST_DB) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM questions WHERE question = ?", ("Approve me?",))
        count = await cursor.fetchone()
        assert count[0] == 1

    # Verify submission status changed
    submission = await db.get_submission_by_id(submission_id)
    assert submission[6] == "approved"


@pytest.mark.asyncio
async def test_reject_submission(db):
    """Test rejecting a submitted question"""
    submitter_id = 123456789
    reviewer_id = 987654321

    # Submit a question
    await db.submit_question(submitter_id, "Reject me?", "Yes", "No", "Test")

    # Get submission ID
    pending = await db.get_pending_submissions(1)
    submission_id = pending[0][0]

    # Reject it
    await db.reject_submission(submission_id, reviewer_id)

    # Verify submission status changed
    submission = await db.get_submission_by_id(submission_id)
    assert submission[6] == "rejected"


@pytest.mark.asyncio
async def test_daily_channel_settings(db):
    """Test daily channel configuration"""
    guild_id = 111222333
    channel_id = 444555666

    # Set daily channel
    await db.set_daily_channel(guild_id, channel_id)

    # Get settings
    config = await db.get_daily_channel(guild_id)
    assert config is not None
    assert config["channel_id"] == channel_id
    assert config["enabled"] is True

    # Disable daily questions
    await db.disable_daily_questions(guild_id)

    # Verify disabled
    config = await db.get_daily_channel(guild_id)
    assert config["enabled"] is False


@pytest.mark.asyncio
async def test_get_user_submissions(db):
    """Test getting all submissions from a user"""
    user_id = 123456789

    # Submit multiple questions
    await db.submit_question(user_id, "Q1?", "A", "B", "Cat1")
    await db.submit_question(user_id, "Q2?", "A", "B", "Cat2")
    await db.submit_question(user_id, "Q3?", "A", "B", "Cat3")

    # Get user submissions
    submissions = await db.get_user_submissions(user_id)
    assert len(submissions) == 3


@pytest.mark.asyncio
async def test_get_question_by_id(db):
    """Test retrieving a specific question by ID"""
    # Add a question
    await db.add_question("Find me?", "A", "B", "Test")

    # Get the question ID
    question = await db.get_random_question()
    question_id = question[0]

    # Retrieve by ID
    retrieved = await db.get_question_by_id(question_id)
    assert retrieved is not None
    assert retrieved[0] == question_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
