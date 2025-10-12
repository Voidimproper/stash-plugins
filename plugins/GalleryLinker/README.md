# Gallery Linker Plugin

A Stash plugin that automatically links image galleries to related scenes and
performers based on file patterns, dates, and metadata.

> **Note**: This plugin is part of the Gallery Linker repository. For the complete project documentation, see the [main README](../../README.md).

## Features

- [TODO] **Auto-link by Date**: Links galleries to scenes with matching dates (within configurable tolerance)
- [TODO] **Auto-link by Filename**: Links galleries based on filename pattern matching
- **Performer Linking**: Automatically associates performers found in gallery filenames/paths
- [TODO] **Manual Linking**: UI for manual gallery-scene-performer associations
- **Batch Operations**: Process multiple galleries at once
- **Dry Run Mode**: Preview changes before applying them
- **Reporting**: Generate detailed linking statistics

## Installation

1. Copy the plugin files to your Stash plugins directory:
   - `gallery_linker.yml`
   - `gallery_linker.py`
   - `gallery_linker.js`

2. Install required Python dependencies:

   ```bash
   pip install stashapp-tools requests
   ```

3. Restart Stash to load the plugin

4. Enable the plugin in Settings > Plugins

## Configuration

The plugin provides several configuration options:

- **Auto-link by Date**: Enable automatic linking based on date matching
- **Date Tolerance**: Number of days tolerance for date matching (default: 7)
- **Auto-link by Filename**: Enable filename pattern matching
- **Link Performers**: Automatically link performers from file paths
- **Debug Tracing**: Enable detailed logging for troubleshooting
- **Dry Run Mode**: Preview changes without applying them

## Usage

### Plugin Tasks

The plugin provides several tasks accessible from the Tasks tab:

1. **Auto-Link Galleries to Scenes**: Automatically links galleries to scenes based on dates and filenames
2. **Auto-Link Performers to Galleries**: Links performers to galleries based on file path analysis
3. **Generate Linking Report**: Creates a report showing linking statistics
4. [TODO] **Validate Existing Links**: Checks existing gallery relationships
5. [TODO] **Clean Orphaned Relationships**: Removes broken links

### UI Interface

When viewing the Galleries page, a floating UI panel provides quick access to common operations:

- Auto-Link Scenes button
- Link Performers button
- Generate Report button

### Linking Logic

**Scene Matching**: Galleries are matched to scenes using:

- Title similarity (70%+ confidence)
- [TODO] Date matching (within configured tolerance)
- [TODO] Filename pattern matching
- [TODO] Performer overlap analysis

**Performer Matching**: Performers are linked by:

- Exact name matches in file paths
- Partial name matches (first/last names)
- Directory structure analysis

## API Integration

The plugin uses Stash's GraphQL API for:

- Querying galleries, scenes, and performers
- Creating and updating relationships
- Bulk operations for efficient processing

## Testing

To test the plugin:

1. Set up a test Stash instance with sample data
2. Enable "Dry Run Mode" in plugin settings
3. Run auto-linking tasks to preview results
4. Review logs for matching accuracy
5. Disable dry run and execute actual linking

## Troubleshooting

- Enable "Debug Tracing" for detailed logs
- Check Python dependencies are installed
- Verify Stash API access and permissions
- Review file path patterns for performer detection

## Example Use Cases

- **Studio Content**: Link gallery photos to corresponding scenes
- **Performer Galleries**: Associate performer image sets with their scenes
- **Event Documentation**: Link behind-the-scenes galleries to productions
- **Metadata Cleanup**: Establish missing relationships in existing libraries

## Contributing

Contributions welcome! Please ensure:

- Code follows existing patterns
- New features include appropriate tests
- Documentation is updated for changes
- Error handling is comprehensive

## License

This plugin is provided under the same license as the Stash project.
