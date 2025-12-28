"""Configuration management for movie generator.

Loads and validates YAML configuration files using Pydantic.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


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


class NarrationConfig(BaseModel):
    """Narration style configuration."""

    character: str = Field(default="ずんだもん")
    style: str = Field(default="casual")


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="openrouter")
    model: str = Field(default="openai/gpt-5.2")


class ContentConfig(BaseModel):
    """Content generation configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)


class SlidesConfig(BaseModel):
    """Slide generation configuration."""

    llm: LLMConfig = Field(default_factory=lambda: LLMConfig(model="nonobananapro"))
    style: str = Field(default="presentation")


class VideoConfig(BaseModel):
    """Video rendering configuration."""

    renderer: str = Field(default="remotion")
    template: str = Field(default="default")
    output_format: str = Field(default="mp4")


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
        "",
        "# Narration style settings",
        "narration:",
        '  character: "ずんだもん"  # Narrator character name',
        '  style: "casual"  # Narration style: casual, formal, educational',
        "",
        "# Content generation settings",
        "content:",
        "  llm:",
        '    provider: "openrouter"  # LLM provider for script generation',
        '    model: "openai/gpt-5.2"  # Model to use for content generation',
        "",
        "# Slide generation settings",
        "slides:",
        "  llm:",
        '    provider: "openrouter"  # LLM provider for slide generation',
        '    model: "nonobananapro"  # Model for slide images',
        '  style: "presentation"  # Slide style: presentation, illustration, minimal',
        "",
        "# Video rendering settings",
        "video:",
        '  renderer: "remotion"  # Video rendering engine',
        '  template: "default"  # Video template to use',
        '  output_format: "mp4"  # Output video format',
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
