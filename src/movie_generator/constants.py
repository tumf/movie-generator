"""Project-wide constants and configuration values."""

import os
from pathlib import Path


class VideoConstants:
    """Video rendering constants."""

    DEFAULT_FPS = 30
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720
    DEFAULT_CRF = 28  # Higher = smaller file, lower quality (18-28 typical range)
    MIN_WIDTH = 800  # Minimum acceptable width for images
    MIN_HEIGHT = 600  # Minimum acceptable height for images


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
    """Standard project directory names and file naming formats."""

    AUDIO = "audio"
    SLIDES = "slides"
    REMOTION = "remotion"
    OUTPUT = "output"
    ASSETS = "assets"
    LOGOS = "logos"

    # File naming formats
    PHRASE_FILENAME_FORMAT = "phrase_{index:04d}.wav"
    SLIDE_FILENAME_FORMAT = "slide_{index:04d}.png"

    # Docker environment project root (overridable with PROJECT_ROOT env var)
    @staticmethod
    def get_docker_project_root() -> Path:
        """Get Docker project root from environment variable or default.

        Returns:
            Path to project root (/app by default, or from PROJECT_ROOT env var).
        """
        return Path(os.getenv("PROJECT_ROOT", "/app"))

    @staticmethod
    def get_project_root() -> Path:
        """Get project root based on environment.

        In Docker environment (DOCKER_ENV set), returns PROJECT_ROOT env var or /app.
        In local development, returns current working directory.

        Returns:
            Path to project root directory.
        """
        if os.getenv("DOCKER_ENV"):
            return ProjectPaths.get_docker_project_root()
        return Path.cwd()


class RetryConfig:
    """Retry operation configuration."""

    MAX_RETRIES = 3
    INITIAL_DELAY = 2.0  # seconds
    BACKOFF_FACTOR = 2.0


class TimingConstants:
    """Timing-related constants."""

    DEFAULT_TRANSITION_DURATION_FRAMES = 15  # 0.5s at 30fps
    DEFAULT_SLIDE_MIN_DURATION = 2.0  # seconds


class TimeoutConstants:
    """Timeout values for various operations (in seconds).

    These constants consolidate timeout settings across the codebase
    to enable consistent adjustments for different environments
    (production, testing, etc.).
    """

    # HTTP/Network operations
    HTTP_DEFAULT = 30.0  # Default HTTP request timeout
    HTTP_EXTENDED = 180.0  # Extended timeout for large content (e.g., long articles)
    HTTP_IMAGE_GENERATION = 120.0  # Image generation requests

    # MCP protocol operations
    MCP_DEFAULT = 30.0  # Default MCP request timeout

    # Asset downloads
    ASSET_DOWNLOAD = 30.0  # Logo/asset download timeout

    # Video rendering
    VIDEO_RENDER_DOWNLOAD = 300.0  # Remotion bundle download (5 minutes)
