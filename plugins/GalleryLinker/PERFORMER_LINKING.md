# Performer Gallery Linking

This document describes the performer-to-gallery linking functionality in the Gallery Linker plugin.

## Overview

The performer-gallery linker automatically associates performers with galleries based on multiple strategies, ensuring
galleries are properly tagged with the performers they feature.

## Features

### Automatic Performer Detection

The linker uses three complementary strategies to find performers for galleries:

1. **Name Parsing**: Extracts performer names from gallery titles and folder paths
   - Supports performer names and aliases
   - Uses fuzzy matching with configurable threshold (default: 0.7)
   - Searches both title and parent directory names

2. **Scene-Based Linking**: Retrieves performers from scenes already linked to the gallery
   - Highest confidence matches (score: 1.0)
   - Automatically propagates performer relationships from scenes to galleries

3. **StashDB Integration** (Coming Soon): Queries StashDB for performer information
   - Placeholder implementation ready for StashDB API integration
   - Will provide additional performer discovery options

### Performer Creation

When enabled, the linker can create missing performers:

- Automatically creates performers not found in the database
- Tags new performers with "Gallery Linker: New Performer" for easy review
- Supports fuzzy search before creating to avoid duplicates

### Configuration

The performer linking can be configured through plugin settings:

- **create_missing**: Create performers that don't exist (default: True)
- **use_stashdb**: Query StashDB for performer information (default: False)
- **dry_run**: Preview changes without applying them (default: False)

## Usage

### Via Stash Plugin Manager

1. Install the Gallery Linker plugin
2. Navigate to Settings > Plugins > Gallery Linker
3. Click "Auto-Link Performers to Galleries" task
4. Monitor the plugin log for results

### Via Command Line

```bash
python gallery_linker.py --mode auto_link_performers --dry-run
```

### Programmatic Usage

```python
from GalleryLinker.gallery_linker import GalleryLinker

linker = GalleryLinker()
results = linker.auto_link_performers(
    create_missing=True,
    use_stashdb=False,
    dry_run=False
)

print(f"Linked: {len(results['linked'])}")
print(f"Created: {len(results['created'])}")
print(f"Errors: {len(results['errors'])}")
print(f"Skipped: {len(results['skipped'])}")
```

## Match Scoring

The linker uses a scoring system to determine match confidence:

- **1.0**: Exact match from linked scene
- **0.7-1.0**: Strong name/alias match from title or path
- **< 0.7**: Rejected (not linked)

## Example Scenarios

### Scenario 1: Gallery with Scene Link

```shell
Gallery: "Beach Photoshoot 2024"
Linked Scene: "Beach Scene" (performers: Jane Doe, John Smith)
Result: Jane Doe and John Smith linked to gallery (score: 1.0 each)
```

### Scenario 2: Gallery Name Parsing

```shell
Gallery: "Jane Doe Summer Collection"
Database: Performer "Jane Doe" exists
Result: Jane Doe linked to gallery (score: 1.0)
```

### Scenario 3: Folder Name Detection

```shell
Gallery Path: "/media/galleries/Jane_Doe/beach-set/image001.jpg"
Database: Performer "Jane Doe" exists
Result: Jane Doe linked to gallery (score: 1.0)
```

### Scenario 4: Missing Performer Creation

```shell
Gallery: "Emily Rose Vacation Photos"
Database: No performer "Emily Rose" found
Result: New performer "Emily Rose" created and linked with tag "Gallery Linker: New Performer"
```

## Results

The linking operation returns a detailed result dictionary:

```python
{
    "linked": [
        {
            "gallery_id": "123",
            "gallery_title": "Beach Photoshoot",
            "gallery_path": "/media/galleries/beach.zip",
            "performer_id": "456",
            "performer_name": "Jane Doe",
            "match_score": 1.0,
            "match_source": "linked_scene",
            "dry_run": False
        }
    ],
    "created": [],
    "errors": [],
    "skipped": [
        {
            "gallery_id": "789",
            "gallery_title": "Landscape Photos",
            "reason": "No new performers found to link"
        }
    ]
}
```

## Best Practices

1. **Run in Dry Run Mode First**: Test the linking logic before applying changes
2. **Review New Performers**: Check the "Gallery Linker: New Performer" tag regularly
3. **Link Scenes First**: Run scene-gallery linking before performer linking for best results
4. **Clean Gallery Names**: Use clear, descriptive gallery names for better matching
5. **Maintain Performer Database**: Keep performer names and aliases up to date

## Troubleshooting

### No Performers Linked

- Verify performers exist in the database
- Check gallery titles and paths contain performer names
- Enable debug logging to see matching details
- Try linking related scenes first

### Too Many False Positives

- Lower the match score threshold in code (default: 0.7)
- Improve gallery naming conventions
- Use more specific performer names

### Missing Performers

- Enable `create_missing` option
- Review and merge performers with "Gallery Linker: New Performer" tag
- Update performer aliases for better matching

## Technical Details

### Module: `performer_gallery_linker.py`

Main class: `PerformerGalleryLinker`

Key methods:

- `link_performers_to_galleries()`: Main linking method
- `_find_performers_from_names()`: Name-based matching
- `_get_performers_from_linked_scenes()`: Scene-based matching
- `_find_performers_from_stashdb()`: StashDB integration (TODO)
- `_create_performer_with_tag()`: New performer creation

### Integration

The performer linker integrates with the main Gallery Linker plugin through:

- `gallery_linker.py`: Main plugin entry point
- `auto_link_performers()` method in `GalleryLinker` class

## Future Enhancements

- [ ] Complete StashDB GraphQL integration
- [ ] Fuzzy search with Levenshtein distance
- [ ] Machine learning-based matching
- [ ] Batch performer creation review UI
- [ ] Custom match score thresholds per gallery
- [ ] Performance optimizations for large libraries

## Contributing

Contributions are welcome! Areas for improvement:

1. StashDB API integration
2. Enhanced matching algorithms
3. Additional performer metadata support
4. Performance optimizations
5. Testing and validation

See the main README for contribution guidelines.
