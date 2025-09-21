#!/usr/bin/env python3

"""
Gallery Linker Plugin for Stash
Links image galleries to related scenes and performers based on file patterns, dates, and metadata.
"""

import sys
import json
import argparse
import logging
import re
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

try:
    from stashapi.stashapp import StashInterface
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies: pip install stashapp-tools requests")
    sys.exit(1)


class GalleryLinker:
    stash: StashInterface
    settings: Dict
    logger: logging.Logger

    def __init__(self, stash_url: str | None = None, api_key: str | None = None):
        # Initialize with default connection config
        default_config = {
            "scheme": "http",
            "host": "localhost",
            "port": "9999",
            "logger": logging.getLogger("stashapi")
        }

        # If custom URL/API key provided, parse and update config
        if stash_url or api_key:
            if stash_url:
                # Parse URL to extract components
                from urllib.parse import urlparse
                parsed = urlparse(stash_url)
                default_config.update({
                    "scheme": parsed.scheme or "http",
                    "host": parsed.hostname or "localhost",
                    "port": str(parsed.port or 9999)
                })
            if api_key:
                default_config["ApiKey"] = api_key

        self.stash = StashInterface(default_config)
        self.settings = {}
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("gallery_linker")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_settings(self, plugin_input: Dict) -> None:
        """Load plugin settings from Stash input"""
        if 'server_connection' in plugin_input:
            # Recreate StashInterface with server connection details
            self.stash = StashInterface(plugin_input['server_connection'])

        self.settings = plugin_input.get('args', {})

        if self.settings.get('debugTracing', False):
            self.logger.setLevel(logging.DEBUG)

    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract date from filename using common patterns"""
        date_patterns = [
            r'(\d{4})[_-](\d{2})[_-](\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
            r'(\d{2})[_-](\d{2})[_-](\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            r'(\d{4})(\d{2})(\d{2})',          # YYYYMMDD
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY first
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                    else:  # Year last
                        return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                except ValueError:
                    continue
        return None

    def extract_performers_from_path(self, path: str, performers: List[Dict]) -> List[str]:
        """Extract performer names from file path"""
        found_performers = []
        path_lower = path.lower()

        for performer in performers:
            name = performer['name'].lower()
            # Check if performer name appears in path
            if name in path_lower:
                found_performers.append(performer['id'])

            # Check for name variants (first name, last name)
            name_parts = name.split()
            if len(name_parts) > 1:
                for part in name_parts:
                    if len(part) > 2 and part in path_lower:
                        found_performers.append(performer['id'])
                        break

        return list(set(found_performers))  # Remove duplicates

    def _score_title_similarity(self, gallery_title: str, scene_title: str) -> Tuple[float, Optional[str]]:
        if gallery_title and scene_title:
            title_sim = self.similarity(gallery_title, scene_title)
            if title_sim > 0.7:
                return title_sim * 0.4, f"Title similarity: {title_sim:.2f}"
        return 0.0, None

    def _score_date_match(self, gallery_date: Optional[str], scene_date: Optional[str]) -> Tuple[float, Optional[str]]:
        if gallery_date and scene_date:
            try:
                g_date = datetime.strptime(gallery_date, '%Y-%m-%d')
                s_date = datetime.strptime(scene_date, '%Y-%m-%d')
                date_diff = abs((g_date - s_date).days)
                tolerance = self.settings.get('dateTolerance', 7)
                if date_diff <= tolerance:
                    date_score = max(0, 1 - (date_diff / tolerance)) * 0.3
                    return date_score, f"Date match: {date_diff} days difference"
            except ValueError:
                pass
        return 0.0, None

    def _score_filename_similarity(self, gallery_path: str, scene_files: List[Dict]) -> Tuple[float, Optional[str]]:
        if gallery_path and scene_files:
            for file_info in scene_files:
                file_path = file_info.get('path', '')
                if file_path:
                    path_sim = self.similarity(
                        os.path.basename(gallery_path),
                        os.path.basename(file_path)
                    )
                    if path_sim > 0.6:
                        return path_sim * 0.2, f"Filename similarity: {path_sim:.2f}"
        return 0.0, None

    def _score_performer_overlap(self, gallery_performers: List[Dict], scene_performers: List[Dict]) -> Tuple[float, Optional[str]]:
        gallery_ids = set(p['id'] for p in gallery_performers)
        scene_ids = set(p['id'] for p in scene_performers)
        if gallery_ids and scene_ids:
            overlap = len(gallery_ids.intersection(scene_ids))
            total = len(gallery_ids.union(scene_ids))
            if total > 0:
                performer_score = (overlap / total) * 0.1
                return performer_score, f"Performer overlap: {overlap}/{total}"
        return 0.0, None

    def find_matching_scenes(self, gallery: Dict, scenes: List[Dict]) -> List[Tuple[Dict, float]]:
        """Find scenes that could match the gallery"""
        matches = []
        gallery_title = gallery.get('title', '')
        gallery_date = gallery.get('date')
        gallery_path = gallery.get('path', {}).get('path', '') if gallery.get('path') else ''

        # Extract date from filename if no date set
        if not gallery_date and gallery_path:
            extracted_date = self.extract_date_from_filename(gallery_path)
            if extracted_date:
                gallery_date = extracted_date.strftime('%Y-%m-%d')

        for scene in scenes:
            score = 0.0
            reasons = []

            # Title similarity
            t_score, t_reason = self._score_title_similarity(gallery_title, scene.get('title', ''))
            score += t_score
            if t_reason:
                reasons.append(t_reason)

            # Date matching
            d_score, d_reason = self._score_date_match(gallery_date, scene.get('date', ''))
            score += d_score
            if d_reason:
                reasons.append(d_reason)

            # Filename/path similarity
            f_score, f_reason = self._score_filename_similarity(gallery_path, scene.get('files', []))
            score += f_score
            if f_reason:
                reasons.append(f_reason)

            # Performer overlap
            p_score, p_reason = self._score_performer_overlap(
                gallery.get('performers', []), scene.get('performers', [])
            )
            score += p_score
            if p_reason:
                reasons.append(p_reason)

            if score > 0.3:  # Minimum threshold
                matches.append((scene, score, reasons))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return [(scene, score) for scene, score, reasons in matches]

    def auto_link_scenes(self) -> Dict:
        """Automatically link galleries to scenes"""
        self.logger.info("Starting auto-link scenes process")

        # Get all galleries
        galleries = self.stash.find_galleries()
        if not galleries:
            return {"message": "No galleries found"}

        # Get all scenes
        scenes = self.stash.find_scenes()
        if not scenes:
            return {"message": "No scenes found"}

        linked_count = 0
        suggestions = []

        for gallery in galleries:
            # Skip if already linked to scenes
            if gallery.get('scenes') and not self.settings.get('overwriteExisting', False):
                continue

            matches = self.find_matching_scenes(gallery, scenes)  # type: ignore

            if matches:
                best_match, score = matches[0]

                if score > 0.7 or self.settings.get('autoLinkByDate', False):
                    # Auto-link if high confidence or auto-link enabled
                    if not self.settings.get('dryRun', False):
                        try:
                            existing_scene_ids = [s['id'] for s in gallery.get('scenes', [])]
                            if best_match['id'] not in existing_scene_ids:
                                existing_scene_ids.append(best_match['id'])

                                self.stash.update_gallery({
                                    'id': gallery['id'],
                                    'scene_ids': existing_scene_ids
                                })
                                linked_count += 1
                                self.logger.info(f"Linked gallery '{gallery.get('title', gallery['id'])}' to scene '{best_match.get('title', best_match['id'])}'")
                        except Exception as e:
                            self.logger.error(f"Failed to link gallery {gallery['id']}: {e}")
                else:
                    # Add to suggestions
                    suggestions.append({
                        'gallery_id': gallery['id'],
                        'gallery_title': gallery.get('title', 'Untitled'),
                        'scene_id': best_match['id'],
                        'scene_title': best_match.get('title', 'Untitled'),
                        'confidence': score
                    })

        result = {
            "linked_count": linked_count,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions[:10]  # Limit to first 10
        }

        if self.settings.get('dryRun', False):
            result["message"] = f"DRY RUN: Would have linked {linked_count} galleries"
        else:
            result["message"] = f"Successfully linked {linked_count} galleries to scenes"

        return result

    def auto_link_performers(self) -> Dict:
        """Automatically link performers to galleries"""
        self.logger.info("Starting auto-link performers process")

        # Get all galleries and performers
        galleries = self.stash.find_galleries()
        performers = self.stash.find_performers()

        if not galleries or not performers:
            return {"message": "No galleries or performers found"}

        linked_count = 0

        for gallery in galleries:
            gallery_path = gallery.get('path', {}).get('path', '') if gallery.get('path') else ''
            if not gallery_path:
                continue

            # Find performers in path
            found_performer_ids = self.extract_performers_from_path(gallery_path, performers)

            if found_performer_ids:
                existing_performer_ids = [p['id'] for p in gallery.get('performers', [])]
                new_performer_ids = list(set(existing_performer_ids + found_performer_ids))

                if len(new_performer_ids) > len(existing_performer_ids):
                    if not self.settings.get('dryRun', False):
                        try:
                            self.stash.update_gallery({
                                'id': gallery['id'],
                                'performer_ids': new_performer_ids
                            })
                            linked_count += 1
                            self.logger.info(f"Added performers to gallery '{gallery.get('title', gallery['id'])}'")
                        except Exception as e:
                            self.logger.error(f"Failed to update gallery {gallery['id']}: {e}")

        result = {
            "linked_count": linked_count,
            "message": ""
        }

        if self.settings.get('dryRun', False):
            result["message"] = f"DRY RUN: Would have updated {linked_count} galleries with performers"
        else:
            result["message"] = f"Successfully updated {linked_count} galleries with performers"

        return result

    def generate_report(self) -> Dict:
        """Generate a report of gallery relationships"""
        self.logger.info("Generating linking report")

        galleries = self.stash.find_galleries()

        total_galleries = len(galleries)
        linked_to_scenes = sum(1 for g in galleries if g.get('scenes'))
        linked_to_performers = sum(1 for g in galleries if g.get('performers'))
        unlinked = sum(1 for g in galleries if not g.get('scenes') and not g.get('performers'))

        report = {
            "total_galleries": total_galleries,
            "linked_to_scenes": linked_to_scenes,
            "linked_to_performers": linked_to_performers,
            "unlinked": unlinked,
            "coverage_percentage": round((total_galleries - unlinked) / total_galleries * 100, 2) if total_galleries > 0 else 0
        }

        return report


def main():
    parser = argparse.ArgumentParser(description="Gallery Linker Plugin")
    parser.add_argument('--url', dest='stash_url', help='Stash URL')
    parser.add_argument('--api-key', dest='api_key', help='Stash API Key')

    args = parser.parse_args()

    # Read from stdin for plugin mode
    plugin_input = None
    if not sys.stdin.isatty():
        try:
            plugin_input = json.loads(sys.stdin.read())
        except json.JSONDecodeError:
            pass

    linker = GalleryLinker(args.stash_url, args.api_key)

    if plugin_input:
        linker.load_settings(plugin_input)
        mode = plugin_input.get('args', {}).get('mode', 'auto_link_scenes')
    else:
        mode = 'auto_link_scenes'

    # Execute the requested operation
    try:
        if mode == 'auto_link_scenes':
            result = linker.auto_link_scenes()
        elif mode == 'auto_link_performers':
            result = linker.auto_link_performers()
        elif mode == 'generate_report':
            result = linker.generate_report()
        else:
            result = {"error": f"Unknown mode: {mode}"}

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result, indent=2))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())