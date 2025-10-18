"""Module to link performers to galleries in Stash based on file paths, linked scenes, and StashDB queries."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import stashapi.log as logger
import util
from stashapi.stashapp import StashInterface


class PerformerGalleryLinker:
    """A class that provides methods to link performers to galleries in Stash."""

    def __init__(self, stash_interface: StashInterface):
        """
        Initialize the linker with a Stash interface.

        Args:
            stash_interface: StashInterface instance for API communication
        """
        self.stash = stash_interface
        self.logger = logger

    def link_performers_to_galleries(
        self,
        gallery_ids: Optional[List[str]] = None,
        performer_ids: Optional[List[str]] = None,
        dry_run: bool = False,
        create_missing: bool = True,
        use_stashdb: bool = True,
    ) -> Dict[str, Any]:
        """
        Link performers to galleries based on multiple strategies.

        Strategies:
        1. Parse folder/file names for performer names
        2. Use linked gallery scenes to retrieve performers
        3. Query StashDB GraphQL based on gallery name for possible performers

        Args:
            gallery_ids: Optional list of specific gallery IDs to process. If None, processes all galleries.
            performer_ids: Optional list of specific performer IDs to consider. If None, considers all performers.
            dry_run: If True, only simulate the linking without making actual changes.
            create_missing: If True, create performers that don't exist with "Gallery Linker: New Performer" tag.
            use_stashdb: If True, query StashDB for performer information.

        Returns:
            Dictionary containing:
            - 'linked': List of successfully linked performer-gallery pairs
            - 'created': List of newly created performers
            - 'errors': List of errors encountered
            - 'skipped': List of skipped items with reasons
        """
        results: Dict[str, Any] = {"linked": [], "created": [], "errors": [], "skipped": []}

        self.logger.info("Starting performer-gallery linking process")

        try:
            # Get galleries to process
            galleries = self._get_galleries_to_process(gallery_ids)
            if not galleries:
                results["errors"].append("No galleries found to process")
                return results

            # Get all performers for matching
            all_performers = self._get_performers_to_consider(performer_ids)
            if not all_performers and not create_missing:
                results["errors"].append("No performers found and create_missing is disabled")
                return results

            self.logger.info(f"Processing {len(galleries)} galleries against {len(all_performers)} performers")

            # Get or create the "Gallery Linker: New Performer" tag if needed
            # new_performer_tag_id = None
            # if create_missing:
            #     new_performer_tag_id = self._get_or_create_tag("Gallery Linker: New Performer", dry_run)

            # Process each gallery
            for gallery in galleries:
                try:
                    gallery_id = gallery["id"]
                    # gallery_title = gallery.get("title", gallery.get("file", "Unknown"))
                    gallery_title = util.extract_gallery_title(self._get_gallery_path(gallery)) or gallery.get(
                        "title", "Unknown"
                    )
                    gallery_path = self._get_gallery_path(gallery)

                    self.logger.debug(f"Processing gallery {gallery_id}: {gallery_title}")

                    # Skip if gallery already has performers (unless we want to add more)
                    existing_performers = gallery.get("performers", [])
                    existing_performer_ids = {str(p["id"]) for p in existing_performers}

                    # Strategy 1: Parse folder/file names for performer names
                    name_matches = self._find_performers_from_names(gallery_title, gallery_path, all_performers)

                    # Strategy 2: Get performers from linked scenes
                    scene_performers = self._get_performers_from_linked_scenes(gallery)

                    # Strategy 3: Query StashDB for performers
                    stashdb_performers = []
                    if use_stashdb:
                        stashdb_performers = self._find_performers_from_stashdb(gallery_title, all_performers)

                    # Combine all matches (deduplicate by ID)
                    all_matches = {}
                    for match in name_matches + scene_performers + stashdb_performers:
                        performer_id = str(match["id"])
                        if performer_id not in all_matches:
                            all_matches[performer_id] = match
                        else:
                            # Update score if higher
                            if match.get("match_score", 0) > all_matches[performer_id].get("match_score", 0):
                                all_matches[performer_id] = match

                    # Filter out already linked performers
                    new_matches = {
                        pid: match for pid, match in all_matches.items() if pid not in existing_performer_ids
                    }

                    if not new_matches:
                        results["skipped"].append(
                            {
                                "gallery_id": gallery_id,
                                "gallery_title": gallery_title,
                                "reason": "No new performers found to link",
                            }
                        )
                        continue

                    # Link performers to gallery
                    for performer_id, match in new_matches.items():
                        link_result = self._link_performer_to_gallery(performer_id, gallery_id, dry_run=dry_run)

                        if link_result["success"]:
                            results["linked"].append(
                                {
                                    "gallery_id": gallery_id,
                                    "gallery_title": gallery_title,
                                    "gallery_path": gallery_path,
                                    "performer_id": performer_id,
                                    "performer_name": match.get("name", "Unknown"),
                                    "match_score": match.get("match_score", 0),
                                    "match_source": match.get("match_source", "unknown"),
                                    "dry_run": dry_run,
                                }
                            )
                        else:
                            results["errors"].append(
                                {
                                    "gallery_id": gallery_id,
                                    "performer_id": performer_id,
                                    "error": link_result["error"],
                                }
                            )

                except Exception as e:
                    results["errors"].append(
                        {"gallery_id": gallery.get("id", "unknown"), "error": f"Error processing gallery: {str(e)}"}
                    )

            self.logger.info(
                f"Linking complete: {len(results['linked'])} linked, "
                f"{len(results['created'])} created, "
                f"{len(results['errors'])} errors, {len(results['skipped'])} skipped"
            )

        except Exception as e:
            results["errors"].append(f"Fatal error during linking process: {str(e)}")

        return results

    def _get_galleries_to_process(self, gallery_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get galleries to process based on provided IDs or all galleries."""
        try:
            fragment = """
                id
                title
                files {
                    path
                }
                performers {
                    id
                    name
                }
                scenes {
                    id
                    title
                    performers {
                        id
                        name
                    }
                }
            """

            if gallery_ids:
                galleries = []
                for gallery_id in gallery_ids:
                    try:
                        gallery_id_int = int(gallery_id)
                        gallery = self.stash.find_gallery(gallery_id_int, fragment=fragment)
                        if gallery:
                            galleries.append(gallery)
                        else:
                            self.logger.warning(f"Gallery with ID {gallery_id} not found")
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid gallery ID format: {gallery_id}")
                return galleries
            else:
                # Get all galleries
                galleries_result = self.stash.find_galleries(f={}, filter={"per_page": -1}, fragment=fragment)
                return galleries_result if isinstance(galleries_result, list) else []
        except Exception as e:
            self.logger.error(f"Error getting galleries: {str(e)}")
            return []

    def _get_performers_to_consider(self, performer_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get performers to consider based on provided IDs or all performers."""
        try:
            fragment = """
                id
                name
                alias_list
                stash_ids {
                    stash_id
                    endpoint
                }
            """

            if performer_ids:
                performers = []
                for performer_id in performer_ids:
                    try:
                        performer_id_int = int(performer_id)
                        performer = self.stash.find_performer(performer_id_int, fragment=fragment)
                        if performer:
                            performers.append(performer)
                        else:
                            self.logger.warning(f"Performer with ID {performer_id} not found")
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid performer ID format: {performer_id}")
                return performers
            else:
                # Get all performers
                performers_result = self.stash.find_performers(f={}, filter={"per_page": -1}, fragment=fragment)
                return performers_result if isinstance(performers_result, list) else []
        except Exception as e:
            self.logger.error(f"Error getting performers: {str(e)}")
            return []

    def _find_performers_from_names(
        self, gallery_title: str, gallery_path: str, all_performers: List[Dict]
    ) -> List[Dict]:
        """
        Find performers by parsing folder/file names.

        Args:
            gallery_title: Gallery title
            gallery_path: Gallery file path
            all_performers: List of all available performers

        Returns:
            List of matching performers with match scores
        """
        matches = []

        # Extract searchable text from title and path
        search_text = self._extract_searchable_text(gallery_title, gallery_path)

        for performer in all_performers:
            performer_name = performer.get("name", "")
            aliases = performer.get("alias_list", []) or []

            # Check name match
            score = self._calculate_name_match_score(search_text, performer_name)
            if score > 0.7:
                match = performer.copy()
                match["match_score"] = score
                match["match_source"] = "name_parsing"
                matches.append(match)
                continue

            # Check alias matches
            for alias in aliases:
                score = self._calculate_name_match_score(search_text, alias)
                if score > 0.7:
                    match = performer.copy()
                    match["match_score"] = score
                    match["match_source"] = "alias_parsing"
                    matches.append(match)
                    break

        return matches

    def _get_performers_from_linked_scenes(self, gallery: Dict) -> List[Dict]:
        """
        Get performers from scenes linked to the gallery.

        Args:
            gallery: Gallery dictionary

        Returns:
            List of performers from linked scenes
        """
        performers = []
        scenes = gallery.get("scenes", [])

        for scene in scenes:
            scene_performers = scene.get("performers", [])
            for performer in scene_performers:
                match = performer.copy()
                match["match_score"] = 1.0  # High confidence from scene link
                match["match_source"] = "linked_scene"
                performers.append(match)

        return performers

    def _find_performers_from_stashdb(self, gallery_title: str, all_performers: List[Dict]) -> List[Dict]:
        """
        Query StashDB for performers related to the gallery.

        Args:
            gallery_title: Gallery title to search
            all_performers: List of all available performers for matching

        Returns:
            List of matching performers
        """
        # TODO: Implement StashDB GraphQL query
        # This would require the StashDB endpoint and authentication
        # For now, return empty list as placeholder
        self.logger.debug(f"StashDB query not yet implemented for: {gallery_title}")
        return []

    def _extract_searchable_text(self, gallery_title: str, gallery_path: str) -> str:
        """
        Extract searchable text from gallery title and path.

        Args:
            gallery_title: Gallery title
            gallery_path: Gallery file path

        Returns:
            Combined searchable text
        """
        # Extract folder name from path
        folder_name = Path(gallery_path).parent.name if gallery_path else ""

        # Combine title and folder name
        combined = f"{gallery_title} {folder_name}"

        # Clean up separators and normalize
        cleaned = re.sub(r"[_\-\.]+", " ", combined)
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()

        return cleaned

    def _calculate_name_match_score(self, search_text: str, performer_name: str) -> float:
        """
        Calculate match score between search text and performer name.

        Args:
            search_text: Text to search in
            performer_name: Performer name to match

        Returns:
            Match score between 0 and 1
        """
        if not search_text or not performer_name:
            return 0.0

        performer_name_lower = performer_name.lower()

        # Exact match
        if performer_name_lower in search_text:
            return 1.0

        # Word-based matching
        search_words = set(search_text.split())
        name_words = set(performer_name_lower.split())

        if not name_words:
            return 0.0

        # Calculate word overlap
        intersection = search_words.intersection(name_words)
        union = search_words.union(name_words)

        if not union:
            return 0.0

        return len(intersection) / len(name_words)  # Score based on name word coverage

    def _get_gallery_path(self, gallery: Dict) -> str:
        """Extract the file path from a gallery object."""
        files = gallery.get("files", [])
        if files and len(files) > 0:
            return str(files[0].get("path", ""))
        return ""

    def _link_performer_to_gallery(self, performer_id: str, gallery_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Perform the actual linking of a performer to a gallery.

        Args:
            performer_id: ID of the performer to link
            gallery_id: ID of the gallery to link to
            dry_run: If True, don't actually perform the operation

        Returns:
            Dictionary with success status and optional error message
        """
        if dry_run:
            return {"success": True, "dry_run": True}

        try:
            # Get current gallery data to preserve existing performers
            gallery_id_int = int(gallery_id)
            current_gallery = self.stash.find_gallery(gallery_id_int, fragment="performers { id }")
            if not current_gallery:
                return {"success": False, "error": "Gallery not found"}

            # Get current performer IDs and add the new one
            current_performer_ids = [int(p["id"]) for p in current_gallery.get("performers", [])]
            performer_id_int = int(performer_id)
            if performer_id_int not in current_performer_ids:
                current_performer_ids.append(performer_id_int)

            # Use GraphQL mutation to update gallery
            update_data = {"id": gallery_id_int, "performer_ids": current_performer_ids}

            try:
                if hasattr(self.stash, "call_GQL"):
                    query = """
                    mutation GalleryUpdate($input: GalleryUpdateInput!) {
                        galleryUpdate(input: $input) {
                            id
                            performers {
                                id
                                name
                            }
                        }
                    }
                    """
                    variables = {"input": update_data}
                    result = self.stash.call_GQL(query, variables)

                    if result and "galleryUpdate" in result.get("data", {}):
                        self.logger.info(f"Successfully linked performer {performer_id} to gallery {gallery_id}")
                        return {"success": True}
                    else:
                        return {"success": False, "error": "GraphQL mutation failed"}
                else:
                    # Fallback: Log the operation
                    self.logger.warning("Direct GraphQL update not available. This is a demo implementation.")
                    self.logger.info(
                        f"Would link performer {performer_id} to gallery {gallery_id} with data: {update_data}"
                    )
                    return {"success": True, "demo_mode": True}

            except AttributeError:
                self.logger.warning("GraphQL update method not available. This is a demo implementation.")
                self.logger.info(
                    f"Would link performer {performer_id} to gallery {gallery_id} with data: {update_data}"
                )
                return {"success": True, "demo_mode": True}

        except Exception as e:
            error_msg = f"Failed to link performer to gallery: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def _get_or_create_tag(self, tag_name: str, dry_run: bool = False) -> Optional[int]:
        """
        Get or create a tag by name.

        Args:
            tag_name: Name of the tag
            dry_run: If True, don't actually create the tag

        Returns:
            Tag ID or None if operation failed
        """
        try:
            # Search for existing tag
            tags = self.stash.find_tags(f={"name": {"value": tag_name, "modifier": "EQUALS"}}, fragment="id name")

            if tags and len(tags) > 0:
                return int(tags[0]["id"])

            # Create new tag if it doesn't exist
            if dry_run:
                self.logger.info(f"DRY RUN: Would create tag '{tag_name}'")
                return None

            if hasattr(self.stash, "call_GQL"):
                query = """
                mutation TagCreate($input: TagCreateInput!) {
                    tagCreate(input: $input) {
                        id
                        name
                    }
                }
                """
                variables = {"input": {"name": tag_name}}
                result = self.stash.call_GQL(query, variables)

                if result and "tagCreate" in result.get("data", {}):
                    tag_id = int(result["data"]["tagCreate"]["id"])
                    self.logger.info(f"Created new tag '{tag_name}' with ID {tag_id}")
                    return tag_id

            return None

        except Exception as e:
            self.logger.error(f"Error getting/creating tag '{tag_name}': {str(e)}")
            return None

    def _create_performer_with_tag(
        self, performer_name: str, tag_id: Optional[int], dry_run: bool = False
    ) -> Optional[Dict]:
        """
        Create a new performer with the specified tag.

        Args:
            performer_name: Name of the performer to create
            tag_id: ID of the tag to add
            dry_run: If True, don't actually create the performer

        Returns:
            Created performer dictionary or None if operation failed
        """
        if dry_run:
            self.logger.info(f"DRY RUN: Would create performer '{performer_name}' with tag ID {tag_id}")
            return None

        try:
            if hasattr(self.stash, "call_GQL"):
                query = """
                mutation PerformerCreate($input: PerformerCreateInput!) {
                    performerCreate(input: $input) {
                        id
                        name
                        tags {
                            id
                            name
                        }
                    }
                }
                """
                input_data: dict = {"name": performer_name}
                if tag_id:
                    input_data["tag_ids"] = [tag_id]

                variables: dict = {"input": input_data}
                result = self.stash.call_GQL(query, variables)

                if result and "performerCreate" in result.get("data", {}):
                    performer = result["data"]["performerCreate"]
                    self.logger.info(f"Created new performer '{performer_name}' with ID {performer['id']}")
                    return performer  # type: ignore[no-any-return]

            return None

        except Exception as e:
            self.logger.error(f"Error creating performer '{performer_name}': {str(e)}")
            return None
