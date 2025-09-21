#!/usr/bin/env python3

"""
Unit tests for GalleryLinker plugin
"""

import unittest
import json
import sys
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint
import pytest

# root = pytest.Config.rootpath
# print(f"Root: {root}")

from plugins.GalleryLinker.gallery_linker import GalleryLinker


class TestGalleryLinker(unittest.TestCase):
    """Test cases for GalleryLinker class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_stash_interface = Mock()

        # Mock the StashInterface constructor
        self.stash_patcher = patch('gallery_linker.StashInterface')
        self.mock_stash_class = self.stash_patcher.start()
        self.mock_stash_class.return_value = self.mock_stash_interface

        self.linker = GalleryLinker)

        # Sample test data
        self.sample_gallery = {
            'id': '1',
            'title': 'Test Gallery',
            'date': '2023-01-15',
            'path': {'path': '/path/to/gallery/Test_Gallery_2023-01-15'},
            'performers': [{'id': '101', 'name': 'Performer One'}],
            'scenes': []
        }

        self.sample_scene = {
            'id': '2',
            'title': 'Test Scene',
            'date': '2023-01-15',
            'files': [{'path': '/path/to/scene/Test_Scene_2023-01-15.mp4'}],
            'performers': [{'id': '101', 'name': 'Performer One'}]
        }

        self.sample_performers = [
            {'id': '101', 'name': 'Performer One'},
            {'id': '102', 'name': 'Jane Doe'},
            {'id': '103', 'name': 'John Smith'}
        ]

    def tearDown(self):
        """Clean up after tests"""
        self.stash_patcher.stop()

    def test_init_default(self):
        """Test default initialization"""
        self.assertIsNotNone(self.linker.stash)
        self.assertEqual(self.linker.settings, {})
        self.assertIsInstance(self.linker.logger, logging.Logger)

    def test_init_with_url_and_api_key(self):
        """Test initialization with custom URL and API key"""
        with patch('gallery_linker.StashInterface') as mock_stash:
            linker = GalleryLinker("http://localhost:9999", "test_api_key")

            # Verify StashInterface was called with correct config
            call_args = mock_stash.call_args[0][0]
            self.assertEqual(call_args['scheme'], 'http')
            self.assertEqual(call_args['host'], 'localhost')
            self.assertEqual(call_args['port'], '9999')
            self.assertEqual(call_args['ApiKey'], 'test_api_key')

    def test_load_settings_with_server_connection(self):
        """Test loading settings with server connection"""
        plugin_input = {
            'server_connection': {
                'scheme': 'https',
                'host': 'example.com',
                'port': '443',
                'ApiKey': 'test_key'
            },
            'args': {
                'mode': 'auto_link_scenes',
                'debugTracing': True,
                'dateTolerance': 5
            }
        }

        with patch('gallery_linker.StashInterface') as mock_stash:
            self.linker.load_settings(plugin_input)

            # Verify new StashInterface was created with server connection
            mock_stash.assert_called_with(plugin_input['server_connection'])

            # Verify settings were loaded
            self.assertEqual(self.linker.settings['mode'], 'auto_link_scenes')
            self.assertEqual(self.linker.settings['dateTolerance'], 5)
            self.assertTrue(self.linker.settings['debugTracing'])

    def test_similarity(self):
        """Test string similarity calculation"""
        # Identical strings
        self.assertEqual(self.linker.similarity("test", "test"), 1.0)

        # Similar strings
        sim = self.linker.similarity("Test Gallery", "test gallery")
        self.assertGreater(sim, 0.8)

        # Different strings
        sim = self.linker.similarity("completely different", "nothing alike")
        self.assertLess(sim, 0.3)

    def test_extract_date_from_filename(self):
        """Test date extraction from filenames"""
        # YYYY-MM-DD format
        date = self.linker.extract_date_from_filename("gallery_2023-01-15_title.jpg")
        self.assertEqual(date, datetime(2023, 1, 15))

        # YYYY_MM_DD format
        date = self.linker.extract_date_from_filename("gallery_2023_01_15_title.jpg")
        self.assertEqual(date, datetime(2023, 1, 15))

        # YYYYMMDD format
        date = self.linker.extract_date_from_filename("gallery_20230115_title.jpg")
        self.assertEqual(date, datetime(2023, 1, 15))

        # No date in filename
        date = self.linker.extract_date_from_filename("gallery_title.jpg")
        self.assertIsNone(date)

    def test_extract_performers_from_path(self):
        """Test performer extraction from file paths"""
        path = "/storage/galleries/Performer One/2023/gallery_folder"
        performers = self.sample_performers

        found_ids = self.linker.extract_performers_from_path(path, performers)
        self.assertIn('101', found_ids)  # Should find 'Performer One'

        # Test with partial name match
        path = "/storage/galleries/Jane/special_gallery"
        found_ids = self.linker.extract_performers_from_path(path, performers)
        self.assertIn('102', found_ids)  # Should find 'Jane Doe' by first name

    def test_find_matching_scenes_high_similarity(self):
        """Test finding matching scenes with high similarity"""
        gallery = self.sample_gallery.copy()
        scenes = [self.sample_scene.copy()]

        matches = self.linker.find_matching_scenes(gallery, scenes)

        self.assertEqual(len(matches), 1)
        scene, score = matches[0]
        self.assertEqual(scene['id'], '2')
        self.assertGreater(score, 0.7)  # High confidence match

    def test_find_matching_scenes_no_matches(self):
        """Test finding matching scenes with no good matches"""
        gallery = {
            'id': '1',
            'title': 'Completely Different Gallery',
            'date': '2020-01-01',
            'path': {'path': '/different/path/gallery'},
            'performers': [],
            'scenes': []
        }
        scenes = [self.sample_scene.copy()]

        matches = self.linker.find_matching_scenes(gallery, scenes)
        self.assertEqual(len(matches), 0)  # No matches above threshold

    def test_find_matching_scenes_date_tolerance(self):
        """Test date matching with tolerance"""
        self.linker.settings = {'dateTolerance': 3}

        gallery = self.sample_gallery.copy()
        gallery['date'] = '2023-01-17'  # 2 days after scene date
        scenes = [self.sample_scene.copy()]

        matches = self.linker.find_matching_scenes(gallery, scenes)
        self.assertEqual(len(matches), 1)  # Should match within tolerance

        # Test outside tolerance
        gallery['date'] = '2023-01-20'  # 5 days after scene date
        matches = self.linker.find_matching_scenes(gallery, scenes)
        # May still match due to other factors, but date score should be lower

    @patch.object(GalleryLinker, 'find_matching_scenes')
    def test_auto_link_scenes_dry_run(self, mock_find_matching):
        """Test auto-link scenes in dry run mode"""
        self.linker.settings = {'dryRun': True}
        self.mock_stash_interface.find_galleries.return_value = [self.sample_gallery]
        self.mock_stash_interface.find_scenes.return_value = [self.sample_scene]

        # Mock a high-confidence match
        mock_find_matching.return_value = [(self.sample_scene, 0.9)]

        result = self.linker.auto_link_scenes()

        self.assertIn("DRY RUN", result['message'])
        self.assertEqual(result['linked_count'], 1)
        # Verify update_gallery was not called in dry run
        self.mock_stash_interface.update_gallery.assert_not_called()

    @patch.object(GalleryLinker, 'find_matching_scenes')
    def test_auto_link_scenes_actual_link(self, mock_find_matching):
        """Test auto-link scenes with actual linking"""
        self.linker.settings = {'dryRun': False}
        self.mock_stash_interface.find_galleries.return_value = [self.sample_gallery]
        self.mock_stash_interface.find_scenes.return_value = [self.sample_scene]

        # Mock a high-confidence match
        mock_find_matching.return_value = [(self.sample_scene, 0.9)]

        result = self.linker.auto_link_scenes()

        self.assertEqual(result['linked_count'], 1)
        # Verify update_gallery was called
        self.mock_stash_interface.update_gallery.assert_called_once()

        # Check the update call
        call_args = self.mock_stash_interface.update_gallery.call_args[0][0]
        self.assertEqual(call_args['id'], '1')
        self.assertIn('2', call_args['scene_ids'])

    def test_auto_link_scenes_skip_existing(self):
        """Test skipping galleries already linked to scenes"""
        gallery_with_scenes = self.sample_gallery.copy()
        gallery_with_scenes['scenes'] = [{'id': '99'}]

        self.linker.settings = {'overwriteExisting': False}
        self.mock_stash_interface.find_galleries.return_value = [gallery_with_scenes]
        self.mock_stash_interface.find_scenes.return_value = [self.sample_scene]

        result = self.linker.auto_link_scenes()

        self.assertEqual(result['linked_count'], 0)
        self.mock_stash_interface.update_gallery.assert_not_called()

    def test_auto_link_performers(self):
        """Test auto-linking performers to galleries"""
        gallery = {
            'id': '1',
            'path': {'path': '/storage/galleries/Performer One/gallery_folder'},
            'performers': []
        }

        self.linker.settings = {'dryRun': False}
        self.mock_stash_interface.find_galleries.return_value = [gallery]
        self.mock_stash_interface.find_performers.return_value = self.sample_performers

        result = self.linker.auto_link_performers()

        self.assertEqual(result['linked_count'], 1)
        self.mock_stash_interface.update_gallery.assert_called_once()

        # Check the update call
        call_args = self.mock_stash_interface.update_gallery.call_args[0][0]
        self.assertEqual(call_args['id'], '1')
        self.assertIn('101', call_args['performer_ids'])

    def test_generate_report(self):
        """Test generating gallery relationship report"""
        galleries = [
            {'id': '1', 'scenes': [{'id': '2'}], 'performers': []},  # Linked to scene
            {'id': '2', 'scenes': [], 'performers': [{'id': '101'}]},  # Linked to performer
            {'id': '3', 'scenes': [{'id': '3'}], 'performers': [{'id': '102'}]},  # Both
            {'id': '4', 'scenes': [], 'performers': []},  # Unlinked
        ]

        self.mock_stash_interface.find_galleries.return_value = galleries

        report = self.linker.generate_report()

        self.assertEqual(report['total_galleries'], 4)
        self.assertEqual(report['linked_to_scenes'], 2)
        self.assertEqual(report['linked_to_performers'], 2)
        self.assertEqual(report['unlinked'], 1)
        self.assertEqual(report['coverage_percentage'], 75.0)

    def test_no_galleries_found(self):
        """Test behavior when no galleries are found"""
        self.mock_stash_interface.find_galleries.return_value = []

        result = self.linker.auto_link_scenes()
        self.assertEqual(result['message'], "No galleries found")

    def test_no_scenes_found(self):
        """Test behavior when no scenes are found"""
        self.mock_stash_interface.find_galleries.return_value = [self.sample_gallery]
        self.mock_stash_interface.find_scenes.return_value = []

        result = self.linker.auto_link_scenes()
        self.assertEqual(result['message'], "No scenes found")

    def test_update_gallery_exception_handling(self):
        """Test exception handling during gallery updates"""
        self.linker.settings = {'dryRun': False}
        self.mock_stash_interface.find_galleries.return_value = [self.sample_gallery]
        self.mock_stash_interface.find_scenes.return_value = [self.sample_scene]
        self.mock_stash_interface.update_gallery.side_effect = Exception("Update failed")

        with patch.object(self.linker, 'find_matching_scenes') as mock_find:
            mock_find.return_value = [(self.sample_scene, 0.9)]

            # Should not crash despite exception
            result = self.linker.auto_link_scenes()
            self.assertEqual(result['linked_count'], 0)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function and plugin integration"""

    @patch('sys.stdin')
    @patch('gallery_linker.GalleryLinker')
    def test_main_plugin_mode(self, mock_linker_class, mock_stdin):
        """Test main function in plugin mode"""
        # Mock stdin input
        plugin_input = {
            'server_connection': {'host': 'localhost', 'port': '9999'},
            'args': {'mode': 'auto_link_scenes'}
        }
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = json.dumps(plugin_input)

        # Mock linker instance
        mock_linker = Mock()
        mock_linker.auto_link_scenes.return_value = {'linked_count': 5}
        mock_linker_class.return_value = mock_linker

        # Import and run main
        from plugins.GalleryLinker.gallery_linker import main

        with patch('builtins.print') as mock_print:
            result = main()

            self.assertEqual(result, 0)
            mock_linker.load_settings.assert_called_once_with(plugin_input)
            mock_linker.auto_link_scenes.assert_called_once()
            mock_print.assert_called_once()

    @patch('sys.argv', ['gallery_linker.py', '--url', 'http://localhost:9999', '--api-key', 'test_key'])
    @patch('sys.stdin')
    @patch('gallery_linker.GalleryLinker')
    def test_main_cli_mode(self, mock_linker_class, mock_stdin):
        """Test main function in CLI mode"""
        mock_stdin.isatty.return_value = True

        # Mock linker instance
        mock_linker = Mock()
        mock_linker.auto_link_scenes.return_value = {'linked_count': 3}
        mock_linker_class.return_value = mock_linker

        from plugins.GalleryLinker.gallery_linker import main

        with patch('builtins.print') as mock_print:
            result = main()

            self.assertEqual(result, 0)
            mock_linker_class.assert_called_with('http://localhost:9999', 'test_key')
            mock_linker.auto_link_scenes.assert_called_once()

    @patch('sys.stdin')
    @patch('gallery_linker.GalleryLinker')
    def test_main_exception_handling(self, mock_linker_class, mock_stdin):
        """Test main function exception handling"""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = '{"args": {"mode": "auto_link_scenes"}}'

        # Mock linker to raise exception
        mock_linker = Mock()
        mock_linker.auto_link_scenes.side_effect = Exception("Test error")
        mock_linker_class.return_value = mock_linker

        from plugins.GalleryLinker.gallery_linker import main

        with patch('builtins.print') as mock_print:
            result = main()

            self.assertEqual(result, 1)
            # Verify error output
            error_output = json.loads(mock_print.call_args[0][0])
            self.assertEqual(error_output['error'], 'Test error')


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run tests
    unittest.main(verbosity=2)