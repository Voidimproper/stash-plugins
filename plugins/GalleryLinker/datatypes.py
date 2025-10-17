"""Data types for GalleryLinker plugin."""

from dataclasses import dataclass, field


@dataclass
class SettingsSchema:
    """Schema for plugin settings."""

    autoLinkByDate: bool = field(default=False)
    dateTolerance: int = field(default=7)
    autoLinkByFilename: bool = field(default=False)
    performerLinking: bool = field(default=False)
    debugTracing: bool = field(default=False)
    dryRun: bool = field(default=False)
    overwriteExisting: bool = field(default=False)
    minimumScore: float = field(default=0.3)
    autoLinkThreshold: float = field(
        default=0.7,
    )

    def __post_init__(self):
        """Validate settings values."""
        if not (0 <= self.minimumScore <= 1):
            raise ValueError("minimumScore must be between 0 and 1")
        if not (0 <= self.autoLinkThreshold <= 1):
            raise ValueError("autoLinkThreshold must be between 0 and 1")
        if not (0 <= self.dateTolerance <= 365):
            raise ValueError("dateTolerance must be between 0 and 365")
