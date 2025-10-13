"""
Gallery Linker Plugin for Stash.

Links image galleries to related scenes and performers based on file patterns, dates, and metadata.
"""

import argparse
import contextlib
import json
import logging
import sys

from void_common.util import parse_settings_argument

try:
    # import stashapi.log as logger
    from stashapi.stashapp import StashInterface
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies: pip install stashapp-tools requests")
    sys.exit(1)


class GalleryLinker:
    """Main class for Gallery Linker Plugin."""

    stash: StashInterface
    settings: dict
    logger: logging.Logger

    def __init__(self, stash_url: str | None = None, api_key: str | None = None):
        """Initialize the GalleryLinker with Stash connection details."""
        default_config = self._build_default_config()

        if stash_url or api_key:
            self._update_config_from_params(default_config, stash_url, api_key)

        self.stash = StashInterface(default_config)
        self.settings = parse_settings_argument("")
        self.logger = self._setup_logger()

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

    def _normalize_string(self, text: str) -> str:
        """Normalize string for comparison."""
        return text.lower().strip()

    def find_matching_scenes(self, gallery, scenes):
        """Find scenes that could match the gallery with input validation and optimizations."""
        pass

    def auto_link_scenes(self):
        """Automatically link galleries to scenes."""
        pass

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
    linker.logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    linker.logger.debug(f"Plugin input: {plugin_input}")
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
    linker.logger.debug(f"Settings: {linker.settings}")
    linker.logger.debug(f"Mode: {mode}")
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
