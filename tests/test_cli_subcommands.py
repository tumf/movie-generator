"""Tests for CLI subcommands."""

from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from movie_generator.cli import audio, script, slides, video


class TestScriptCreate:
    """Test script create command."""

    def test_help_message(self) -> None:
        """Test script create --help shows proper message."""
        runner = CliRunner()
        result = runner.invoke(script, ["create", "--help"])
        assert result.exit_code == 0
        assert "Generate script from URL" in result.output
        assert "--output" in result.output
        assert "--force" in result.output
        assert "--quiet" in result.output
        assert "--verbose" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_mode(self) -> None:
        """Test script create with --dry-run."""
        runner = CliRunner()
        result = runner.invoke(script, ["create", "https://example.com", "--dry-run"])
        assert result.exit_code == 0
        assert "[DRY-RUN]" in result.output
        assert "Would fetch content from" in result.output

    def test_quiet_and_verbose_mutually_exclusive(self) -> None:
        """Test that --quiet and --verbose cannot be used together."""
        runner = CliRunner()
        result = runner.invoke(script, ["create", "https://example.com", "--quiet", "--verbose"])
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output

    def test_skip_existing_script(self) -> None:
        """Test that script create skips if script.yaml exists without --force."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create an existing script file
            script_path = Path("script.yaml")
            script_path.write_text("existing: content")

            result = runner.invoke(script, ["create", "https://example.com"])
            assert result.exit_code != 0
            assert "already exists" in result.output
            assert "Use --force to overwrite" in result.output

    @patch("movie_generator.cli._fetch_and_generate_script")
    def test_uses_common_function(self, mock_fetch: Mock) -> None:
        """Test that script create uses the common _fetch_and_generate_script function."""
        from movie_generator.script.generator import Narration, ScriptSection, VideoScript

        # Mock the common function to return a simple script
        mock_script = VideoScript(
            title="Test Script",
            description="Test Description",
            sections=[
                ScriptSection(
                    title="Section 1",
                    narrations=[Narration(text="Hello", reading="ハロー")],
                )
            ],
        )
        mock_fetch.return_value = mock_script

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(script, ["create", "https://example.com"])
            assert result.exit_code == 0
            # Verify the common function was called
            mock_fetch.assert_called_once()
            # Verify script was saved
            script_path = Path("script.yaml")
            assert script_path.exists()


class TestAudioGenerate:
    """Test audio generate command."""

    def test_help_message(self) -> None:
        """Test audio generate --help shows proper message."""
        runner = CliRunner()
        result = runner.invoke(audio, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate audio files from script.yaml" in result.output
        assert "--scenes" in result.output
        assert "--force" in result.output
        assert "--quiet" in result.output
        assert "--verbose" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_mode(self) -> None:
        """Test audio generate with --dry-run."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy script file
            script_path = Path("script.yaml")
            script_path.write_text(
                """
title: Test
description: Test
sections:
  - title: Section 1
    narrations:
      - text: Hello
        reading: ハロー
"""
            )
            result = runner.invoke(audio, ["generate", str(script_path), "--dry-run"])
            assert result.exit_code == 0
            assert "[DRY-RUN]" in result.output

    def test_missing_script_file(self) -> None:
        """Test audio generate with non-existent script."""
        runner = CliRunner()
        result = runner.invoke(audio, ["generate", "nonexistent.yaml"])
        assert result.exit_code != 0

    def test_quiet_and_verbose_mutually_exclusive(self) -> None:
        """Test that --quiet and --verbose cannot be used together."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            script_path = Path("script.yaml")
            script_path.write_text("title: Test\ndescription: Test\nsections: []")
            result = runner.invoke(audio, ["generate", str(script_path), "--quiet", "--verbose"])
            assert result.exit_code != 0
            assert "mutually exclusive" in result.output


class TestSlidesGenerate:
    """Test slides generate command."""

    def test_help_message(self) -> None:
        """Test slides generate --help shows proper message."""
        runner = CliRunner()
        result = runner.invoke(slides, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate slide images from script.yaml" in result.output
        assert "--api-key" in result.output
        assert "--force" in result.output
        assert "--quiet" in result.output
        assert "--verbose" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_mode(self) -> None:
        """Test slides generate with --dry-run."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            script_path = Path("script.yaml")
            script_path.write_text(
                """
title: Test
description: Test
sections:
  - title: Section 1
    narrations:
      - text: Hello
        reading: ハロー
"""
            )
            result = runner.invoke(slides, ["generate", str(script_path), "--dry-run"])
            assert result.exit_code == 0
            assert "[DRY-RUN]" in result.output

    def test_missing_api_key(self) -> None:
        """Test slides generate without API key (dry-run bypasses check)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            script_path = Path("script.yaml")
            script_path.write_text(
                """
