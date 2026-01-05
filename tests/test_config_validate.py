"""Tests for config validation functionality."""

from pathlib import Path
from textwrap import dedent

import pytest

from movie_generator.config import validate_config


class TestConfigValidation:
    """Test configuration validation function."""

    def test_valid_config(self, tmp_path: Path) -> None:
        """Test validation of a valid configuration file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                project:
                  name: "Test Project"
                  output_dir: "./output"
                
                audio:
                  engine: "voicevox"
                  speaker_id: 3
                  speed_scale: 1.0
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test validation of non-existent file."""
        config_file = tmp_path / "nonexistent.yaml"

        result = validate_config(config_file)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "File not found" in result.errors[0]

    def test_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        """Test validation of file with invalid YAML syntax."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text(
            dedent("""
                project:
                  name: "Test
                  # Missing closing quote
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert "YAML parse error" in result.errors[0]

    def test_invalid_schema(self, tmp_path: Path) -> None:
        """Test validation of file with schema violations."""
        config_file = tmp_path / "invalid_schema.yaml"
        config_file.write_text(
            dedent("""
                audio:
                  speaker_id: "not_a_number"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("speaker_id" in error for error in result.errors)

    def test_missing_background_file(self, tmp_path: Path) -> None:
        """Test validation detects missing background file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                video:
                  background:
                    type: "image"
                    path: "/nonexistent/background.png"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert any("Background file not found" in error for error in result.errors)

    def test_missing_bgm_file(self, tmp_path: Path) -> None:
        """Test validation detects missing BGM file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                video:
                  bgm:
                    path: "/nonexistent/bgm.mp3"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert any("BGM file not found" in error for error in result.errors)

    def test_duplicate_persona_ids(self, tmp_path: Path) -> None:
        """Test validation detects duplicate persona IDs."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                personas:
                  - id: "zundamon"
                    name: "ずんだもん"
                    synthesizer:
                      engine: "voicevox"
                      speaker_id: 3
                  - id: "zundamon"
                    name: "ずんだもん2号"
                    synthesizer:
                      engine: "voicevox"
                      speaker_id: 4
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert any("Duplicate persona ID" in error for error in result.errors)

    def test_missing_character_image(self, tmp_path: Path) -> None:
        """Test validation detects missing character image."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                personas:
                  - id: "zundamon"
                    name: "ずんだもん"
                    synthesizer:
                      engine: "voicevox"
                      speaker_id: 3
                    character_image: "/nonexistent/character.png"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert not result.is_valid
        assert any("Character image not found" in error for error in result.errors)

    def test_missing_optional_images_warning(self, tmp_path: Path) -> None:
        """Test validation warns about missing optional character images."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                personas:
                  - id: "zundamon"
                    name: "ずんだもん"
                    synthesizer:
                      engine: "voicevox"
                      speaker_id: 3
                    mouth_open_image: "/nonexistent/mouth.png"
                    eye_close_image: "/nonexistent/eye.png"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        # These are warnings, not errors
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("Mouth open image not found" in warning for warning in result.warnings)
        assert any("Eye close image not found" in warning for warning in result.warnings)

    def test_relative_paths_resolved(self, tmp_path: Path) -> None:
        """Test validation resolves relative paths from config directory."""
        # Create actual files
        bg_file = tmp_path / "background.png"
        bg_file.write_text("fake image", encoding="utf-8")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            dedent("""
                video:
                  background:
                    type: "image"
                    path: "background.png"
            """),
            encoding="utf-8",
        )

        result = validate_config(config_file)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_empty_config_file(self, tmp_path: Path) -> None:
        """Test validation of empty configuration file."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("", encoding="utf-8")

        result = validate_config(config_file)

        assert not result.is_valid
        assert any("empty" in error.lower() for error in result.errors)
