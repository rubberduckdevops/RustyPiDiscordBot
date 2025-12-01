# Contributing to Would You Rather Discord Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/WYRDiscordBot.git
   cd WYRDiscordBot
   ```

3. **Set up your development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

4. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

Before submitting changes, make sure all tests pass:

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# View coverage report in browser
make coverage
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

### Writing Tests

- All new features should include tests
- Tests are located in `test_*.py` files
- We use `pytest` and `pytest-asyncio`
- Aim for good test coverage (>80%)

Example test:
```python
@pytest.mark.asyncio
async def test_my_feature(db):
    # Arrange
    user_id = 123456

    # Act
    result = await db.my_new_function(user_id)

    # Assert
    assert result is not None
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (max line length: 127)
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

## Pull Request Process

1. **Update tests** - Add or update tests for your changes
2. **Run tests locally** - Ensure all tests pass
3. **Format your code** - Run `make format`
4. **Update documentation** - Update README.md if needed
5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference any related issues
   - Describe what you changed and why
   - Include screenshots if applicable

### PR Requirements

- All tests must pass ✅
- Code must be formatted with Black ✅
- Linting checks must pass ✅
- Coverage should not decrease ✅

## Commit Message Guidelines

Good commit messages help understand the project history:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Examples:
```
Add user submission approval system

Fix streak calculation bug in database.py

Update README with daily questions setup
```

## Reporting Bugs

If you find a bug:

1. **Check existing issues** - It might already be reported
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)
   - Error messages or logs

## Feature Requests

We welcome feature suggestions! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly
3. **Explain the use case** - Why is it needed?
4. **Propose implementation** if you have ideas

## Questions?

Feel free to open an issue for questions about:
- Setting up the development environment
- Understanding the codebase
- Implementing a feature
- Anything else!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
