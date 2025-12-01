.PHONY: test lint format clean install run

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=. --cov-report=term-missing --cov-report=html

# Run linting
lint:
	flake8 .
	black --check .

# Format code
format:
	black .

# Clean up generated files
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f coverage.xml
	rm -f test_*.db
	rm -f bandit-report.json
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the bot
run:
	python bot.py

# Run tests in watch mode (requires pytest-watch)
watch:
	ptw

# Show coverage report
coverage:
	pytest --cov=. --cov-report=html
	@echo "Opening coverage report..."
	@which open > /dev/null && open htmlcov/index.html || \
	which xdg-open > /dev/null && xdg-open htmlcov/index.html || \
	echo "Coverage report generated in htmlcov/index.html"
