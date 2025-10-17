"""
Gallery Linker Plugin for Stash.

Links image galleries to related scenes and performers based on file patterns, dates, and metadata.
"""

import argparse
import contextlib
import json
import logging
import sys
from typing import Any

from GalleryLinker.scene_gallery_linker import SceneGalleryLinker
from GalleryLinker.util import parse_settings_argument

try:
    import stashapi.log as logger
    from stashapi.stashapp import StashInterface
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies: pip install stashapp-tools requests")
    sys.exit(1)


class GalleryLinker:
    """Main class for Gallery Linker Plugin."""

    stash: StashInterface
    settings: dict

    def __init__(self, stash_url: str | None = None, api_key: str | None = None):
        """Initialize the GalleryLinker with Stash connection details."""
        default_config = self._build_default_config()

        if stash_url or api_key:
            self._update_config_from_params(default_config, stash_url, api_key)

        self.stash = StashInterface(default_config)
        self.settings = parse_settings_argument("")
        self.logger = logger

    def _build_default_config(self) -> dict:
        """Build default Stash connection configuration."""
        return {
            "scheme": "http",
            "host": "localhost",
            "port": "9999",
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

    def load_settings(self, plugin_input: dict) -> None:
        """Load plugin settings from Stash input."""
        if "server_connection" in plugin_input:
            # Recreate StashInterface with server connection details
            self.stash = StashInterface(plugin_input["server_connection"])

        self.settings = plugin_input.get("args", {})

    def auto_link_scenes(self, link_strategy: str = "name_similarity", dry_run: bool = False) -> dict[str, Any]:
        """Automatically link galleries to scenes."""
        linker = SceneGalleryLinker(self.stash)

        batch_result = linker.link_scenes_to_galleries_by_path(
            scene_ids=None,  # Process all scenes
            gallery_ids=None,  # Consider all galleries
            dry_run=dry_run,
            link_strategy=link_strategy,
        )

        self.logger.info(f"Batch Linked: {len(batch_result['linked'])}")
        self.logger.info(f"Batch Errors: {len(batch_result['errors'])}")
        self.logger.info(f"Batch Skipped: {len(batch_result['skipped'])}")

        if self.logger.sl.level <= logging.DEBUG:
            self.logger.debug("Detailed linked items:")
            for linked in batch_result["linked"]:
                self.logger.debug(
                    f"  Scene '{linked['scene_title']}' linked to Gallery '{linked['gallery_title']}' "
                    f"(Score: {linked['match_score']:.2f}, Dry Run: {linked.get('dry_run', False)})"
                )

            self.logger.debug("Detailed errors:")
            for error in batch_result["errors"]:
                self.logger.debug(f"  {error}")

            self.logger.debug("Detailed skipped items:")
            for skipped in batch_result["skipped"]:
                self.logger.debug(
                    f"  Scene ID {skipped['scene_id']}, Title: {skipped['scene_title']} skipped: {skipped['reason']}"
                )
        return batch_result  # type: ignore[no-any-return]

    def auto_link_performers(self):
        """Automatically link performers to galleries."""
        pass

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
    logger.debug(f"Plugin input: {plugin_input}")
    if plugin_input:
        linker.load_settings(plugin_input)
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
    logger.debug(f"Settings: {linker.settings}")
    logger.debug(f"Mode: {mode}")
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

        logger.debug(result)

    except Exception as e:
        error_result = {"error": str(e)}
        logger.error(error_result)
        return 1

    return 0


if __name__ == "__main__":
    """Entry point for the plugin."""
    sys.exit(main())
