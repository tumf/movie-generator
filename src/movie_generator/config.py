"""Configuration management for movie generator.

Loads and validates YAML configuration files using Pydantic.
"""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings

from .constants import SubtitleConstants
from .exceptions import ConfigurationError


class VoicevoxSynthesizerConfig(BaseModel):
    """VOICEVOX synthesizer configuration."""

    engine: Literal["voicevox"] = "voicevox"
    speaker_id: int = Field(ge=0, description="VOICEVOX speaker ID")
    speed_scale: float = Field(default=1.0, gt=0.0, description="Speech speed multiplier")


class PersonaConfig(BaseModel):
    """Persona (speaker) configuration for multi-speaker dialogue."""

    id: str = Field(description="Unique persona identifier (e.g., 'zundamon', 'metan')")
    name: str = Field(description="Display name for the persona")
    character: str = Field(
        default="", description="Character description for LLM prompt generation"
    )
    synthesizer: VoicevoxSynthesizerConfig = Field(description="Audio synthesizer settings")
    subtitle_color: str = Field(
        default=SubtitleConstants.DEFAULT_COLOR,
        description="Subtitle text color (hex). See SubtitleConstants for default.",
    )
    character_image: str | None = Field(
        default=None,
        description="Path to character base image (mouth closed, eyes open)",
    )
    character_position: Literal["left", "right", "center"] = Field(
        default="left",
        description=(
            "Character display position on screen. "
            "NOTE: This field is auto-assigned based on persona order during rendering. "
            "First persona -> left, second -> right, third+ -> center. "
            "Manual values in config are ignored."
        ),
    )
    mouth_open_image: str | None = Field(
        default=None, description="Path to character image with mouth open (for lip sync)"
    )
    eye_close_image: str | None = Field(
        default=None, description="Path to character image with eyes closed (for blinking)"
    )
    animation_style: Literal["bounce", "sway", "static"] = Field(
        default="sway", description="Character animation style"
    )

    @model_validator(mode="before")
    @classmethod
    def handle_avatar_image_alias(cls, data: Any) -> Any:
        """Support avatar_image as alias for character_image during validation."""
        if isinstance(data, dict):
            if "avatar_image" in data and "character_image" not in data:
                data = data.copy()
                data["character_image"] = data.pop("avatar_image")
        return data


class StyleConfig(BaseModel):
    """Visual style configuration."""

    resolution: tuple[int, int] = Field(default=(1920, 1080))
    fps: int = Field(default=30, ge=1)
    font_family: str = Field(default="Noto Sans JP")
    primary_color: str = Field(default="#FFFFFF")
    background_color: str = Field(default="#1a1a2e")


class AudioConfig(BaseModel):
    """Audio generation configuration."""

    engine: str = Field(default="voicevox")
    speaker_id: int = Field(default=3, ge=0)
    speed_scale: float = Field(default=1.0, gt=0.0)
    enable_furigana: bool = Field(
        default=True,
        description="Enable automatic furigana generation using morphological analysis",
    )


class NarrationConfig(BaseModel):
    """Narration style configuration."""

    character: str = Field(default="ずんだもん")
    style: str = Field(default="casual")
    initial_pause: float = Field(
        default=1.0,
        description="Initial pause duration (seconds) before the first phrase. "
        "Useful to show the first slide before narration starts.",
    )
    slide_pause: float = Field(
        default=1.0,
        description="Pause duration (seconds) when transitioning between slides/sections. "
        "Set to 0 to disable.",
    )
    ending_pause: float = Field(
        default=1.0,
        description="Pause duration (seconds) after the last phrase ends. "
        "Keeps the final slide visible for viewers to absorb information.",
    )
    speaker_pause: float = Field(
        default=0.5,
        description="Pause duration (seconds) between speaker changes in dialogue mode. "
        "Set to 0 to disable.",
    )


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="openrouter")
    model: str = Field(default="openai/gpt-5.2")


