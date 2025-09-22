# import sys
import json
from datatypes import SettingsSchema
from dataclasses import asdict


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
