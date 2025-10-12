# Project Brief

## Core Mission

Create and maintain a template repository for developing and distributing Stash media management system plugins with automated building and deployment.

## Project Goals

1. **Plugin Development Environment**: Provide a structured template for creating Stash plugins with proper organization, build tools, and quality checks
2. **Automated Distribution**: Build and deploy plugin repositories to GitHub Pages with automatic index generation and checksums
3. **Developer Experience**: Streamline plugin development with pre-configured tooling, testing, and CI/CD workflows
4. **Community Standards**: Follow established patterns from CommunityScripts and official Stash documentation

## Key Requirements

- Support Python 3.12+ (updated from multi-version to focus on latest)
- Automated plugin packaging into .zip files with metadata
- Generate plugin source index (index.yml) for Stash Plugin Manager
- Quality assurance through linting, formatting, and testing
- GitHub Actions for continuous integration and deployment
- Plugin isolation with individual requirements and configurations

## Success Criteria

- Developers can easily create new Stash plugins using this template
- Plugins are automatically built, tested, and deployed when committed
- Generated plugin repositories work seamlessly with Stash Plugin Manager
- Code quality is maintained through automated checks
- Documentation is clear and comprehensive

## Scope

- **In Scope**: Plugin template structure, build system, CI/CD, documentation, example plugins
- **Out of Scope**: Individual plugin functionality (that's for plugin developers), Stash core modifications, plugin hosting beyond GitHub Pages

## Current Focus

The repository currently contains a GalleryLinker plugin as an example implementation, demonstrating the full plugin development workflow from creation to deployment. This plugin links image galleries to related scenes and performers based on file patterns, dates, and metadata.
