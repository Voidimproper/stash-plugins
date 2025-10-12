# Technical Context

## Core Technologies

### Python Ecosystem

- **Version**: Python 3.12+ (focused on latest, per pyproject.toml)
- **Package Manager**: pip with setuptools/pyproject.toml
- **Dependency Management**: requirements.txt per plugin + dev requirements

### Key Dependencies

- **stashapp-tools**: Primary dependency for Stash API interaction (>=0.2.0)
- **requests**: HTTP client for external API calls (>=2.28.0)
- **StashInterface**: From `stashapi.stashapp` for Stash connectivity

### Development Tools

- **Black**: Code formatting (120 character line length, Python 3.12 target)
- **Flake8**: Linting with specific ignores (E203, W503)
- **MyPy**: Type checking with ignore-missing-imports
- **isort**: Import sorting with black profile
- **pytest**: Testing framework
- **pre-commit**: Git hook management (v4.3.0+)
- **JupyterLab**: Notebook development environment (v4.4.7+)

### Alternative Tools (Available)

- **Pyright**: Alternative type checker with Python 3.12 support
- **Ruff**: Fast linter and formatter alternative (configured for py38+ compatibility)
- **Bandit**: Security analysis tool (excludes tests, skips B101/B601)

## Development Setup

### Initial Environment Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Configure pre-commit hooks
make install-hooks
# or
pre-commit install
```

### VS Code Integration

- **Workspace**: `stash-plugins.code-workspace` provides IDE configuration
- **Extensions**: Python, pre-commit support
- **Settings**: Line length 120, Black formatting, isort integration

### Docker Support

- `docker-compose.yml` available for containerized development
- GraphQL configuration in `graphql.config.yml`

## Code Quality Configuration

### Formatting Standards

```toml
[tool.black]
line-length = 120
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 120
known_first_party = ["plugins"]
known_third_party = ["stashapi", "requests", "stashapp-tools"]
```

### Linting Configuration

```ini
[flake8]
max-line-length = 120
ignore = E203, W503  # Black compatibility
```

### Type Checking

```toml
[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
disallow_untyped_defs = false  # Relaxed for plugin development
```

## Build and Deployment

### Build System

- **Script**: `build_site.sh` (bash script)
- **Output**: `_site/` directory with plugin packages and index
- **Format**: ZIP files + YAML index compatible with Stash Plugin Manager

### CI/CD Pipeline (GitHub Actions)

```yaml
# Triggered on: push/PR to main/develop branches
jobs:
  - testing (Python 3.12 focused)
  - code quality checks (black, isort, flake8, mypy, ruff, bandit)
  - pre-commit hook validation
  - build validation (main branch only)
  - automatic deployment to GitHub Pages
```

### Deployment Target

- **Platform**: GitHub Pages
- **URL Format**: `https://<username>.github.io/<repo-name>/main/index.yml`
- **Trigger**: Successful build on main branch

## Plugin Development Patterns

### Plugin Structure Requirements

```python
# plugin_name.py - Main implementation
from stashapi.stashapp import StashInterface

class PluginName:
    def __init__(self):
        self.stash = StashInterface()

    def execute_task(self, task_name, args):
        # Implementation using StashInterface
        pass
```

### Configuration Pattern

```yaml
# plugin_name.yml - Plugin metadata
name: "Plugin Name"
description: "Plugin description"
version: "1.0.0"
ui:
  javascript:
    - plugin_name.js  # Optional UI components
settings:
  - id: "setting_name"
    displayName: "Setting Display Name"
    description: "Setting description"
    type: "BOOLEAN"  # or NUMBER, STRING, etc.
tasks:
  - name: "task_name"
    description: "Task description"
    defaultArgs:
      mode: "default_mode"
exec:
  - python
  - "{pluginDir}/plugin_name.py"
interface: "raw"
```

## Technical Constraints

### Python Version Support

- Focused on Python 3.12+ (updated from multi-version approach)
- Leverages modern Python features and performance improvements
- Simplifies development and testing matrix

### Stash Integration Requirements

- Must use StashInterface for API communication
- GraphQL queries through established patterns
- Handle authentication and connectivity gracefully

### Performance Considerations

- Plugin loading should be fast
- Large operations should provide progress feedback
- Memory usage should be reasonable for typical Stash environments

## Tool Usage Patterns

### Make Commands

```bash
make format     # Black formatting
make lint       # Flake8 + MyPy
make test       # pytest
make pre-commit # Run all pre-commit hooks
make pyright    # Alternative type checking
make ruff       # Alternative linting
make ruff-fix   # Auto-fix with ruff
```

### Pre-commit Integration

- Runs automatically on git commit
- Enforces formatting and basic quality checks
- Prevents commits that would fail CI
- Configured hooks: trailing-whitespace, end-of-file-fixer, check-yaml, etc.

### Testing Framework

- **Framework**: pytest
- **Structure**: `tests/` directory
- **Coverage**: Available via `make test-coverage`
- **Plugin-specific**: `make test-plugin PLUGIN=PluginName`

## Documentation Tools

### Sphinx Integration

- **Project**: "Stash Plugins"
- **Extensions**: autodoc, viewcode, napoleon, myst_parser
- **Theme**: sphinx_rtd_theme
- **Format**: Support for both RST and Markdown via MyST

### Code Generation

- **GraphQL**: `datamodel-code-generator` for Stash API models
- **Target**: `plugins/void_common/stash_gql` package
- **Source**: Local Stash GraphQL endpoint (localhost:9999)

## Development Dependencies

### Core Dev Tools

```python
# Code quality
"black>=23.0.0"
"flake8>=6.0.0"
"isort>=5.12.0"
"mypy>=1.0.0"
"pre-commit>=4.3.0"

# Development environment
"jupyterlab>=4.4.7"

# Documentation
"sphinx>=5.0.0"
"sphinx-rtd-theme>=1.0.0"
"myst-parser>=0.18.0"

# Code generation
"datamodel-code-generator[http,graphql]>=0.33.0"
"gql[all]>=4.0.0"
```

### Optional Dependency Groups

- **lint**: Minimal linting tools
- **docs**: Documentation building tools
- **dev**: Complete development environment

## Community Integration Standards

- **stashapp-tools**: Standard dependency for all plugins
- **Plugin patterns**: Follow CommunityScripts examples
- **API usage**: Standard GraphQL patterns via StashInterface
- **Configuration**: YAML-based settings and task definitions
