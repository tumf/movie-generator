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


class ConfigDefaults:
    """Default values and validation bounds for configuration.

    These constants centralize all magic numbers used in config.py,
    enabling consistent updates and better readability.
    """

    # Audio synthesis defaults
    AUDIO_ENGINE = "voicevox"
    AUDIO_SPEAKER_ID = 3  # Zundamon
    AUDIO_SPEED_SCALE = 1.0
    AUDIO_SPEED_SCALE_MIN = 0.0  # Exclusive minimum (gt=0.0)
    AUDIO_PRONUNCIATION_MODEL = "openai/gpt-4o-mini"

    # Narration timing defaults (seconds)
    NARRATION_CHARACTER = "ずんだもん"
    NARRATION_STYLE = "casual"
    NARRATION_INITIAL_PAUSE = 1.0
    NARRATION_SLIDE_PAUSE = 1.0
    NARRATION_ENDING_PAUSE = 1.0
    NARRATION_SPEAKER_PAUSE = 0.5

    # Video encoding defaults
    VIDEO_CRF_DEFAULT = 28
    VIDEO_CRF_MIN = 0
    VIDEO_CRF_MAX = 51

    # Video rendering defaults
    VIDEO_RENDERER = "remotion"
    VIDEO_TEMPLATE = "default"
    VIDEO_OUTPUT_FORMAT = "mp4"
    VIDEO_RENDER_CONCURRENCY = 4
    VIDEO_RENDER_TIMEOUT = 300  # seconds

    # Transition defaults
    TRANSITION_TYPE = "fade"
    TRANSITION_DURATION_FRAMES = 15
    TRANSITION_TIMING = "linear"

    # BGM defaults
    BGM_VOLUME_DEFAULT = 0.3
    BGM_VOLUME_MIN = 0.0
    BGM_VOLUME_MAX = 1.0
    BGM_FADE_IN_SECONDS = 2.0
    BGM_FADE_OUT_SECONDS = 2.0

    # Background defaults
    BACKGROUND_FIT = "cover"

    # LLM defaults
    LLM_PROVIDER = "openrouter"
    LLM_MODEL = "openai/gpt-5.2"
    LLM_BASE_URL = "https://openrouter.ai/api/v1"

    # Slides LLM defaults
    SLIDES_LLM_PROVIDER = "openrouter"
    SLIDES_LLM_MODEL = "google/gemini-3-pro-image-preview"
    SLIDES_LLM_BASE_URL = "https://openrouter.ai/api/v1"
    SLIDES_STYLE = "presentation"

    # Pronunciation defaults
    PRONUNCIATION_ACCENT = 0  # Auto-detect
    PRONUNCIATION_WORD_TYPE = "PROPER_NOUN"
    PRONUNCIATION_PRIORITY_DEFAULT = 10
    PRONUNCIATION_PRIORITY_MIN = 1
    PRONUNCIATION_PRIORITY_MAX = 10

    # Persona pool defaults
    PERSONA_POOL_COUNT = 2

    # Persona animation defaults
    PERSONA_ANIMATION_STYLE = "sway"

    # Style defaults
    STYLE_FONT_FAMILY = "Noto Sans JP"
    STYLE_PRIMARY_COLOR = "#FFFFFF"
    STYLE_BACKGROUND_COLOR = "#1a1a2e"

    # Project defaults
    PROJECT_NAME = "My YouTube Channel"
    PROJECT_OUTPUT_DIR = "./output"

    # Content generation defaults
    CONTENT_LANGUAGES_DEFAULT = ["ja"]