class ContentConfig(BaseModel):
    """Content generation configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    languages: list[str] = Field(
        default=["ja"], description="Languages for content generation (e.g., ['ja', 'en'])"
    )


class SlidesLLMConfig(BaseModel):
    """LLM configuration for slide generation."""

    provider: str = Field(default="openrouter")
    # NOTE: DO NOT change this model. gemini-3-pro-image-preview is the correct model.
    # Do NOT use gemini-2.5-flash-image-preview or any other model.
    model: str = Field(default="google/gemini-3-pro-image-preview")


class SlidesConfig(BaseModel):
    """Slide generation configuration."""

    llm: SlidesLLMConfig = Field(default_factory=SlidesLLMConfig)
    style: str = Field(default="presentation")


class TransitionConfig(BaseModel):
    """Transition configuration for slide changes."""

    type: str = Field(
        default="fade",
        description="Transition type: fade, slide, wipe, flip, clockWipe, none",
    )
    duration_frames: int = Field(default=15, ge=1, description="Transition duration in frames")
    timing: str = Field(default="linear", description="Timing function: linear, spring")

    def model_post_init(self, __context: Any) -> None:
        """Validate transition type."""
        valid_types = {"fade", "slide", "wipe", "flip", "clockWipe", "none"}
        if self.type not in valid_types:
            raise ConfigurationError(
                f"Invalid transition type '{self.type}'. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )

        valid_timings = {"linear", "spring"}
        if self.timing not in valid_timings:
            raise ConfigurationError(
                f"Invalid timing function '{self.timing}'. "
                f"Must be one of: {', '.join(sorted(valid_timings))}"
            )


class BackgroundConfig(BaseModel):
    """Background configuration for video rendering."""

    type: Literal["image", "video"] = Field(description="Background type: image or video")
    path: str = Field(description="Path to background file (relative or absolute)")
    fit: Literal["cover", "contain", "fill"] = Field(
        default="cover",
        description="How to fit background: cover (fill maintaining aspect), "
        "contain (fit inside), fill (stretch)",
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate background file existence."""
        bg_path = Path(self.path)
        if not bg_path.is_absolute():
            # Relative paths will be resolved from project root later
            return

        if not bg_path.exists():
            raise ConfigurationError(f"Background file not found: {self.path}")

        # Validate file extension matches type
        image_exts = {".png", ".jpg", ".jpeg", ".webp"}
        video_exts = {".mp4", ".webm", ".mov"}

        ext = bg_path.suffix.lower()
        if self.type == "image" and ext not in image_exts:
            raise ConfigurationError(
                f"Invalid image extension '{ext}'. Expected: {', '.join(sorted(image_exts))}"
            )
        elif self.type == "video" and ext not in video_exts:
            raise ConfigurationError(
                f"Invalid video extension '{ext}'. Expected: {', '.join(sorted(video_exts))}"
            )


class BgmConfig(BaseModel):
    """Background music configuration."""

    path: str = Field(description="Path to BGM audio file (relative or absolute)")
    volume: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="BGM volume (0.0-1.0, default 0.3 to avoid overpowering narration)",
    )
    fade_in_seconds: float = Field(default=2.0, ge=0.0, description="Fade-in duration in seconds")
    fade_out_seconds: float = Field(default=2.0, ge=0.0, description="Fade-out duration in seconds")
    loop: bool = Field(default=True, description="Loop BGM if shorter than video duration")

    def model_post_init(self, __context: Any) -> None:
        """Validate BGM file existence."""
        bgm_path = Path(self.path)
        if not bgm_path.is_absolute():
            # Relative paths will be resolved from project root later
            return

        if not bgm_path.exists():
            raise ConfigurationError(f"BGM file not found: {self.path}")

        # Validate audio file extension
        audio_exts = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}
        ext = bgm_path.suffix.lower()
        if ext not in audio_exts:
            raise ConfigurationError(
                f"Invalid audio extension '{ext}'. Expected: {', '.join(sorted(audio_exts))}"
            )


