"""Project-wide constants and configuration values."""


class VideoConstants:
    """Video rendering constants."""

    DEFAULT_FPS = 30
    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080


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
