# Testing Guide

This document explains the testing setup for the Would You Rather Discord Bot.

## Test Results

```
✅ 14 tests passing
✅ 94% database coverage
✅ All async operations tested
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing
```

### Using Makefile

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# View coverage in browser
make coverage
```

## What's Tested

### Database Operations (14 tests)

1. **Initialization** - Database tables and starter questions
2. **Questions** - Adding, retrieving, and getting by ID
3. **Users** - Creation, coin awards, streak tracking
4. **Voting** - Recording votes, preventing duplicates, getting results
5. **Leaderboard** - Ranking users by coins
6. **Submissions** - User question submissions
7. **Approval System** - Approving and rejecting submissions
8. **Daily Questions** - Channel configuration and settings
9. **User Submissions History** - Tracking submission status

## Test Coverage

Current coverage: **94% on database.py**

Missing coverage (database.py):
- Lines 230-233: Consecutive day streak logic edge cases
- Line 239: First vote ever path
- Line 325: Exception handling path
- Lines 364, 377-381: Return value paths

These are minor edge cases and error handling paths that are difficult to test in isolation.

## Continuous Integration

### GitHub Actions Workflow

The `.github/workflows/test.yml` file runs:

1. **Tests** on multiple Python versions:
   - Python 3.9
   - Python 3.10
   - Python 3.11
   - Python 3.12

2. **Linting**:
   - flake8 for code quality
   - black for code formatting

3. **Security**:
   - bandit for security vulnerabilities

4. **Coverage**:
   - Uploads to Codecov (optional)

### Workflow Triggers

Tests run automatically on:
- Push to `main` branch
- Pull requests to `main` branch

## Writing New Tests

When adding new features, follow this pattern:

```python
@pytest.mark.asyncio
async def test_your_feature(db):
    """Test description"""
    # Arrange - Set up test data
    user_id = 123456789

    # Act - Perform the action
    result = await db.your_new_function(user_id)

    # Assert - Verify the result
    assert result is not None
    assert result['some_field'] == expected_value
```

### Test Fixtures

The `db` fixture provides:
- Fresh test database for each test
- Automatic cleanup after test
- Isolated test environment

## Debugging Tests

### Run specific tests

```bash
# Run one test file
pytest test_database.py

# Run one specific test
pytest test_database.py::test_add_question

# Run tests matching a pattern
pytest -k "submit"
```

### See detailed output

```bash
# Show print statements
pytest -s

# Show full traceback
pytest --tb=long

# Stop at first failure
pytest -x
```

## Coverage Reports

### Terminal Report

```bash
pytest --cov=. --cov-report=term-missing
```

Shows coverage with line numbers of missing coverage.

### HTML Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # Mac/Linux
```

Interactive HTML report showing exactly which lines are covered.

### XML Report (for CI)

```bash
pytest --cov=. --cov-report=xml
```

Generates `coverage.xml` for tools like Codecov.

## Best Practices

1. **Test isolation** - Each test should be independent
2. **Clear names** - Test names should describe what they test
3. **AAA pattern** - Arrange, Act, Assert
4. **One assertion per test** - Or related assertions only
5. **Test edge cases** - Empty inputs, None values, errors
6. **Async tests** - Use `@pytest.mark.asyncio` decorator
7. **Clean up** - Use fixtures for setup/teardown

## Troubleshooting

### Tests fail locally but pass in CI

- Check Python version (run `python --version`)
- Ensure all dependencies are installed
- Delete `__pycache__` and `.pytest_cache`

### Import errors

```bash
# Make sure you're in the project directory
cd /path/to/WYRDiscordBot

# Install dependencies
pip install -r requirements.txt
```

### Database locked errors

- Close any other connections to test database
- Delete `test_*.db` files
- Run tests again

## Future Test Coverage

Consider adding tests for:

- Bot commands (requires mocking Discord interactions)
- Button interactions (VoteView, ApprovalView)
- Daily question task scheduling
- Error handling and edge cases
- Integration tests with real Discord API (optional)

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
