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


@dataclass
class MatchResult:
    """Represents a matching result between a gallery and scene."""

    scene: dict
    score: float
    reasons: list[str]

    def __post_init__(self):
        """Validate score is between 0 and 1."""
        if self.score < 0 or self.score > 1:
            raise ValueError("Score must be between 0 and 1")


@dataclass
class ScoringConfig:
    """Configuration for scoring algorithm."""

    title_similarity_weight: float = 0.4
    date_match_weight: float = 0.3
    filename_similarity_weight: float = 0.2
    performer_overlap_weight: float = 0.1

    title_similarity_threshold: float = 0.7
    filename_similarity_threshold: float = 0.6
    default_minimum_score: float = 0.3
    default_auto_link_threshold: float = 0.7

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total_weight = (
            self.title_similarity_weight
            + self.date_match_weight
            + self.filename_similarity_weight
            + self.performer_overlap_weight
        )
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
