# VoidImproper Stash Plugins

![Tests and Quality Checks](https://github.com/Voidimproper/stash-plugins/actions/workflows/test.yml/badge.svg)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A comprehensive template repository for developing and distributing **Stash media management system plugins**
with automated building, testing, and deployment workflows.

## 🚀 Features

- **🏗️ Complete Development Environment**: Pre-configured tooling for Python 3.12+ development
- **🔧 Quality Assurance**: Automated code formatting (Black), linting (Flake8), type checking (MyPy)
- **📦 Automated Building**: Generate plugin packages and source index automatically
- **🚀 GitHub Pages Deployment**: Automatic publishing to GitHub Pages for easy distribution
- **🧪 Testing Framework**: pytest configuration with coverage reporting
- **📚 Comprehensive Documentation**: Detailed guides and examples
- **🎯 Example Plugin**: GalleryLinker plugin demonstrating best practices

## 📋 Quick Start

### 1. Create Your Repository

1. Click **Use this template** > **Create a new repository**
2. Choose a repository name and click **Create repository**
3. Open **Settings** and head to **Pages**
4. Under Build and deployment select the Source as **GitHub Actions**

### 2. Set Up Development Environment

```bash
# Clone your new repository
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
make install-hooks
```

### 3. Start Developing

```bash
# Create a new plugin (manually for now)
mkdir -p plugins/YourPluginName
cd plugins/YourPluginName

# Create required files
touch __init__.py
touch your_plugin_name.py
touch your_plugin_name.yml
touch requirements.txt
touch README.md
```

## 🏗️ Repository Structure

```shell
stash-plugins/
├── plugins/                   # Plugin collection
│   ├── __init__.py            # Package marker
│   ├── GalleryLinker/         # Example plugin
│   └── void_common/           # Shared utilities
├── memory-bank/               # Project documentation
├── notebooks/                 # Development notebooks
├── scripts/                   # Build/utility scripts
├── build_site.sh              # Build script
└── pyproject.toml             # Project configuration
```

## 🔧 Plugin Development

### Plugin Structure

Each plugin follows this standardized structure:

```shell
plugins/PluginName/
├── __init__.py              # Package marker
├── plugin_name.py           # Main implementation
├── plugin_name.yml          # Plugin metadata and configuration
├── plugin_name.js           # Optional UI components
├── requirements.txt         # Plugin-specific dependencies
└── README.md               # Plugin documentation
```

### Example Plugin Configuration

```yaml
name: "Your Plugin Name"
description: "Brief description of functionality"
version: "1.0.0"
url: "https://github.com/your-username/your-repo"
ui:
  javascript:
    - plugin_name.js
settings:
  - id: "enable_feature"
    displayName: "Enable Feature"
    description: "Enable the main feature"
    type: "BOOLEAN"
tasks:
  - name: "Main Task"
    description: "Primary plugin operation"
    defaultArgs:
      mode: "default"
exec:
  - python
  - "{pluginDir}/plugin_name.py"
interface: "raw"
```

## 🧪 Development Workflow

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Run all quality checks
make pre-commit

# Run tests
make test
```

### Building and Deployment

```bash
# Build plugin repository locally
./build_site.sh

# Plugins are automatically built and deployed via GitHub Actions
# when changes are pushed to main/develop branches
```

## 📦 Installation and Distribution

### Plugin Source Index

Your plugins will be automatically published to:

```shell
https://<your-username>.github.io/<repository-name>/main/index.yml
```

### Installing Plugins

1. Open Stash and go to **Settings** > **Plugins**
2. Add your source index URL to plugin sources
3. Install plugins directly through the Stash Plugin Manager

### Sharing Your Plugins

- [Create a forum topic](https://discourse.stashapp.cc/t/-/33) for your plugin
- [Add your source to the community list](https://discourse.stashapp.cc/t/-/122)

## 📚 Example: GalleryLinker Plugin

This repository includes a comprehensive example plugin that demonstrates:

- **Auto-linking**: Galleries to scenes by date and filename patterns
- **Performer Linking**: Automatic performer association based on file paths
- **Report Generation**: Comprehensive relationship reporting
- **UI Integration**: JavaScript components for enhanced user experience
- **Configuration**: Multiple settings and task modes
- **Best Practices**: Debug tracing, dry-run modes, error handling

## 🌐 Community References

Learn from these excellent community plugin repositories:

### JavaScript-Focused Plugins

- [Valkyr-JS/PerformerDetailsExtended](https://github.com/Valkyr-JS/PerformerDetailsExtended)
- [Valkyr-JS/StashMergers](https://github.com/Valkyr-JS/StashMergers)
- [Valkyr-JS/StashReels](https://github.com/Valkyr-JS/StashReels)
- [Valkyr-JS/ValkyrSceneCards](https://github.com/Valkyr-JS/ValkyrSceneCards)

### Python-Focused Plugins

- [7dJx1qP/stash-plugins](https://github.com/7dJx1qP/stash-plugins)
- [Serechops/Serechops-Stash](https://github.com/Serechops/Serechops-Stash)
- [stg-annon/StashScripts](https://github.com/stg-annon/StashScripts)

### Tools and Utilities

- [W0lfieW0lf/StashApp-Tools](https://github.com/W0lfieW0lf/StashApp-Tools)
- [feederbox826/stashlist](https://github.com/feederbox826/stashlist)
- [tetrax-10/stash-stuffs](https://github.com/tetrax-10/stash-stuffs)

### Community Collections

- [rosa-umineko/CommunityScripts](https://github.com/rosa-umineko/CommunityScripts)
- [S3L3CT3DLoves/stashPlugins](https://github.com/S3L3CT3DLoves/stashPlugins)
- [carrotwaxr/stash-plugins](https://github.com/carrotwaxr/stash-plugins)

## 🛠️ Technical Specifications

### Requirements

- **Python**: 3.12+
- **Dependencies**: stashapp-tools, requests
- **Development**: Black, Flake8, MyPy, pytest, pre-commit

### Key Features

- **Multi-plugin repository** support
- **Automated CI/CD** via GitHub Actions
- **Quality assurance** with pre-commit hooks
- **Plugin isolation** with individual dependencies
- **Shared utilities** via `void_common` package
- **Notebook development** workflow support

### Build System

- Generates ZIP packages for each plugin
- Creates plugin source index with checksums
- Automatic deployment to GitHub Pages
- Compatible with Stash Plugin Manager

## 📖 Documentation

- **Plugin Creation Guide**: [docs.stashapp.cc](https://docs.stashapp.cc/in-app-manual/plugins/#creating-plugins)
- **Community Forum**: [discourse.stashapp.cc](https://discourse.stashapp.cc)
- **API Documentation**: Available in project documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the [AGPL-3.0 License](LICENCE). You can change the license before publishing your plugins.

## 🔗 Links

- **Stash Project**: [stashapp.cc](https://stashapp.cc)
- **Community Scripts**: [CommunityScripts Repository](https://github.com/stashapp/CommunityScripts)
- **Plugin Documentation**: [docs.stashapp.cc](https://docs.stashapp.cc)
- **Community Forum**: [discourse.stashapp.cc](https://discourse.stashapp.cc)

---

⭐ **Star this repository** if you find it helpful for your Stash plugin development!
