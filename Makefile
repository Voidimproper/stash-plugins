# Makefile for Stash plugin testing

# Python executable
PYTHON := python3

# Test directories
TEST_DIR := tests
PLUGIN_DIR := plugins
COVERAGE_DIR := $(TEST_DIR)/htmlcov

# Virtual environment
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

.PHONY: help install test test-unit test-integration test-coverage clean lint format setup-venv

help:
	@echo "Available targets:"
	@echo "  setup-venv       - Create virtual environment and install dependencies"
	@echo "  install          - Install dev dependencies (using pyproject.toml)"
	@echo "  install-test     - Install test dependencies only"
	@echo "  install-requirements - Install from requirements.txt (fallback)"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-verbose     - Run tests with verbose output"
	@echo "  lint             - Run code linting"
	@echo "  format           - Format code with black"
	@echo "  format-check     - Check code formatting"
	@echo "  pre-commit       - Run pre-commit hooks"
	@echo "  clean            - Clean up generated files"

# Set up virtual environment
setup-venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r $(TEST_DIR)/requirements.txt

# Install dependencies (using pyproject.toml)
install:
	pip install -e ".[dev]"

# Install only test dependencies
install-test:
	pip install -e ".[test]"

# Install from requirements.txt (fallback)
install-requirements:
	pip install -r $(TEST_DIR)/requirements.txt

# Run all tests
test:
	pytest $(TEST_DIR) -v

# Run unit tests only
test-unit:
	pytest $(TEST_DIR) -v -m unit

# Run integration tests only
test-integration:
	pytest $(TEST_DIR) -v -m integration

# Run tests with coverage
test-coverage:
	pytest $(TEST_DIR) --cov=$(PLUGIN_DIR) --cov-report=html --cov-report=term-missing

# Run tests with verbose output
test-verbose:
	pytest $(TEST_DIR) -vvv --tb=long

# Run specific test file
test-gallery:
	pytest $(TEST_DIR)/plugins/GalleryLinker/test_gallery_linker.py -v

# Lint code
lint:
	flake8 $(PLUGIN_DIR) $(TEST_DIR) --max-line-length=120 --ignore=E203,W503
	mypy $(PLUGIN_DIR) --ignore-missing-imports

# Format code
format:
	black $(PLUGIN_DIR) $(TEST_DIR) --line-length=120

# Check code formatting
format-check:
	black $(PLUGIN_DIR) $(TEST_DIR) --line-length=120 --check --diff

# Clean up generated files
clean:
	rm -rf $(COVERAGE_DIR)
	rm -rf $(TEST_DIR)/coverage.xml
	rm -rf $(TEST_DIR)/.coverage
	rm -rf $(TEST_DIR)/.pytest_cache
	rm -rf $(PLUGIN_DIR)/__pycache__
	rm -rf $(TEST_DIR)/__pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Run tests in parallel
test-parallel:
	pytest $(TEST_DIR) -n auto

# Run tests with failure reporting
test-report:
	pytest $(TEST_DIR) --junit-xml=$(TEST_DIR)/test-results.xml

# Continuous testing (watch for changes)
test-watch:
	pytest-watch $(TEST_DIR) $(PLUGIN_DIR)

# Performance profiling
test-profile:
	pytest $(TEST_DIR) --profile --profile-svg

# Run tests for specific plugin
test-plugin:
	@if [ -z "$(PLUGIN)" ]; then \
		echo "Usage: make test-plugin PLUGIN=PluginName"; \
		exit 1; \
	fi
	pytest $(TEST_DIR)/plugins/$(PLUGIN) -v

# Install development tools
install-dev: install
	pip install pytest-watch pytest-profiling

# Validate test configuration
validate:
	pytest --collect-only $(TEST_DIR)

# Show test coverage in browser
show-coverage: test-coverage
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(COVERAGE_DIR)/index.html; \
	elif command -v open > /dev/null; then \
		open $(COVERAGE_DIR)/index.html; \
	else \
		echo "Coverage report generated at $(COVERAGE_DIR)/index.html"; \
	fi

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Sort imports
sort-imports:
	isort $(PLUGIN_DIR) $(TEST_DIR)

# Build package
build:
	python -m build

# Install package in development mode
install-dev-mode:
	pip install -e .

# Run ruff linting (alternative to flake8)
ruff:
	ruff check $(PLUGIN_DIR) $(TEST_DIR)

# Fix with ruff
ruff-fix:
	ruff check --fix $(PLUGIN_DIR) $(TEST_DIR)

# Type check with pyright
pyright:
	pyright $(PLUGIN_DIR)