class VideoConfig(BaseModel):
    """Video rendering configuration."""

    renderer: str = Field(default="remotion")
    template: str = Field(default="default")
    output_format: str = Field(default="mp4")
    transition: TransitionConfig = Field(default_factory=TransitionConfig)
    background: BackgroundConfig | None = Field(
        default=None, description="Optional background image/video for entire video"
    )
    bgm: BgmConfig | None = Field(default=None, description="Optional background music")


class PronunciationWord(BaseModel):
    """Pronunciation dictionary entry."""

    reading: str = Field(description="Katakana reading")
    accent: int = Field(default=0, ge=0, description="Accent position (0=auto)")
    word_type: str = Field(default="PROPER_NOUN")
    priority: int = Field(default=10, ge=1, le=10)


class PronunciationConfig(BaseModel):
    """Pronunciation dictionary configuration."""

    custom: dict[str, PronunciationWord | str] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    name: str = Field(default="My YouTube Channel")
    output_dir: str = Field(default="./output")


class Config(BaseSettings):
    """Main configuration model."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    narration: NarrationConfig = Field(default_factory=NarrationConfig)
    content: ContentConfig = Field(default_factory=ContentConfig)
    slides: SlidesConfig = Field(default_factory=SlidesConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    pronunciation: PronunciationConfig = Field(default_factory=PronunciationConfig)
    personas: list[PersonaConfig] = Field(
        default_factory=list, description="Persona configurations for multi-speaker dialogue"
    )

    @field_validator("personas")
    @classmethod
    def validate_unique_persona_ids(cls, personas: list[PersonaConfig]) -> list[PersonaConfig]:
        """Validate that persona IDs are unique."""
        if not personas:
            return personas

        ids = [p.id for p in personas]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            raise ConfigurationError(
                f"Duplicate persona IDs found: {', '.join(set(duplicates))}. "
                "Each persona must have a unique ID."
            )
        return personas


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML config file. If None, uses defaults.

    Returns:
        Validated Config object.

    Raises:
        FileNotFoundError: If config_path is specified but doesn't exist.
        yaml.YAMLError: If YAML parsing fails.
        pydantic.ValidationError: If config validation fails.
    """
    if config_path is None:
        return Config()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    return Config(**data)


