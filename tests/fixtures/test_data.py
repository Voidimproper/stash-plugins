#!/usr/bin/env python3

"""
Test fixtures and sample data for Stash plugin testing
"""

from datetime import datetime, timedelta


class TestData:
    """Container for test data and fixtures"""

    @staticmethod
    def get_sample_galleries():
        """Sample gallery data for testing"""
        return [
            {
                'id': '1',
                'title': 'Test Gallery One',
                'date': '2023-01-15',
                'path': {'path': '/storage/galleries/Performer_One/2023/Test_Gallery_2023-01-15'},
                'performers': [{'id': '101', 'name': 'Performer One'}],
                'scenes': [],
                'studio': {'id': '201', 'name': 'Test Studio'},
                'tags': [{'id': '301', 'name': 'tag1'}]
            },
            {
                'id': '2',
                'title': 'Gallery Two',
                'date': '2023-01-16',
                'path': {'path': '/storage/galleries/Jane_Doe/Gallery_Two_20230116'},
                'performers': [{'id': '102', 'name': 'Jane Doe'}],
                'scenes': [{'id': '10', 'title': 'Scene Ten'}],
                'studio': None,
                'tags': []
            },
            {
                'id': '3',
                'title': 'Unlinked Gallery',
                'date': '2023-02-01',
                'path': {'path': '/storage/galleries/unlinked/Random_Gallery'},
                'performers': [],
                'scenes': [],
                'studio': None,
                'tags': []
            },
            {
                'id': '4',
                'title': 'Multi Performer Gallery',
                'date': '2023-01-20',
                'path': {'path': '/storage/galleries/multi/Multi_Performer_Gallery'},
                'performers': [
                    {'id': '101', 'name': 'Performer One'},
                    {'id': '103', 'name': 'John Smith'}
                ],
                'scenes': [],
                'studio': {'id': '201', 'name': 'Test Studio'},
                'tags': [{'id': '301', 'name': 'tag1'}, {'id': '302', 'name': 'tag2'}]
            },
            {
                'id': '5',
                'title': 'Gallery Without Date',
                'date': None,
                'path': {'path': '/storage/galleries/nodates/Gallery_2023_03_15_title'},
                'performers': [{'id': '102', 'name': 'Jane Doe'}],
                'scenes': [],
                'studio': None,
                'tags': []
            }
        ]

    @staticmethod
    def get_sample_scenes():
        """Sample scene data for testing"""
        return [
            {
                'id': '10',
                'title': 'Test Scene One',
                'date': '2023-01-15',
                'files': [{'path': '/storage/scenes/Performer_One/Test_Scene_2023-01-15.mp4'}],
                'performers': [{'id': '101', 'name': 'Performer One'}],
                'studio': {'id': '201', 'name': 'Test Studio'},
                'tags': [{'id': '301', 'name': 'tag1'}],
                'duration': 3600,
                'rating': 5
            },
            {
                'id': '11',
                'title': 'Scene Two',
                'date': '2023-01-16',
                'files': [{'path': '/storage/scenes/Jane_Doe/Scene_Two_20230116.mp4'}],
                'performers': [{'id': '102', 'name': 'Jane Doe'}],
                'studio': None,
                'tags': [],
                'duration': 2400,
                'rating': 4
            },
            {
                'id': '12',
                'title': 'Multi Performer Scene',
                'date': '2023-01-20',
                'files': [{'path': '/storage/scenes/multi/Multi_Performer_Scene.mp4'}],
                'performers': [
                    {'id': '101', 'name': 'Performer One'},
                    {'id': '103', 'name': 'John Smith'}
                ],
                'studio': {'id': '201', 'name': 'Test Studio'},
                'tags': [{'id': '301', 'name': 'tag1'}, {'id': '302', 'name': 'tag2'}],
                'duration': 4200,
                'rating': 5
            },
            {
                'id': '13',
                'title': 'Scene With Different Date',
                'date': '2023-02-01',
                'files': [{'path': '/storage/scenes/other/Different_Scene.mp4'}],
                'performers': [{'id': '104', 'name': 'Other Performer'}],
                'studio': {'id': '202', 'name': 'Other Studio'},
                'tags': [{'id': '303', 'name': 'different'}],
                'duration': 1800,
                'rating': 3
            },
            {
                'id': '14',
                'title': 'Scene Without Date',
                'date': None,
                'files': [{'path': '/storage/scenes/nodates/Scene_2023_03_15.mp4'}],
                'performers': [{'id': '102', 'name': 'Jane Doe'}],
                'studio': None,
                'tags': [],
                'duration': 3000,
                'rating': None
            }
        ]

    @staticmethod
    def get_sample_performers():
        """Sample performer data for testing"""
        return [
            {
                'id': '101',
                'name': 'Performer One',
                'aliases': ['P1', 'PerformerOne'],
                'gender': 'FEMALE',
                'birthdate': '1990-05-15',
                'ethnicity': 'Caucasian',
                'country': 'USA',
                'eye_color': 'Blue',
                'height': 165,
                'weight': 55,
                'measurements': '34B-24-35',
                'fake_tits': 'No',
                'career_length': '2010-2023',
                'tattoos': 'Small star on wrist',
                'piercings': 'Ears',
                'tags': [{'id': '301', 'name': 'tag1'}]
            },
            {
                'id': '102',
                'name': 'Jane Doe',
                'aliases': ['Jane D', 'JD'],
                'gender': 'FEMALE',
                'birthdate': '1992-08-22',
                'ethnicity': 'Asian',
                'country': 'Japan',
                'eye_color': 'Brown',
                'height': 160,
                'weight': 50,
                'measurements': '32A-22-33',
                'fake_tits': 'No',
                'career_length': '2015-2023',
                'tattoos': None,
                'piercings': None,
                'tags': []
            },
            {
                'id': '103',
                'name': 'John Smith',
                'aliases': ['JS', 'Johnny'],
                'gender': 'MALE',
                'birthdate': '1988-12-10',
                'ethnicity': 'Caucasian',
                'country': 'Canada',
                'eye_color': 'Green',
                'height': 180,
                'weight': 75,
                'measurements': None,
                'fake_tits': None,
                'career_length': '2012-2023',
                'tattoos': 'Full sleeve on left arm',
                'piercings': None,
                'tags': [{'id': '302', 'name': 'tag2'}]
            },
            {
                'id': '104',
                'name': 'Other Performer',
                'aliases': [],
                'gender': 'FEMALE',
                'birthdate': '1995-03-05',
                'ethnicity': 'Hispanic',
                'country': 'Mexico',
                'eye_color': 'Hazel',
                'height': 168,
                'weight': 60,
                'measurements': '36C-26-38',
                'fake_tits': 'Yes',
                'career_length': '2018-2023',
                'tattoos': 'Rose on shoulder',
                'piercings': 'Navel',
                'tags': [{'id': '303', 'name': 'different'}]
            }
        ]

    @staticmethod
    def get_sample_studios():
        """Sample studio data for testing"""
        return [
            {
                'id': '201',
                'name': 'Test Studio',
                'url': 'https://teststudio.com',
                'parent': None,
                'details': 'A test studio for unit testing',
                'aliases': ['TS', 'TestStudio']
            },
            {
                'id': '202',
                'name': 'Other Studio',
                'url': 'https://otherstudio.com',
                'parent': {'id': '201', 'name': 'Test Studio'},
                'details': 'Another studio for testing',
                'aliases': ['OS']
            }
        ]

    @staticmethod
    def get_sample_tags():
        """Sample tag data for testing"""
        return [
            {
                'id': '301',
                'name': 'tag1',
                'aliases': ['t1'],
                'description': 'First test tag'
            },
            {
                'id': '302',
                'name': 'tag2',
                'aliases': ['t2'],
                'description': 'Second test tag'
            },
            {
                'id': '303',
                'name': 'different',
                'aliases': ['diff'],
                'description': 'A different tag'
            }
        ]

    @staticmethod
    def get_plugin_input_samples():
        """Sample plugin input data for testing"""
        return {
            'basic_plugin_input': {
                'server_connection': {
                    'Scheme': 'http',
                    'Host': 'localhost',
                    'Port': 9999,
                    'SessionCookie': {
                        'Name': 'session',
                        'Value': 'test_session_value',
                        'Path': '/',
                        'Domain': 'localhost',
                        'Expires': '2024-12-31T23:59:59Z'
                    },
                    'Dir': '/home/user/.stash',
                    'PluginDir': '/home/user/.stash/plugins'
                },
                'args': {
                    'mode': 'auto_link_scenes',
                    'debugTracing': False,
                    'dryRun': False,
                    'dateTolerance': 7,
                    'overwriteExisting': False,
                    'autoLinkByDate': False
                }
            },
            'debug_plugin_input': {
                'server_connection': {
                    'Scheme': 'https',
                    'Host': 'remote.stash.com',
                    'Port': 443,
                    'ApiKey': 'test_api_key_12345',
                    'Dir': '/opt/stash',
                    'PluginDir': '/opt/stash/plugins'
                },
                'args': {
                    'mode': 'generate_report',
                    'debugTracing': True,
                    'dryRun': True,
                    'dateTolerance': 3,
                    'overwriteExisting': True,
                    'autoLinkByDate': True
                }
            }
        }

    @staticmethod
    def get_file_path_samples():
        """Sample file paths for testing path-based logic"""
        return {
            'with_dates': [
                '/storage/galleries/performer/Gallery_2023-01-15_title',
                '/storage/galleries/performer/Gallery_2023_01_15_title',
                '/storage/galleries/performer/Gallery_20230115_title',
                '/storage/scenes/performer/Scene_2023-01-15.mp4',
                '/storage/scenes/performer/Scene_20230115.mp4'
            ],
            'with_performers': [
                '/storage/galleries/Performer One/gallery_folder',
                '/storage/galleries/Jane Doe/special_gallery',
                '/storage/galleries/John Smith/workout_gallery',
                '/storage/galleries/multi/Performer One & Jane Doe/collab'
            ],
            'without_dates': [
                '/storage/galleries/performer/Random_Gallery_Title',
                '/storage/scenes/performer/Scene_Title.mp4',
                '/storage/galleries/folder/subfolder/gallery'
            ],
            'edge_cases': [
                '/storage/galleries/2023/01/15/gallery_in_date_folder',
                '/storage/galleries/performer_2023_not_date/gallery',
                '/storage/galleries/20230/invalid_date/gallery',
                '/storage/galleries/performer/gallery_123456_numbers'
            ]
        }

    @staticmethod
    def get_expected_matches():
        """Expected match results for testing matching logic"""
        return {
            'high_confidence_matches': [
                {
                    'gallery_id': '1',
                    'scene_id': '10',
                    'expected_score_range': (0.8, 1.0),
                    'reasons': ['title_similarity', 'date_match', 'performer_overlap']
                },
                {
                    'gallery_id': '4',
                    'scene_id': '12',
                    'expected_score_range': (0.75, 0.95),
                    'reasons': ['date_match', 'performer_overlap', 'studio_match']
                }
            ],
            'medium_confidence_matches': [
                {
                    'gallery_id': '2',
                    'scene_id': '11',
                    'expected_score_range': (0.4, 0.7),
                    'reasons': ['date_match', 'performer_overlap']
                }
            ],
            'low_confidence_matches': [
                {
                    'gallery_id': '3',
                    'scene_id': '13',
                    'expected_score_range': (0.0, 0.3),
                    'reasons': ['date_match']
                }
            ],
            'no_matches': [
                {
                    'gallery_id': '5',
                    'scene_id': '13',
                    'expected_score_range': (0.0, 0.2),
                    'reasons': []
                }
            ]
        }


