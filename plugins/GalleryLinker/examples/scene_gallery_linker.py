"""Example usage of the SceneGalleryLinker class."""

import logging

from GalleryLinker.scene_gallery_linker import SceneGalleryLinker
from stashapi.stashapp import StashInterface


def example_usage_1(stash: StashInterface):
    """
    Example usage of the SceneGalleryLinker class.
    """

    # Create the linker
    linker = SceneGalleryLinker(stash)

    # Example 1: Link specific scene to specific gallery
    result = linker.link_scene_to_gallery_by_ids(
        scene_id="3", gallery_id="1", dry_run=False  # Set to False to actually perform the operation
    )
    print(f"Direct linking result: {result}")


def example_usage_2(stash: StashInterface):
    """Example usage of the SceneGalleryLinker class."""
    # Create the linker
    linker = SceneGalleryLinker(stash)

    # Example 2: Auto-link scenes to galleries based on path proximity
    batch_result = linker.link_scenes_to_galleries_by_path(
        scene_ids=None,  # Process all scenes
        gallery_ids=None,  # Consider all galleries
        # dry_run=True,
        # link_strategy="path_proximity",
        link_strategy="name_similarity",
    )

    print("Batch linking results:")
    print(f"  Linked: {len(batch_result['linked'])}")
    print(f"  Errors: {len(batch_result['errors'])}")
    print(f"  Skipped: {len(batch_result['skipped'])}")
    print("Detailed linked items:")
    for linked in batch_result["linked"]:
        print(
            f"  Scene '{linked['scene_title']}' linked to Gallery '{linked['gallery_title']}' "
            f"(Score: {linked['match_score']:.2f}, Dry Run: {linked.get('dry_run', False)})"
        )

    print("Detailed errors:")
    for error in batch_result["errors"]:
        print(f"  {error}")

    print("Detailed skipped items:")
    for skipped in batch_result["skipped"]:
        print(f"  Scene ID {skipped['scene_id']}, Title: {skipped['scene_title']} skipped: {skipped['reason']}")


def example_usage_3(stash: StashInterface):
    """Example usage of the SceneGalleryLinker class."""
    # Create the linker
    linker = SceneGalleryLinker(stash)

    # Example 3: Link specific scenes with name similarity strategy
    specific_scenes = ["scene1", "scene2", "scene3"]
    name_result = linker.link_scenes_to_galleries_by_path(
        scene_ids=specific_scenes,
        gallery_ids=None,
        # dry_run=True,  # Actually perform the linking
        link_strategy="name_similarity",
    )

    # Print detailed results
    for linked in name_result["linked"]:
        print(
            f"Linked '{linked['scene_title']}' to '{linked['gallery_title']}' " f"(score: {linked['match_score']:.2f})"
        )


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Initialize Stash interface (assumes proper configuration)
    stash = StashInterface(
        {
            "scheme": "http",
            "host": "localhost",
            "port": 9999,
            # "api_key": "your-api-key-here",  # Optional, if authentication is required
        }
    )
    # Run example
    # example_usage_1(stash)
    example_usage_2(stash)
    # example_usage_3(stash)
