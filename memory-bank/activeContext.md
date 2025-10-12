# Active Context

## Current Work Focus

### Primary Activity

Working with the **GalleryLinker** plugin as the main example implementation that demonstrates the full plugin development workflow. This plugin serves as both a functional tool and a template for future plugin development.

### Recent Development

- GalleryLinker plugin implementation in `plugins/GalleryLinker/`
- Notebook-based development workflow (`notebooks/gallery_linker.ipynb`)
- Plugin structure following established patterns from CommunityScripts
- Memory bank documentation system being established

### Current State

- Repository has mature build system with `build_site.sh`
- Quality assurance tools fully configured (Black, Flake8, MyPy, etc.)
- GitHub Actions CI/CD pipeline operational
- VS Code workspace configuration complete
- Python 3.12+ focused development environment
- Memory bank documentation system being initialized

## Next Steps

### Immediate Priorities

1. **Complete Memory Bank Setup**: Finalize documentation for consistent development experience
2. **GalleryLinker Refinement**: Ensure plugin demonstrates best practices
3. **Testing Framework**: Validate plugin functionality and build process
4. **Documentation Review**: Ensure README and CLAUDE.md are comprehensive

### Development Focus Areas

- Plugin template refinement based on GalleryLinker learnings
- Integration testing with actual Stash instances
- Community pattern alignment with CommunityScripts repository

## Active Decisions and Considerations

### Plugin Development Patterns

- **Notebook-first Development**: Using Jupyter notebooks for prototyping before formal plugin implementation
- **Shared Utilities**: `void_common` package for cross-plugin functionality
- **Configuration Management**: YAML-based plugin configuration with settings and tasks
- **UI Integration**: JavaScript components for enhanced user experience

### Technical Choices Under Review

- **Dependency Management**: Balance between shared dependencies and plugin isolation
- **Testing Strategy**: Local testing vs integration testing with Stash
- **Documentation Format**: README standards and inline documentation practices
- **Python Version Strategy**: Focused on 3.12+ for simplified development

## Important Patterns and Preferences

### Code Organization

```
plugins/PluginName/
├── __init__.py              # Package marker
├── plugin_name.py           # Main implementation (underscore naming)
├── plugin_name.yml          # Configuration (matches Python file)
├── plugin_name.js           # Optional UI components
├── requirements.txt         # Plugin-specific dependencies
├── README.md               # Documentation
└── additional modules       # As needed (datatypes.py, util.py, etc.)
```

### Development Workflow

1. **Prototype in Notebook**: Use `notebooks/` for initial development and testing
2. **Formalize as Plugin**: Move working code to proper plugin structure
3. **Configure Metadata**: Define settings, tasks, and execution in YAML
4. **Test Locally**: Validate with local Stash instance
5. **Quality Check**: Ensure passes all pre-commit hooks and CI

### Naming Conventions

- **Files**: snake_case for Python files and modules
- **Classes**: PascalCase for main plugin classes
- **Directories**: PascalCase for plugin directory names
- **YAML**: Matches Python filename (plugin_name.yml for plugin_name.py)

## Learnings and Project Insights

### Plugin Development Insights

- **StashInterface Usage**: Central pattern for all Stash API interactions
- **Configuration Flexibility**: YAML settings enable user customization without code changes
- **Task-based Architecture**: Multiple tasks per plugin enable diverse functionality
- **UI Enhancement**: JavaScript components improve user experience significantly

### Build System Learnings

- **Automation Benefits**: `build_site.sh` eliminates manual packaging errors
- **Index Generation**: Automatic checksum and metadata generation ensures compatibility
- **GitHub Pages Integration**: Seamless deployment without additional infrastructure

### Quality Assurance Discoveries

- **Pre-commit Value**: Catches issues before CI, improving development speed
- **Python 3.12 Focus**: Simplifies development and leverages latest features
- **Black + isort Integration**: Eliminates formatting discussions and inconsistencies

## Community Integration

### Reference Repositories

- **CommunityScripts**: `/Users/dank/git/voidimproper/gh-stashapp/CommunityScripts/` - Primary reference for patterns
- **Plugin Template**: `/Users/dank/git/voidimproper/gh-stashapp/plugins-repo-template/` - Official template structure
- **Stash Docs**: `/Users/dank/git/voidimproper/gh-stashapp/Stash-Docs/` - Documentation source

### Community Standards Alignment

- Following established plugin patterns from CommunityScripts
- Using standard dependency stack (stashapp-tools, requests)
- Implementing common plugin features (settings, tasks, dry-run modes)

## Current Challenges

### Technical Challenges

- **Dependency Conflicts**: Managing plugin-specific requirements without conflicts
- **Testing Complexity**: Validating plugins without full Stash environment setup
- **Documentation Maintenance**: Keeping examples and guides current with changes

### Process Challenges

- **Template Maintenance**: Ensuring new plugins follow established patterns
- **Community Feedback**: Incorporating suggestions while maintaining consistency
- **Version Management**: Coordinating plugin versions with template updates

## GalleryLinker Specific Context

### Plugin Functionality

- **Auto-linking**: Galleries to scenes by date and filename patterns
- **Performer Linking**: Automatic performer association based on file paths
- **Report Generation**: Comprehensive relationship reporting
- **UI Features**: JavaScript components for enhanced interface

### Configuration Options

- `autoLinkByDate`: Boolean setting for date-based linking
- `dateTolerance`: Number setting for date matching tolerance
- `autoLinkByFilename`: Boolean for filename pattern matching
- `performerLinking`: Boolean for automatic performer association
- `debugTracing`: Boolean for troubleshooting output
- `dryRun`: Boolean for safe preview mode

### Development Status

- Core functionality implemented in `gallery_linker.py`
- YAML configuration complete with comprehensive settings
- UI integration via `gallery_linker.js`
- Notebook prototyping in `notebooks/gallery_linker.ipynb`
- Documentation and testing in progress

## Memory Bank Usage

This is the initial memory bank setup, establishing the foundation for all future development work. The memory bank follows the hierarchical structure defined in .clinerules, ensuring consistent context preservation across development sessions.
