# Makefile for Stash plugins development

# Python executable
PYTHON := python3

# Directories
PLUGIN_DIR := plugins

# Virtual environment (using .venv to match existing structure)
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

.PHONY: help install lint format clean pre-commit build

help:
	@echo "Available targets:"
	@echo "  env              - Set up a virtual environment in .venv"
	@echo "  install          - Install dev dependencies (using pyproject.toml)"
	@echo "  lint             - Run code linting with flake8 and mypy"
	@echo "  format           - Format code with black"
	@echo "  format-check     - Check code formatting without making changes"
	@echo "  sort-imports     - Sort imports with isort"
	@echo "  pre-commit       - Run all pre-commit hooks"
	@echo "  install-hooks    - Install pre-commit hooks"
	@echo "  ruff             - Run ruff linting"
	@echo "  ruff-fix         - Fix issues with ruff"
	@echo "  build            - Build plugin repository with build_site.sh"
	@echo "  clean            - Clean up generated files"

# Set up virtual environment
env:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV) --prompt stash-plugins; \
		$(VENV_PIP) install --upgrade pip; \
		$(VENV_PIP) install -r requirements.txt; \
		echo "Virtual environment created in $(VENV)"; \
	else \
		echo "Virtual environment already exists in $(VENV)"; \
	fi
	@echo "To activate the virtual environment, run: source $(VENV_BIN)/activate"

# Install dependencies (using pyproject.toml)
install:
	pip install -e ".[dev]"

# Lint code
lint:
	flake8 $(PLUGIN_DIR) --max-line-length=120 --ignore=E203,W503
	mypy $(PLUGIN_DIR) --ignore-missing-imports

# Format code
format:
	black $(PLUGIN_DIR) --line-length=120

# Check code formatting
format-check:
	black $(PLUGIN_DIR) --line-length=120 --check --diff

# Sort imports
sort-imports:
	isort $(PLUGIN_DIR) --profile=black --line-length=120

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Run ruff linting
ruff:
	ruff check $(PLUGIN_DIR)

# Fix with ruff
ruff-fix:
	ruff check --fix $(PLUGIN_DIR)

# Build plugin repository
build:
	./build_site.sh

# Build to custom directory
build-to:
	@if [ -z "$(DIR)" ]; then \
		echo "Usage: make build-to DIR=output_directory"; \
		exit 1; \
	fi
	./build_site.sh $(DIR)

# Clean up generated files
clean:
	rm -rf _site
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Run a specific plugin script
run-plugin:
	@if [ -z "$(PLUGIN)" ]; then \
		echo "Usage: make run-plugin PLUGIN=PluginName [ARGS='--arg1 value1']"; \
		echo "Example: make run-plugin PLUGIN=GalleryLinker ARGS='--mode generate_report'"; \
		exit 1; \
	fi
	cd $(PLUGIN_DIR)/$(PLUGIN) && $(PYTHON) $(shell echo $(PLUGIN) | tr A-Z a-z | sed 's/$$/.py/') $(ARGS)

# Install package in development mode
install-dev-mode:
	pip install -e .