title: Test
description: Test
sections:
  - title: Section 1
    narrations:
      - text: Hello
        reading: ハロー
"""
            )
            # Without dry-run, should fail with missing API key
            # But API key check only happens if not in dry-run mode
            # So we test that dry-run works without API key
            result = runner.invoke(slides, ["generate", str(script_path), "--dry-run"])
            assert result.exit_code == 0
            assert "[DRY-RUN]" in result.output


class TestVideoRender:
    """Test video render command."""

    def test_help_message(self) -> None:
        """Test video render --help shows proper message."""
        runner = CliRunner()
        result = runner.invoke(video, ["render", "--help"])
        assert result.exit_code == 0
        assert "Render video from script, audio, and slides" in result.output
        assert "--output" in result.output
        assert "--force" in result.output
        assert "--quiet" in result.output
        assert "--verbose" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_mode(self) -> None:
        """Test video render with --dry-run."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            script_path = Path("script.yaml")
            script_path.write_text(
                """
title: Test
description: Test
sections:
  - title: Section 1
    narrations:
      - text: Hello
        reading: ハロー
"""
            )
            result = runner.invoke(video, ["render", str(script_path), "--dry-run"])
            assert result.exit_code == 0
            assert "[DRY-RUN]" in result.output

    def test_missing_audio_directory(self) -> None:
        """Test video render without audio directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            script_path = Path("script.yaml")
            script_path.write_text("title: Test\ndescription: Test\nsections: []")
            result = runner.invoke(video, ["render", str(script_path)])
            assert result.exit_code != 0
            assert "Audio directory not found" in result.output


class TestCommonOptions:
    """Test common options across all commands."""

    def test_force_option_available_on_all_commands(self) -> None:
        """Test --force is available on all subcommands."""
        runner = CliRunner()
        commands = [
            (script, ["create", "--help"]),
            (audio, ["generate", "--help"]),
            (slides, ["generate", "--help"]),
            (video, ["render", "--help"]),
        ]
        for cmd, args in commands:
            result = runner.invoke(cmd, args)
            assert "--force" in result.output or "-f" in result.output

    def test_quiet_option_available_on_all_commands(self) -> None:
        """Test --quiet is available on all subcommands."""
        runner = CliRunner()
        commands = [
            (script, ["create", "--help"]),
            (audio, ["generate", "--help"]),
            (slides, ["generate", "--help"]),
            (video, ["render", "--help"]),
        ]
        for cmd, args in commands:
            result = runner.invoke(cmd, args)
            assert "--quiet" in result.output or "-q" in result.output

    def test_verbose_option_available_on_all_commands(self) -> None:
        """Test --verbose is available on all subcommands."""
        runner = CliRunner()
        commands = [
            (script, ["create", "--help"]),
            (audio, ["generate", "--help"]),
            (slides, ["generate", "--help"]),
            (video, ["render", "--help"]),
        ]
        for cmd, args in commands:
            result = runner.invoke(cmd, args)
            assert "--verbose" in result.output or "-v" in result.output

    def test_dry_run_option_available_on_all_commands(self) -> None:
        """Test --dry-run is available on all subcommands."""
        runner = CliRunner()
        commands = [
            (script, ["create", "--help"]),
            (audio, ["generate", "--help"]),
            (slides, ["generate", "--help"]),
            (video, ["render", "--help"]),
        ]
        for cmd, args in commands:
            result = runner.invoke(cmd, args)
            assert "--dry-run" in result.output


class TestBackwardCompatibility:
    """Test that existing generate command still works."""

    def test_generate_command_exists(self) -> None:
        """Test that generate command is still available."""
        runner = CliRunner()
        from movie_generator.cli import cli

        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "generate" in result.output

    def test_generate_command_help(self) -> None:
        """Test generate command help message."""
        runner = CliRunner()
        from movie_generator.cli import cli

        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate video from URL or existing script.yaml" in result.output
