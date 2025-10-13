# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Stash plugins repository that provides a template for creating and distributing plugins for the Stash media management system. The repository is structured to automatically build and deploy plugin source indexes to GitHub Pages.

## Key Development Commands

### Environment Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
make install-hooks
# or
pre-commit install
```

### Code Quality and Testing

```bash
# Format code
make format
# or
black plugins --line-length=120

# Lint code
make lint
# or
flake8 plugins --max-line-length=120 --ignore=E203,W503
mypy plugins --ignore-missing-imports

# Sort imports
isort plugins --profile=black --line-length=120

# Run all pre-commit hooks
make pre-commit
# or
pre-commit run --all-files

# Type checking alternatives
make pyright      # Using pyright
make ruff         # Using ruff linter
make ruff-fix     # Auto-fix with ruff
```

### Plugin Building and Deployment

```bash
# Build plugin repository (creates _site directory with index.yml and plugin zips)
./build_site.sh

# Build to custom directory
./build_site.sh custom_output_dir
```

## Architecture

### Plugin Structure

Each plugin is organized in its own directory under `plugins/`:

```
plugins/
├── __init__.py
└── PluginName/
    ├── __init__.py
    ├── plugin_name.py          # Main plugin implementation
    ├── plugin_name.yml         # Plugin metadata and configuration
    ├── requirements.txt        # Plugin-specific dependencies
    └── README.md              # Plugin documentation
```

### Plugin Configuration (*.yml files)

- **name**: Display name for the plugin
- **description**: Brief description of functionality
- **version**: Plugin version
- **settings**: User-configurable options with types (BOOLEAN, NUMBER, etc.)
- **tasks**: Available plugin operations with defaultArgs
- **exec**: How to execute the plugin (typically Python)
- **interface**: Interface type (usually "raw")

### Core Dependencies

- **stashapp-tools**: Main dependency for Stash API interaction
- **requests**: HTTP client library
- Plugins use `StashInterface` from `stashapi.stashapp` for Stash connectivity

### Build System

- Uses `build_site.sh` to create plugin repository with:
  - `index.yml`: Plugin source index with metadata, versions, and checksums
  - Individual `.zip` files for each plugin containing all plugin files
- GitHub Actions automatically build and deploy to GitHub Pages when plugins are modified

## Code Style Configuration

- **Line length**: 120 characters
- **Python versions**: 3.10, 3.11, 3.12
- **Formatter**: Black with line-length=120
- **Import sorting**: isort with black profile
- **Type checking**: MyPy with ignore-missing-imports
- **Linting**: Flake8 with specific ignores (E203, W503)

## Testing Framework

The repository uses pytest for testing:

```bash
# Run all tests
make test
# or
pytest tests -v

# Run specific plugin tests
make test-plugin PLUGIN=PluginName

# Run with coverage
make test-coverage
```

## Continuous Integration

GitHub Actions run on push/PR to main/develop branches:

- **Tests**: Multi-version Python testing (3.10, 3.11, 3.12)
- **Code Quality**: Black formatting, isort, flake8, mypy, ruff, bandit security checks
- **Pre-commit**: All pre-commit hooks validation
- **Build**: Package building and validation (on main branch only)
- **Deploy**: Automatic plugin repository deployment to GitHub Pages

## Reference Projects and Documentation

### Local Reference Repositories

For plugin development examples and documentation, refer to these local repositories in `${HOME}/git/voidimproper/gh-stashapp/`:

#### CommunityScripts (`${HOME}/git/voidimproper/gh-stashapp/CommunityScripts/`)

- **Purpose**: Official Stash community plugins, themes, userscripts, and utilities
- **Plugin examples**: Contains real-world plugin implementations in `plugins/` directory
- **Key plugins to study**:
  - `FileMonitor/`: Comprehensive plugin with scheduler, file monitoring, and UI
  - `DupFileManager/`: File management utilities
  - `CommunityScriptsUILibrary/`: UI components library
- **Source index**: `https://stashapp.github.io/CommunityScripts/stable/index.yml`
- **Installation**: Available via Stash Plugin Manager (Community stable source)

#### Plugin Template (`${HOME}/git/voidimproper/gh-stashapp/plugins-repo-template/`)

- **Purpose**: Official template for creating plugin repositories
- **Usage**: Use as reference for repository structure and GitHub Actions setup
- **Features**: Pre-configured build and deployment workflows

#### Stash Documentation (`${HOME}/git/voidimproper/gh-stashapp/Stash-Docs/`)

- **Purpose**: Official Stash documentation source
- **Website**: <https://docs.stashapp.cc>
- **Key sections**:
  - `docs/plugins/`: Plugin development guides
  - `docs/in-app-manual/plugins/`: Creating plugins documentation
  - `docs/api.md`: API documentation
- **Local development**: Use `mkdocs serve` to run documentation locally

#### Additional References

- **CommunityScrapers**: Scraper examples and templates
- **stash**: Main Stash application source code
- **stash-box**: StashDB source code
- **StashDB-Docs**: StashDB documentation

### Development Workflow

1. **Study existing plugins** in CommunityScripts for implementation patterns
2. **Reference official documentation** at docs.stashapp.cc for plugin creation guides
3. **Use plugin template** structure for new plugin repositories
4. **Test with community plugins** to understand common patterns and best practices

### Community Resources

- **Forum**: <https://discourse.stashapp.cc> for support and discussions
- **Plugin sharing**: Create topics on forum and add to community source index list
- **Plugin manager**: Available in Stash Settings > Plugins for easy installation

## Important Notes

- Plugin source index URL format: `https://<username>.github.io/<repo-name>/main/index.yml`
- All plugins should handle Stash API authentication and connectivity through StashInterface
- Plugin tasks support different modes (e.g., auto_link_scenes, generate_report, etc.)
- Debug tracing and dry-run modes are commonly implemented for troubleshooting
- Follow patterns from CommunityScripts plugins for consistency with community standards
