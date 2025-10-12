# Product Context

## Why This Project Exists

### Problem Statement

Stash plugin development was fragmented and difficult for new developers:

- No standardized template for creating plugin repositories
- Manual build processes prone to errors
- Inconsistent plugin distribution methods
- Complex setup for automated deployment
- Lack of integrated quality assurance tools

### Target Users

1. **Plugin Developers**: Individuals creating new Stash plugins who need a reliable foundation
2. **Community Contributors**: Developers extending existing plugins or creating specialized tools
3. **DevOps-minded Developers**: Those who want automated building, testing, and deployment

### Problems We Solve

- **Development Complexity**: Eliminates setup overhead with pre-configured tooling
- **Distribution Friction**: Automated plugin packaging and index generation
- **Quality Inconsistency**: Built-in linting, formatting, and testing standards
- **Deployment Manual Work**: GitHub Actions handle building and publishing automatically
- **Documentation Gaps**: Clear examples and comprehensive development guides

## How It Should Work

### Developer Experience Flow

1. **Clone/Fork**: Developer starts with this template repository
2. **Create Plugin**: Add new plugin directory under `plugins/` with proper structure
3. **Develop**: Write plugin code with IDE support, linting, and testing
4. **Commit**: Push changes trigger automated quality checks
5. **Deploy**: Successful builds automatically update plugin repository on GitHub Pages
6. **Distribute**: Users install via Stash Plugin Manager using generated index URL

### User Experience Goals

- **Zero-Config Start**: Template works immediately after cloning
- **IDE Integration**: Full VS Code workspace configuration
- **Quality Feedback**: Immediate feedback on code quality issues
- **Automated Publishing**: No manual deployment steps required
- **Standard Compliance**: Follows community patterns and best practices

### Key Interactions

- **Plugin Creation**: Structured directories with metadata files
- **Development**: Local testing with stash-tools integration
- **Quality Assurance**: Pre-commit hooks and CI validation
- **Distribution**: Automatic plugin source index updates
- **Installation**: Seamless integration with Stash Plugin Manager

## Integration Points

- **Stash Core**: Plugins interact via StashInterface API
- **Community Standards**: Follows CommunityScripts patterns
- **GitHub Ecosystem**: Uses Actions, Pages, and standard Git workflows
- **Python Ecosystem**: Leverages standard tools (Black, Flake8, MyPy, pytest)

## Example Plugin: GalleryLinker

The repository includes GalleryLinker as a reference implementation that:

- Links image galleries to related scenes and performers
- Uses file patterns, dates, and metadata for matching
- Demonstrates comprehensive plugin features (settings, tasks, UI integration)
- Shows best practices for Stash API interaction
- Includes debug tracing and dry-run modes
