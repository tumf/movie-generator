"""Test configuration loading."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.config import Config, load_config, merge_configs


def test_default_config() -> None:
    """Test loading default configuration."""
    config = Config()
    assert config.project.name == "My YouTube Channel"
    assert config.style.resolution == (1920, 1080)
    assert config.audio.speaker_id == 3


def test_load_config_from_file(tmp_path: Path) -> None:
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(
        """
project:
  name: "Test Project"
  output_dir: "./test_output"

style:
  resolution: [1280, 720]
  fps: 60
"""
    )

    config = load_config(config_file)
    assert config.project.name == "Test Project"
    assert config.project.output_dir == "./test_output"
    assert config.style.resolution == (1280, 720)
    assert config.style.fps == 60


def test_load_config_nonexistent_file() -> None:
    """Test loading from nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))


def test_merge_configs() -> None:
    """Test merging two configurations."""
    # Create configs with explicit dict construction
    from movie_generator.config import ProjectConfig, StyleConfig

    base = Config()
    base.project = ProjectConfig(name="Base Project", output_dir="./base")
    base.style = StyleConfig(fps=30)

    override = Config()
    override.project = ProjectConfig(name="Override Project")
    override.style = StyleConfig(fps=60)

    merged = merge_configs(base, override)
    assert merged.project.name == "Override Project"
    # Note: merge replaces entire project dict, so output_dir comes from override's default
    assert merged.style.fps == 60
