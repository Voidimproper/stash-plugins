"""
Gallery Linker Plugin for Stash.

Links image galleries to related scenes and performers based on file patterns, dates, and metadata.
"""

import argparse
import contextlib
import json
import logging
import os
import re
import sys
from datetime import datetime
from difflib import SequenceMatcher
from functools import lru_cache
from typing import List, Optional, Tuple, Union
from datatypes import MatchResult, ScoringConfig
from util import parse_settings_argument, _get_default_settings

try:
    from stashapi.stashapp import StashInterface
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies: pip install stashapp-tools requests")
    sys.exit(1)

# Type aliases for better code readability
Scenedict = dict[str, Union[str, List, dict]]
Gallerydict = dict[str, Union[str, List, dict]]


class GalleryLinker:
    """Main class for Gallery Linker Plugin."""

    def __init__(self, stash_url: str | None = None, api_key: str | None = None):
        """Initialize the GalleryLinker with Stash connection details."""
        self.scoring_config = ScoringConfig()

        default_config = self._build_default_config()

        if stash_url or api_key:
            self._update_config_from_params(default_config, stash_url, api_key)

        self.stash = StashInterface(default_config)
        self.settings = _get_default_settings()
        self.logger = self._setup_logger()

    @property
    def TITLE_SIMILARITY_WEIGHT(self) -> float:
        return self.scoring_config.title_similarity_weight

    @property
    def DATE_MATCH_WEIGHT(self) -> float:
        return self.scoring_config.date_match_weight

    @property
    def FILENAME_SIMILARITY_WEIGHT(self) -> float:
        return self.scoring_config.filename_similarity_weight

    @property
    def PERFORMER_OVERLAP_WEIGHT(self) -> float:
        return self.scoring_config.performer_overlap_weight

    @property
    def TITLE_SIMILARITY_THRESHOLD(self) -> float:
        return self.scoring_config.title_similarity_threshold

    @property
    def FILENAME_SIMILARITY_THRESHOLD(self) -> float:
        return self.scoring_config.filename_similarity_threshold

    @property
    def DEFAULT_MINIMUM_SCORE(self) -> float:
        return self.scoring_config.default_minimum_score

    @property
    def DEFAULT_AUTO_LINK_THRESHOLD(self) -> float:
        return self.scoring_config.default_auto_link_threshold

    stash: StashInterface
    settings: dict
    logger: logging.Logger
    scoring_config: ScoringConfig

    def _build_default_config(self) -> dict:
        """Build default Stash connection configuration."""
        return {
            "scheme": "http",
            "host": "localhost",
            "port": "9999",
            "logger": logging.getLogger("stashapi"),
        }

    def _update_config_from_params(self, config: dict, stash_url: str | None, api_key: str | None) -> None:
        """Update configuration with provided URL and API key."""
        if stash_url:
            from urllib.parse import urlparse

            parsed = urlparse(stash_url)
            config.update(
                {
                    "scheme": parsed.scheme or "http",
                    "host": parsed.hostname or "localhost",
                    "port": str(parsed.port or 9999),
                }
            )
        if api_key:
            config["ApiKey"] = api_key

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("gallery_linker")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_settings(self, plugin_input: dict) -> None:
        """Load plugin settings from Stash input."""
        if "server_connection" in plugin_input:
            # Recreate StashInterface with server connection details
            self.stash = StashInterface(plugin_input["server_connection"])

        self.settings = plugin_input.get("args", {})

        if self.settings.get("debugTracing", False):
            self.logger.setLevel(logging.DEBUG)

    def _normalize_string(self, text: Optional[str]) -> str:
        """Normalize string for comparison."""
        if not text:
            return ""
        return text.lower().strip()

    @lru_cache(maxsize=1000)
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings with caching."""
        norm_a = self._normalize_string(a)
        norm_b = self._normalize_string(b)

        if not norm_a or not norm_b:
            return 0.0

        return SequenceMatcher(None, norm_a, norm_b).ratio()

    def extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract date from filename using common patterns."""
        date_patterns = [
            r"(\d{4})[_-](\d{2})[_-](\d{2})",  # YYYY-MM-DD or YYYY_MM_DD
            r"(\d{2})[_-](\d{2})[_-](\d{4})",  # DD-MM-YYYY or MM-DD-YYYY
            r"(\d{4})(\d{2})(\d{2})",  # YYYYMMDD
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

    def extract_performers_from_path(self, path: str, performers: List[dict]) -> List[str]:
        """Extract performer names from file path."""
        found_performers = []
        path_lower = path.lower()

        for performer in performers:
            name = performer["name"].lower()
            # Check if performer name appears in path
            if name in path_lower:
                found_performers.append(performer["id"])

            # Check for name variants (first name, last name)
            name_parts = name.split()
            if len(name_parts) > 1:
                for part in name_parts:
                    if len(part) > 2 and part in path_lower:
                        found_performers.append(performer["id"])
                        break

        return list(set(found_performers))  # Remove duplicates

    def _score_title_similarity(self, gallery_title: str, scene_title: str) -> Tuple[float, Optional[str]]:
        """Score title similarity between gallery and scene."""
        if gallery_title and scene_title:
            title_sim = self.similarity(gallery_title, scene_title)
            if title_sim > self.TITLE_SIMILARITY_THRESHOLD:
                return title_sim * self.TITLE_SIMILARITY_WEIGHT, f"Title similarity: {title_sim:.2f}"
        return 0.0, None

    def _score_date_match(self, gallery_date: Optional[str], scene_date: Optional[str]) -> Tuple[float, Optional[str]]:
        """Score date match between gallery and scene."""
        if gallery_date and scene_date:
            try:
                g_date = datetime.strptime(gallery_date, "%Y-%m-%d")
                s_date = datetime.strptime(scene_date, "%Y-%m-%d")
                date_diff = abs((g_date - s_date).days)
                tolerance = self.settings.get("dateTolerance", 7)
                if date_diff <= tolerance:
                    date_score = max(0, 1 - (date_diff / tolerance)) * self.DATE_MATCH_WEIGHT
                    return date_score, f"Date match: {date_diff} days difference"
            except ValueError:
                pass
        return 0.0, None

    def _score_filename_similarity(self, gallery_path: str, scene_files: List[dict]) -> Tuple[float, Optional[str]]:
        """Score filename similarity between gallery and scene files."""
        if gallery_path and scene_files:
            gallery_filename = os.path.basename(gallery_path)
            for file_info in scene_files:
                file_path = file_info.get("path", "")
                if file_path:
                    scene_filename = os.path.basename(file_path)
                    path_sim = self.similarity(gallery_filename, scene_filename)
                    if path_sim > self.FILENAME_SIMILARITY_THRESHOLD:
                        return path_sim * self.FILENAME_SIMILARITY_WEIGHT, f"Filename similarity: {path_sim:.2f}"
        return 0.0, None

    def _score_performer_overlap(
        self, gallery_performers: List[dict], scene_performers: List[dict]
    ) -> Tuple[float, Optional[str]]:
        """Score performer overlap between gallery and scene."""
        gallery_ids = {p["id"] for p in gallery_performers}
        scene_ids = {p["id"] for p in scene_performers}
        if gallery_ids and scene_ids:
            overlap = len(gallery_ids.intersection(scene_ids))
            total = len(gallery_ids.union(scene_ids))
            if total > 0:
                performer_score = (overlap / total) * self.PERFORMER_OVERLAP_WEIGHT
                return performer_score, f"Performer overlap: {overlap}/{total}"
        return 0.0, None

    def find_matching_scenes(self, gallery: Gallerydict, scenes: List[Scenedict]) -> List[MatchResult]:
        """Find scenes that could match the gallery with input validation and optimizations."""
        if not gallery or not isinstance(gallery, dict):
            raise ValueError("Gallery must be a non-empty dictionary")
        if not scenes or not isinstance(scenes, list):
            raise ValueError("Scenes must be a non-empty list")

        self.logger.debug(f"Finding matches for gallery: {gallery.get('title', gallery.get('id'))}")

        matches = []
        minimum_score = self.settings.get("minimumScore", self.DEFAULT_MINIMUM_SCORE)

        gallery_title = gallery.get("title", "")
        gallery_date = gallery.get("date", "")
        gallery_path = gallery.get("path", {}).get("path", "") if gallery.get("path") else ""   # type: ignore

        # Extract date from filename if no date set
        if not gallery_date and gallery_path:
            extracted_date = self.extract_date_from_filename(gallery_path)
            if extracted_date:
                gallery_date = extracted_date.strftime("%Y-%m-%d")

        for i, scene in enumerate(scenes):
            if self.settings.get("debugTracing") and i % 100 == 0:
                self.logger.debug(f"Processed {i}/{len(scenes)} scenes")

            # Early exit optimization - quick title check
            if gallery_title and scene.get("title"):
                quick_title_sim = self.similarity(gallery_title, scene["title"])  # type: ignore
                if quick_title_sim < 0.1:  # Very low threshold for early exit
                    continue

            score = 0.0
            reasons = []

            # Title similarity
            t_score, t_reason = self._score_title_similarity(gallery_title, scene.get("title", ""))  # type: ignore
            score += t_score
            if t_reason:
                reasons.append(t_reason)

            # Date matching
            d_score, d_reason = self._score_date_match(gallery_date, scene.get("date", ""))  # type: ignore
            score += d_score
            if d_reason:
                reasons.append(d_reason)

            # Filename/path similarity
            f_score, f_reason = self._score_filename_similarity(gallery_path, scene.get("files", []))  # type: ignore
            score += f_score
            if f_reason:
                reasons.append(f_reason)

            # Performer overlap
            p_score, p_reason = self._score_performer_overlap(
                gallery.get("performers", []), scene.get("performers", [])  # type: ignore
            )
            score += p_score
            if p_reason:
                reasons.append(p_reason)

            if score > minimum_score:
                matches.append(MatchResult(scene, score, reasons))

        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)

        self.logger.debug(f"Found {len(matches)} matches above threshold")
        return matches

    def auto_link_scenes(self) -> dict:
        """Automatically link galleries to scenes."""
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
            if gallery.get("scenes") and not self.settings.get("overwriteExisting", False):
                continue

            matches = self.find_matching_scenes(gallery, scenes)  # type: ignore

            if matches:
                best_match = matches[0]

                auto_link_threshold = self.settings.get("autoLinkThreshold", self.DEFAULT_AUTO_LINK_THRESHOLD)
                if best_match.score > auto_link_threshold or self.settings.get("autoLinkByDate", False):
                    # Auto-link if high confidence or auto-link enabled
                    if not self.settings.get("dryRun", False):
                        try:
                            existing_scene_ids = [s["id"] for s in gallery.get("scenes", [])]
                            if best_match.scene["id"] not in existing_scene_ids:
                                existing_scene_ids.append(best_match.scene["id"])

                                self.stash.update_gallery({"id": gallery["id"], "scene_ids": existing_scene_ids})
                                linked_count += 1
                                self.logger.info(
                                    f"Linked gallery '{gallery.get('title', gallery['id'])}' to scene '{best_match.scene.get('title', best_match.scene['id'])}'"
                                )
                        except Exception as e:
                            self.logger.error(f"Failed to link gallery {gallery['id']}: {e}")
                            if self.settings.get("debugTracing", False):
                                self.logger.exception("Full traceback:")
                else:
                    # Add to suggestions
                    suggestions.append(
                        {
                            "gallery_id": gallery["id"],
                            "gallery_title": gallery.get("title", "Untitled"),
                            "scene_id": best_match.scene["id"],
                            "scene_title": best_match.scene.get("title", "Untitled"),
                            "confidence": best_match.score,
                            "reasons": best_match.reasons,
                        }
                    )

        result = {
            "linked_count": linked_count,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions[:10],  # Limit to first 10
        }

        if self.settings.get("dryRun", False):
            result["message"] = f"DRY RUN: Would have linked {linked_count} galleries"
        else:
            result["message"] = f"Successfully linked {linked_count} galleries to scenes"

        return result

    def auto_link_performers(self) -> dict:
        """Automatically link performers to galleries."""
        self.logger.info("Starting auto-link performers process")

        # Get all galleries and performers
        galleries = self.stash.find_galleries()
        performers = self.stash.find_performers()

        if not galleries or not performers:
            return {"message": "No galleries or performers found"}

        linked_count = 0

        for gallery in galleries:
            gallery_path = gallery.get("path", {}).get("path", "") if gallery.get("path") else ""
            if not gallery_path:
                continue

            # Find performers in path
            found_performer_ids = self.extract_performers_from_path(gallery_path, performers)

            if found_performer_ids:
                existing_performer_ids = [p["id"] for p in gallery.get("performers", [])]
                new_performer_ids = list(set(existing_performer_ids + found_performer_ids))

                if len(new_performer_ids) > len(existing_performer_ids) and not self.settings.get("dryRun", False):
                    try:
                        self.stash.update_gallery({"id": gallery["id"], "performer_ids": new_performer_ids})
                        linked_count += 1
                        self.logger.info(f"Added performers to gallery '{gallery.get('title', gallery['id'])}'")
                    except Exception as e:
                        self.logger.error(f"Failed to update gallery {gallery['id']}: {e}")

        result = {"linked_count": linked_count, "message": ""}

        if self.settings.get("dryRun", False):
            result["message"] = f"DRY RUN: Would have updated {linked_count} galleries with performers"
        else:
            result["message"] = f"Successfully updated {linked_count} galleries with performers"

        return result

    def generate_report(self) -> dict:
        """Generate a report of gallery relationships."""
        self.logger.info("Generating linking report")

        galleries = self.stash.find_galleries()

        total_galleries = len(galleries)
        linked_to_scenes = sum(1 for g in galleries if g.get("scenes"))
        linked_to_performers = sum(1 for g in galleries if g.get("performers"))
        unlinked = sum(1 for g in galleries if not g.get("scenes") and not g.get("performers"))

        report = {
            "total_galleries": total_galleries,
            "linked_to_scenes": linked_to_scenes,
            "linked_to_performers": linked_to_performers,
            "unlinked": unlinked,
            "coverage_percentage": (
                round((total_galleries - unlinked) / total_galleries * 100, 2) if total_galleries > 0 else 0
            ),
        }

        return report


