"""Project-wide constants and configuration values."""


class VideoConstants:
    """Video rendering constants."""

    DEFAULT_FPS = 30
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    DEFAULT_CRF = 28  # Higher = smaller file, lower quality (18-28 typical range)


class SubtitleConstants:
    """Subtitle styling constants.

    IMPORTANT: This is the Single Source of Truth for subtitle default values.
    All modules (config.py, remotion_renderer.py, templates.py) MUST use these constants.
    Do NOT hardcode color values elsewhere to prevent regression.

    Design Decision:
    - Default color is WHITE (#FFFFFF) for single-speaker mode
    - Multi-speaker mode uses persona-specific colors from config
    - If a persona has no color defined, WHITE is used as fallback
    """

    DEFAULT_COLOR = "#FFFFFF"  # White - neutral default for all modes


class FileExtensions:
    """Supported file extensions."""

    YAML = {".yaml", ".yml"}
    IMAGE = {".png", ".jpg", ".jpeg"}
    AUDIO = {".wav", ".mp3"}
    VIDEO = {".mp4", ".mov"}


class ProjectPaths:
    """Standard project directory names."""

    AUDIO = "audio"
    SLIDES = "slides"
    REMOTION = "remotion"
    OUTPUT = "output"
    ASSETS = "assets"
    LOGOS = "logos"


class RetryConfig:
    """Retry operation configuration."""

    MAX_RETRIES = 3
    INITIAL_DELAY = 2.0  # seconds
    BACKOFF_FACTOR = 2.0


class TimingConstants:
    """Timing-related constants."""

    DEFAULT_TRANSITION_DURATION_FRAMES = 15  # 0.5s at 30fps
    DEFAULT_SLIDE_MIN_DURATION = 2.0  # seconds
