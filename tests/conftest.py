#!/usr/bin/env python3

"""
Pytest configuration and shared fixtures for Stash plugin tests
"""

import pytest
import sys
import logging
from pathlib import Path
from unittest.mock import patch

# Add the plugins directory to the path
# plugins_dir = Path(__file__).parent.parent / "test_plugins"
# sys.path.insert(0, str(plugins_dir))

# Import test data
from tests.fixtures.test_data import TestData, MockStashInterface


@pytest.fixture
def mock_stash_interface():
    """Fixture providing a mock StashInterface"""
    return MockStashInterface()


@pytest.fixture
def sample_galleries():
    """Fixture providing sample gallery data"""
    return TestData.get_sample_galleries()


@pytest.fixture
def sample_scenes():
    """Fixture providing sample scene data"""
    return TestData.get_sample_scenes()


@pytest.fixture
def sample_performers():
    """Fixture providing sample performer data"""
    return TestData.get_sample_performers()


@pytest.fixture
def sample_studios():
    """Fixture providing sample studio data"""
    return TestData.get_sample_studios()


@pytest.fixture
def sample_tags():
    """Fixture providing sample tag data"""
    return TestData.get_sample_tags()


@pytest.fixture
def plugin_input_basic():
    """Fixture providing basic plugin input data"""
    return TestData.get_plugin_input_samples()['basic_plugin_input']


@pytest.fixture
def plugin_input_debug():
    """Fixture providing debug plugin input data"""
    return TestData.get_plugin_input_samples()['debug_plugin_input']


@pytest.fixture
def file_path_samples():
    """Fixture providing sample file paths"""
    return TestData.get_file_path_samples()


@pytest.fixture
def expected_matches():
    """Fixture providing expected match results"""
    return TestData.get_expected_matches()


@pytest.fixture
def mock_stash_interface_patch():
    """Fixture that patches StashInterface globally"""
    with patch('stashapi.stashapp.StashInterface') as mock_class:
        mock_instance = MockStashInterface()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def gallery_linker_with_mock():
    """Fixture providing GalleryLinker with mocked StashInterface"""
    # Add specific plugin path for import
    gallery_plugin_path = Path(__file__).parent.parent / "plugins" / "GalleryLinker"
    if str(gallery_plugin_path) not in sys.path:
        sys.path.insert(0, str(gallery_plugin_path))

    with patch('gallery_linker.StashInterface') as mock_stash_class:
        mock_stash_instance = MockStashInterface()
        mock_stash_class.return_value = mock_stash_instance

        # Import here to avoid circular imports
        try:
            from plugins.GalleryLinker import GalleryLinker
        except ImportError:
            # Fallback import method
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "gallery_linker",
                gallery_plugin_path / "gallery_linker.py"
            )
            gallery_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gallery_module)
            GalleryLinker = gallery_module.GalleryLinker

        linker = GalleryLinker()
        linker.stash = mock_stash_instance

        yield linker, mock_stash_instance


@pytest.fixture
def temp_logger():
    """Fixture providing a temporary logger for testing"""
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers.clear()

    # Add a test handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    yield logger

    # Clean up
    logger.handlers.clear()


@pytest.fixture(scope="session")
def test_config():
    """Session-scoped fixture providing test configuration"""
    return {
        'stash_url': 'http://localhost:9999',
        'api_key': 'test_api_key',
        'timeout': 30,
        'debug': True
    }


# Test configuration hooks
def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Set up logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Disable external network calls during testing
    try:
        import requests
        import urllib3
        urllib3.disable_warnings()
    except ImportError:
        pass


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    for item in items:
        # Mark tests based on their location or name
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath) or "test_" in item.name:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "slow" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)


# Custom pytest markers
pytest_plugins = []