def main():
    """Define the main entry point for the plugin."""
    parser = argparse.ArgumentParser(description="Gallery Linker Plugin")
    parser.add_argument("--url", dest="stash_url", help="Stash URL")
    parser.add_argument("--api-key", dest="api_key", help="Stash API Key")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Enable dry run mode")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--mode",
        dest="mode",
        choices=["auto_link_scenes", "auto_link_performers", "generate_report"],
        default="auto_link_scenes",
        help="Operation mode",
    )
    parser.add_argument("--settings", dest="settings", help="JSON string of plugin settings")

    args = parser.parse_args()

    # Read from stdin for plugin mode
    plugin_input = None
    if not sys.stdin.isatty():
        with contextlib.suppress(json.JSONDecodeError):
            plugin_input = json.loads(sys.stdin.read())

    linker = GalleryLinker(args.stash_url, args.api_key)

    if plugin_input:
        linker.load_settings(plugin_input)
        mode = plugin_input.get("args", {}).get("mode", "auto_link_scenes")
    else:
        # Parse settings from command line argument if provided
        if args.settings:
            try:
                parsed_settings = parse_settings_argument(args.settings)
                # Create plugin_input structure to use existing load_settings method
                plugin_input = {"args": parsed_settings}
                linker.load_settings(plugin_input)
            except ValueError as e:
                print(f"Error parsing settings: {e}", file=sys.stderr)
                return 1

        mode = args.mode

    # Execute the requested operation
    try:
        if mode == "auto_link_scenes":
            result = linker.auto_link_scenes()
        elif mode == "auto_link_performers":
            result = linker.auto_link_performers()
        elif mode == "generate_report":
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
    """Entry point for the plugin."""
    sys.exit(main())
