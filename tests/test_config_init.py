"""Tests for config init command."""

import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.cli import cli
from movie_generator.config import (
    generate_default_config_yaml,
    load_config,
    write_config_to_file,
)


class TestConfigInitCLI:
    """Test config init CLI command."""

    def test_init_stdout(self):
        """Test config init outputs to stdout by default."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "init"])

        assert result.exit_code == 0
        assert "# Default configuration for movie-generator" in result.output
        assert "project:" in result.output
        assert "style:" in result.output
        assert "audio:" in result.output

    def test_init_file_output(self, tmp_path):
        """Test config init writes to file with --output option."""
        runner = CliRunner()
        output_file = tmp_path / "test-config.yaml"

        result = runner.invoke(cli, ["config", "init", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Configuration written to" in result.output

        # Verify file content
        content = output_file.read_text()
        assert "# Default configuration for movie-generator" in content
        assert "project:" in content

    def test_init_file_output_short_option(self, tmp_path):
        """Test config init with -o short option."""
        runner = CliRunner()
        output_file = tmp_path / "test-config.yaml"

        result = runner.invoke(cli, ["config", "init", "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_init_overwrite_confirmation_decline(self, tmp_path):
        """Test config init prompts for confirmation when file exists."""
        runner = CliRunner()
        output_file = tmp_path / "existing-config.yaml"
        output_file.write_text("existing content")

        # Decline overwrite
        result = runner.invoke(cli, ["config", "init", "--output", str(output_file)], input="n\n")

        assert result.exit_code == 0
        assert "already exists" in result.output
        assert "Operation cancelled" in result.output
        # File should remain unchanged
        assert output_file.read_text() == "existing content"

    def test_init_overwrite_confirmation_accept(self, tmp_path):
        """Test config init overwrites when user confirms."""
        runner = CliRunner()
        output_file = tmp_path / "existing-config.yaml"
        output_file.write_text("existing content")

        # Accept overwrite
        result = runner.invoke(cli, ["config", "init", "--output", str(output_file)], input="y\n")

        assert result.exit_code == 0
        assert "Configuration written to" in result.output
        # File should be overwritten
        assert "# Default configuration for movie-generator" in output_file.read_text()

    def test_init_force_overwrite(self, tmp_path):
        """Test config init --force overwrites without confirmation."""
        runner = CliRunner()
        output_file = tmp_path / "existing-config.yaml"
        output_file.write_text("existing content")

        result = runner.invoke(cli, ["config", "init", "--output", str(output_file), "--force"])

        assert result.exit_code == 0
        assert "Configuration written to" in result.output
        # Should not prompt for confirmation
        assert "already exists" not in result.output
        # File should be overwritten
        assert "# Default configuration for movie-generator" in output_file.read_text()

    def test_init_invalid_path(self):
        """Test config init fails gracefully with invalid path."""
        runner = CliRunner()
        invalid_path = "/invalid/nonexistent/path/config.yaml"

        result = runner.invoke(cli, ["config", "init", "--output", invalid_path])

        assert result.exit_code != 0
        assert "Error" in result.output


class TestConfigGeneration:
    """Test configuration generation functions."""

    def test_generate_default_config_yaml(self):
        """Test default config YAML generation."""
        yaml_content = generate_default_config_yaml()

        # Should contain comments
        assert "# Default configuration for movie-generator" in yaml_content
        assert "# Project settings" in yaml_content
        assert "# Your channel name" in yaml_content

        # Should contain all sections
        assert "project:" in yaml_content
        assert "style:" in yaml_content
        assert "audio:" in yaml_content
        assert "narration:" in yaml_content
        assert "content:" in yaml_content
        assert "slides:" in yaml_content
        assert "video:" in yaml_content
        assert "pronunciation:" in yaml_content

    def test_generated_yaml_is_valid(self):
        """Test that generated YAML is valid and parseable."""
        yaml_content = generate_default_config_yaml()

        # Should be valid YAML
        data = yaml.safe_load(yaml_content)
        assert isinstance(data, dict)
        assert "project" in data
        assert "style" in data
        assert "audio" in data

    def test_generated_config_loads_successfully(self, tmp_path):
        """Test that generated config can be loaded with load_config."""
        output_file = tmp_path / "test-config.yaml"
        write_config_to_file(output_file, overwrite=False)

        # Should load without errors
        config = load_config(output_file)

        # Verify some default values
        assert config.project.name == "My YouTube Channel"
        assert config.project.output_dir == "./output"
        assert config.style.resolution == (1920, 1080)
        assert config.style.fps == 30
        assert config.audio.speaker_id == 3
        assert config.narration.character == "ずんだもん"

    def test_generated_config_matches_defaults(self, tmp_path):
        """Test that generated config matches default Config values."""
        output_file = tmp_path / "test-config.yaml"
        write_config_to_file(output_file, overwrite=False)

        loaded_config = load_config(output_file)
        default_config = load_config(None)

        # Compare all fields
        assert loaded_config.project == default_config.project
        assert loaded_config.style == default_config.style
        assert loaded_config.audio == default_config.audio
        assert loaded_config.narration == default_config.narration
        assert loaded_config.content == default_config.content
        assert loaded_config.slides == default_config.slides
        assert loaded_config.video == default_config.video

    def test_write_config_to_file(self, tmp_path):
        """Test write_config_to_file function."""
        output_file = tmp_path / "config.yaml"
        write_config_to_file(output_file, overwrite=False)

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Default configuration for movie-generator" in content

    def test_write_config_file_exists_error(self, tmp_path):
        """Test write_config_to_file raises error when file exists."""
        output_file = tmp_path / "config.yaml"
        output_file.write_text("existing content")

        with pytest.raises(FileExistsError):
            write_config_to_file(output_file, overwrite=False)

    def test_write_config_overwrite(self, tmp_path):
        """Test write_config_to_file overwrites when overwrite=True."""
        output_file = tmp_path / "config.yaml"
        output_file.write_text("existing content")

        write_config_to_file(output_file, overwrite=True)

        content = output_file.read_text()
        assert "# Default configuration for movie-generator" in content
        assert "existing content" not in content

    def test_write_config_creates_parent_directories(self, tmp_path):
        """Test write_config_to_file creates parent directories if needed."""
        output_file = tmp_path / "nested" / "dir" / "config.yaml"

        write_config_to_file(output_file, overwrite=False)

        assert output_file.exists()
        assert output_file.parent.exists()
