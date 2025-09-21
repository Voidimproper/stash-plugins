# Stash Plugin Tests

This directory contains comprehensive unit tests for Stash plugins.

## Structure

```bash
tests/
├── __init__.py                    # Tests package
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                     # Pytest settings
├── requirements.txt               # Test dependencies
├── Makefile                       # Build automation
├── README.md                      # This file
├── fixtures/                      # Test data and fixtures
│   ├── __init__.py
│   └── test_data.py               # Sample data for testing
└── plugins/                       # Plugin-specific tests
    └── GalleryLinker/
        └── test_gallery_linker.py # GalleryLinker tests
```

## Setup

### 1. Install Dependencies

```bash
# Option 1: Direct installation
pip install -r tests/requirements.txt

# Option 2: Using virtual environment
make setup-venv
source venv/bin/activate
```

### 2. Verify Installation

```bash
pytest --version
```

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific plugin tests
make test-plugin PLUGIN=GalleryLinker

# Run with verbose output
make test-verbose
```

### Test Categories

```bash
# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run tests in parallel
make test-parallel
```

### Advanced Options

```bash
# Run with profiling
make test-profile

# Watch for changes and re-run tests
make test-watch

# Generate XML report for CI
make test-report
```

## Test Organization

### Fixtures

Common test data is provided through pytest fixtures in `conftest.py`:

- `mock_stash_interface` - Mock StashInterface for testing
- `sample_galleries` - Sample gallery data
- `sample_scenes` - Sample scene data
- `sample_performers` - Sample performer data
- `plugin_input_basic` - Basic plugin input
- `plugin_input_debug` - Debug plugin input

### Test Data

The `fixtures/test_data.py` module contains:

- `TestData` - Static test data provider
- `MockStashInterface` - Mock implementation for testing
- Sample data for galleries, scenes, performers, studios, tags

### Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.network` - Tests requiring network access

## Writing Tests

### Example Test

```python
import pytest
from unittest.mock import patch

def test_gallery_linker_init(mock_stash_interface):
    """Test GalleryLinker initialization"""
    from GalleryLinker.gallery_linker import GalleryLinker

    linker = GalleryLinker()
    assert linker.stash is not None
    assert linker.settings == {}

@pytest.mark.unit
def test_similarity_calculation():
    """Test string similarity calculation"""
    from GalleryLinker.gallery_linker import GalleryLinker

    linker = GalleryLinker()
    assert linker.similarity("test", "test") == 1.0
    assert linker.similarity("hello", "world") < 0.5
```

### Best Practices

1. **Use descriptive test names** - Clearly describe what is being tested
2. **One assertion per test** - Keep tests focused and atomic
3. **Mock external dependencies** - Use mocks for StashInterface calls
4. **Test edge cases** - Include tests for error conditions and boundary values
5. **Use fixtures** - Leverage shared test data and setup

### Mocking Guidelines

```python
# Mock StashInterface methods
mock_stash.find_galleries.return_value = sample_galleries
mock_stash.find_scenes.return_value = sample_scenes

# Mock exceptions
mock_stash.update_gallery.side_effect = Exception("Update failed")

# Verify method calls
mock_stash.update_gallery.assert_called_once_with({'id': '1', 'scene_ids': ['2']})
```

## Coverage

### Generating Reports

```bash
# HTML coverage report
make test-coverage

# View in browser
make show-coverage
```

### Coverage Goals

- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Focus**: Critical business logic and error handling

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: make install

    - name: Run tests
      run: make test-coverage

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure plugins directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:/path/to/plugins"
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall requirements
   pip install -r tests/requirements.txt --force-reinstall
   ```

3. **Mock Issues**
   ```python
   # Ensure proper patching
   @patch('module.StashInterface')  # Use full import path
   ```

### Debug Mode

```bash
# Run with debug output
pytest tests/ -vvv --tb=long --capture=no
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add comprehensive test coverage for new features
3. Update fixtures with any new sample data needed
4. Run the full test suite before submitting
5. Include both positive and negative test cases

## License

Same as the main Stash project.