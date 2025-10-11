"""Utility functions for GalleryLinker plugin."""

import json
from dataclasses import asdict

from .datatypes import SettingsSchema


def parse_settings_argument(settings_json: str) -> dict:
    """Parse settings JSON string into object using schema from gallery_linker.yml."""
    if not settings_json:
        return asdict(SettingsSchema())

    try:
        settings = json.loads(settings_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in settings argument: {e}") from e

    try:
        parsed_settings = SettingsSchema(**settings)
    except TypeError as e:
        raise ValueError(f"Invalid settings structure: {e}") from e

    return asdict(parsed_settings)


class Filters:
    """Filter definitions for gallery linking."""

    @staticmethod
    def null_galleries():
        """Filter for galleries without any scenes or performers."""
        return {"galleries": {"modifier": "IS_NULL"}}

    @staticmethod
    def null_performers():
        """Filter for performers without any scenes or galleries."""
        return {"performers": {"modifier": "IS_NULL"}}

    @staticmethod
    def null_scenes():
        """Filter for scenes without any galleries or performers."""
        return {"scenes": {"modifier": "IS_NULL"}}

    @staticmethod
    def equal(field: str, value):
        """Filter for a generic value."""
        return {field: {"value": value, "modifier": "EQUALS"}}


FILTERS = Filters()
