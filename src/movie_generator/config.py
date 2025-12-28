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


class ContentConfig(BaseModel):
    """Content generation configuration."""

    llm_provider: str = Field(default="openrouter")
    model: str = Field(default="gemini-3-pro")


class SlidesConfig(BaseModel):
    """Slide generation configuration."""

    provider: str = Field(default="openrouter")
    model: str = Field(default="nonobananapro")
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