def merge_configs(base: Config, override: Config) -> Config:
    """Merge two configurations, with override taking precedence.

    Args:
        base: Base configuration.
        override: Override configuration.

    Returns:
        Merged configuration.
    """
    base_dict = base.model_dump()
    override_dict = override.model_dump()

    # Deep merge dictionaries
    def deep_merge(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
        result = d1.copy()
        for key, value in d2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    merged = deep_merge(base_dict, override_dict)
    return Config(**merged)


def generate_default_config_yaml() -> str:
    """Generate default configuration as YAML with helpful comments.

    Returns:
        YAML string with inline comments explaining each field.
    """
    yaml_lines = [
        "# Default configuration for movie-generator",
        "",
        "# Project settings",
        "project:",
        '  name: "My YouTube Channel"  # Your channel name',
        '  output_dir: "./output"  # Directory for generated files',
        "",
        "# Video style settings",
        "style:",
        "  resolution: [1920, 1080]  # Video resolution (width, height)",
        "  fps: 30  # Frames per second",
        '  font_family: "Noto Sans JP"  # Font for text overlays',
        '  primary_color: "#FFFFFF"  # Primary text color (hex)',
        '  background_color: "#1a1a2e"  # Background color (hex)',
        "",
        "# Audio generation settings",
        "audio:",
        '  engine: "voicevox"  # Audio synthesis engine',
        "  speaker_id: 3  # VOICEVOX speaker ID (3 = Zundamon)",
        "  speed_scale: 1.0  # Speech speed multiplier (1.0 = normal)",
        "  enable_furigana: true  # Auto-generate furigana using morphological analysis",
        "",
        "# Narration style settings",
        "narration:",
        '  character: "ずんだもん"  # Narrator character name (used when no personas defined)',
        '  style: "casual"  # Narration style: casual, formal, educational',
        "",
        "# Persona configurations for multi-speaker dialogue",
        "# Uncomment and configure for dialogue mode",
        "# personas:",
        '#   - id: "zundamon"',
        '#     name: "ずんだもん"',
        '#     character: "元気で明るい東北の妖精"',
        "#     synthesizer:",
        '#       engine: "voicevox"',
        "#       speaker_id: 3",
        "#       speed_scale: 1.0",
        '#     subtitle_color: "#8FCF4F"',
        '#     character_image: "assets/characters/zundamon/base.png"  # Base character image',
        '#     character_position: "left"  # Position: left, right, center',
        '#     mouth_open_image: "assets/characters/zundamon/mouth_open.png"  # For lip sync',
        '#     eye_close_image: "assets/characters/zundamon/eye_close.png"  # For blinking',
        '#     animation_style: "sway"  # Animation style: bounce, sway, static',
        '#   - id: "metan"',
        '#     name: "四国めたん"',
        '#     character: "優しくて落ち着いた四国の妖精"',
        "#     synthesizer:",
        '#       engine: "voicevox"',
        "#       speaker_id: 2",
        "#       speed_scale: 1.0",
        '#     subtitle_color: "#FF69B4"',
        '#     character_image: "assets/characters/metan/base.png"',
        '#     character_position: "right"',
        "",
        "# Content generation settings",
        "content:",
        "  llm:",
        '    provider: "openrouter"  # LLM provider for script generation',
        '    model: "openai/gpt-5.2"  # Model to use for content generation',
        '  languages: ["ja"]  # Languages for content generation (e.g., ["ja", "en"])',
        "",
        "# Slide generation settings",
        "slides:",
        "  llm:",
        '    provider: "openrouter"  # LLM provider for slide generation',
        '    model: "google/gemini-3-pro-image-preview"  # Model for slide images',
        '  style: "presentation"  # Slide style: presentation, illustration, minimal',
        "",
        "# Video rendering settings",
        "video:",
        '  renderer: "remotion"  # Video rendering engine',
        '  template: "default"  # Video template to use',
        '  output_format: "mp4"  # Output video format',
        "  transition:",
        '    type: "fade"  # Transition type: fade, slide, wipe, flip, clockWipe, none',
        "    duration_frames: 15  # Transition duration in frames (0.5s at 30fps)",
        '    timing: "linear"  # Timing function: linear, spring',
        "  background:",
        '    type: "video"  # Background type: image or video',
        '    path: "assets/backgrounds/default-background.mp4"  # Path to background file',
        '    fit: "cover"  # How to fit: cover (fill), contain (fit inside), fill (stretch)',
        "  bgm:",
        '    path: "assets/bgm/default-bgm.mp3"  # Path to background music file',
        "    volume: 0.3  # BGM volume (0.0-1.0, default 0.3 to avoid overpowering narration)",
        "    fade_in_seconds: 2.0  # Fade-in duration in seconds",
        "    fade_out_seconds: 2.0  # Fade-out duration in seconds",
        "    loop: true  # Loop BGM if shorter than video duration",
        "",
        "# Pronunciation dictionary for proper nouns and technical terms",
        "pronunciation:",
        "  custom:",
        '    "Bubble Tea":',
        '      reading: "バブルティー"  # Katakana reading',
        "      accent: 5  # Accent position (0 = auto)",
        '      word_type: "PROPER_NOUN"  # Word type',
        "      priority: 10  # Priority (1-10, higher = more important)",
        '    "Ratatui":',
        '      reading: "ラタトゥイ"',
        "      accent: 4",
        '      word_type: "PROPER_NOUN"',
        "      priority: 10",
    ]
    return "\n".join(yaml_lines)


def write_config_to_file(output_path: Path, overwrite: bool = False) -> None:
    """Write default configuration to a file.

    Args:
        output_path: Path where config file should be written.
        overwrite: If True, overwrite existing file without confirmation.

    Raises:
        FileExistsError: If file exists and overwrite is False.
        OSError: If unable to write to the specified path.
    """
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {output_path}")

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write config
    config_yaml = generate_default_config_yaml()
    output_path.write_text(config_yaml, encoding="utf-8")


def print_default_config() -> None:
    """Print default configuration to stdout."""
    print(generate_default_config_yaml())


class ValidationResult:
    """Result of configuration validation."""

    def __init__(self) -> None:
        """Initialize validation result."""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


def validate_config(config_path: Path) -> ValidationResult:
    """Validate configuration file.

    Performs the following checks:
    1. YAML syntax validation
    2. Pydantic schema validation
    3. Referenced file existence (background, BGM, character images)
    4. Persona ID uniqueness

    Args:
        config_path: Path to configuration file to validate.

    Returns:
        ValidationResult with errors and warnings.
    """
    result = ValidationResult()

    # Check if file exists
    if not config_path.exists():
        result.add_error(f"File not found: {config_path}")
        return result

    # Step 1: YAML syntax check
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
    except yaml.YAMLError as e:
        error_msg = f"YAML parse error: {e}"
        # Try to include line number if available
        if hasattr(e, "problem_mark"):
            mark = getattr(e, "problem_mark")
            if mark and hasattr(mark, "line") and hasattr(mark, "column"):
                error_msg += f" (line {mark.line + 1}, column {mark.column + 1})"
        result.add_error(error_msg)
        return result
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    if data is None:
        result.add_error("Configuration file is empty")
        return result

    # Step 2: Pydantic schema validation
    try:
        cfg = Config(**data)
    except Exception as e:
        # Format pydantic validation errors
        from pydantic import ValidationError

        if isinstance(e, ValidationError):
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                result.add_error(f"Invalid field '{field_path}': {error['msg']}")
        else:
            result.add_error(f"Schema validation error: {e}")
        return result

    # Step 3: Referenced file existence checks
    # Note: Relative paths are resolved from the config file's directory
    config_dir = config_path.parent

    # Check background file
    if cfg.video.background:
        bg_path = Path(cfg.video.background.path)
        if not bg_path.is_absolute():
            bg_path = config_dir / bg_path

        if not bg_path.exists():
            result.add_error(f"Background file not found: {cfg.video.background.path}")

    # Check BGM file
    if cfg.video.bgm:
        bgm_path = Path(cfg.video.bgm.path)
        if not bgm_path.is_absolute():
            bgm_path = config_dir / bgm_path

        if not bgm_path.exists():
            result.add_error(f"BGM file not found: {cfg.video.bgm.path}")

    # Check persona character images
    for persona in cfg.personas:
        if persona.character_image:
            img_path = Path(persona.character_image)
            if not img_path.is_absolute():
                img_path = config_dir / img_path

            if not img_path.exists():
                result.add_error(
                    f"Character image not found for persona '{persona.id}': {persona.character_image}"
                )

        if persona.mouth_open_image:
            img_path = Path(persona.mouth_open_image)
            if not img_path.is_absolute():
                img_path = config_dir / img_path

            if not img_path.exists():
                result.add_warning(
                    f"Mouth open image not found for persona '{persona.id}': {persona.mouth_open_image}"
                )

        if persona.eye_close_image:
            img_path = Path(persona.eye_close_image)
            if not img_path.is_absolute():
                img_path = config_dir / img_path

            if not img_path.exists():
                result.add_warning(
                    f"Eye close image not found for persona '{persona.id}': {persona.eye_close_image}"
                )

    # Step 4: Persona ID uniqueness (already checked by Pydantic, but we verify here too)
    # This is already validated by the field_validator in Config class, but we include it
    # for completeness and to provide a clear error message

    return result
