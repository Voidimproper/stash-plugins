import sys
import json


def parse_settings_argument(settings_json: str) -> dict:
    """Parse settings JSON string into object using schema from gallery_linker.yml."""
    if not settings_json:
        return _get_default_settings()

    try:
        settings = json.loads(settings_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in settings argument: {e}") from e

    expected_settings = _get_settings_schema()
    parsed_settings = {}

    for key, config in expected_settings.items():
        value = settings.get(key, config["default"])
        parsed_settings[key] = _validate_and_convert_setting(key, value, config)

    # Log any unexpected settings
    unexpected_keys = set(settings.keys()) - set(expected_settings.keys())
    if unexpected_keys:
        print(f"Warning: Unexpected settings keys: {unexpected_keys}", file=sys.stderr)

    return parsed_settings


def _get_settings_schema() -> dict:
    """Get the settings schema definition."""
    return {
        "autoLinkByDate": {"type": "boolean", "default": False},
        "dateTolerance": {"type": "number", "default": 7, "min": 0, "max": 365},
        "autoLinkByFilename": {"type": "boolean", "default": False},
        "performerLinking": {"type": "boolean", "default": False},
        "debugTracing": {"type": "boolean", "default": False},
        "dryRun": {"type": "boolean", "default": False},
        "overwriteExisting": {"type": "boolean", "default": False},
        "minimumScore": {"type": "number", "default": 0.3, "min": 0.0, "max": 1.0},
        "autoLinkThreshold": {"type": "number", "default": 0.7, "min": 0.0, "max": 1.0},
    }


def _get_default_settings() -> dict:
    """Get default settings values."""
    schema = _get_settings_schema()
    return {key: config["default"] for key, config in schema.items()}


def _validate_and_convert_setting(key: str, value, config: dict):
    """Validate and convert a single setting value."""
    if config["type"] == "boolean":
        return _convert_to_boolean(key, value)
    elif config["type"] == "number":
        return _convert_to_number(key, value, config)
    else:
        raise ValueError(f"Unknown setting type '{config['type']}' for key '{key}'")


def _convert_to_boolean(key: str, value) -> bool:
    """Convert value to boolean with validation."""
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    elif isinstance(value, (int, float)):
        return bool(value)
    else:
        raise ValueError(f"Setting '{key}' must be a boolean value, got {type(value)}")


def _convert_to_number(key: str, value, config: dict):
    """Convert value to number with validation and range checking."""
    if isinstance(value, (int, float)):
        result = value
    elif isinstance(value, str):
        try:
            result = float(value) if "." in value else int(value)
        except ValueError as e:
            raise ValueError(f"Setting '{key}' must be a number, got '{value}'") from e
    else:
        raise ValueError(f"Setting '{key}' must be a number, got {type(value)}")

    # Range validation
    if "min" in config and result < config["min"]:
        raise ValueError(f"Setting '{key}' must be >= {config['min']}, got {result}")
    if "max" in config and result > config["max"]:
        raise ValueError(f"Setting '{key}' must be <= {config['max']}, got {result}")

    return result
