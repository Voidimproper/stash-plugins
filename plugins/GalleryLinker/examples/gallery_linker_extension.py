"""Example extension to the GalleryLinker plugin that adds scene linking functionality."""

# Integration with the existing GalleryLinker plugin pattern
import logging
from typing import Any, Dict

from GalleryLinker.scene_gallery_linker import SceneGalleryLinker


class GalleryLinkerExtension:
    """
    Extension to the existing GalleryLinker plugin that adds scene linking functionality.
    """

    def __init__(self, gallery_linker_instance):
        """
        Initialize with an existing GalleryLinker instance.

        Args:
            gallery_linker_instance: Instance of the main GalleryLinker class
        """
        self.gallery_linker = gallery_linker_instance
        self.stash = gallery_linker_instance.stash
        self.settings = gallery_linker_instance.settings
        self.logger = gallery_linker_instance.logger

        # Create the scene-gallery linker
        self.scene_gallery_linker = SceneGalleryLinker(self.stash)

    def auto_link_scenes_to_galleries(self) -> Dict[str, Any]:
        """
        Automatically link scenes to galleries using the configured settings.

        Returns:
            Dictionary with linking results and statistics
        """
        self.logger.info("Starting automatic scene-to-gallery linking")

        # Use settings from the main plugin
        dry_run = self.settings.get("dryRun", True)
        debug_tracing = self.settings.get("debugTracing", False)

        if debug_tracing:
            self.logger.setLevel(logging.DEBUG)

        # Get scenes without galleries
        scenes_without_galleries = self.gallery_linker.get_scenes_without_galleries()
        scene_ids = [scene["id"] for scene in scenes_without_galleries]

        results = {"linked": [], "errors": [], "skipped": [], "message": ""}
        if not scene_ids:
            self.logger.info("No scenes without galleries found")
            results["message"] = "No scenes without galleries found"
            return results

        # Perform the linking
        results = self.scene_gallery_linker.link_scenes_to_galleries_by_path(
            scene_ids=scene_ids,
            gallery_ids=None,  # Consider all galleries
            dry_run=dry_run,
            link_strategy="path_proximity",
        )

        # Add summary statistics
        results["total_scenes_processed"] = len(scene_ids)
        results["link_success_rate"] = len(results["linked"]) / len(scene_ids) * 100 if scene_ids else 0

        self.logger.info(
            f"Scene linking completed: {len(results['linked'])} linked, "
            f"{len(results['errors'])} errors, {len(results['skipped'])} skipped"
        )

        return results  # type: ignore[no-any-return]