class MockStashInterface:
    """Mock StashInterface for testing without actual Stash connection"""

    def __init__(self, config=None):
        self.config = config or {}
        self.galleries = TestData.get_sample_galleries()
        self.scenes = TestData.get_sample_scenes()
        self.performers = TestData.get_sample_performers()
        self.studios = TestData.get_sample_studios()
        self.tags = TestData.get_sample_tags()

    def find_galleries(self, **kwargs):
        """Mock find_galleries method"""
        return self.galleries

    def find_scenes(self, **kwargs):
        """Mock find_scenes method"""
        return self.scenes

    def find_performers(self, **kwargs):
        """Mock find_performers method"""
        return self.performers

    def find_studios(self, **kwargs):
        """Mock find_studios method"""
        return self.studios

    def find_tags(self, **kwargs):
        """Mock find_tags method"""
        return self.tags

    def find_gallery(self, gallery_id):
        """Mock find_gallery method"""
        for gallery in self.galleries:
            if gallery['id'] == str(gallery_id):
                return gallery
        return None

    def find_scene(self, scene_id):
        """Mock find_scene method"""
        for scene in self.scenes:
            if scene['id'] == str(scene_id):
                return scene
        return None

    def update_gallery(self, gallery_data):
        """Mock update_gallery method"""
        gallery_id = gallery_data['id']
        for i, gallery in enumerate(self.galleries):
            if gallery['id'] == gallery_id:
                # Update the gallery with new data
                if 'scene_ids' in gallery_data:
                    # Convert scene IDs to scene objects
                    scenes = []
                    for scene_id in gallery_data['scene_ids']:
                        scene = self.find_scene(scene_id)
                        if scene:
                            scenes.append({'id': scene_id, 'title': scene['title']})
                    self.galleries[i]['scenes'] = scenes

                if 'performer_ids' in gallery_data:
                    # Convert performer IDs to performer objects
                    performers = []
                    for performer_id in gallery_data['performer_ids']:
                        for performer in self.performers:
                            if performer['id'] == performer_id:
                                performers.append({'id': performer_id, 'name': performer['name']})
                                break
                    self.galleries[i]['performers'] = performers

                return self.galleries[i]
        return None

    def update_scene(self, scene_data):
        """Mock update_scene method"""
        scene_id = scene_data['id']
        for i, scene in enumerate(self.scenes):
            if scene['id'] == scene_id:
                self.scenes[i].update(scene_data)
                return self.scenes[i]
        return None