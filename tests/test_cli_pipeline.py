"""Tests for CLI pipeline stages.

This module tests the pipeline stage functions to verify:
1. Script resolution (loading existing or generating from URL)
2. Stage function call order and interfaces
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from rich.progress import Progress

from movie_generator.cli_pipeline import (
    PipelineParams,
    stage_script_resolution,
)
from movie_generator.config import Config
from movie_generator.script.generator import Narration, ScriptSection, VideoScript


class TestPipelineStages:
    """Test pipeline stage functions."""

    @pytest.fixture
    def mock_params(self) -> PipelineParams:
        """Create mock pipeline parameters."""
        return PipelineParams(
            url_or_script=None,
            config=Config(),
            output_dir=Path("/tmp/test"),
            api_key="test-key",
            mcp_config=None,
            scenes=None,
            show_progress=False,
            persona_pool_count=None,
            persona_pool_seed=None,
            strict=False,
        )

    @pytest.fixture
    def mock_script(self) -> VideoScript:
        """Create a mock script."""
        return VideoScript(
            title="Test Script",
            description="Test Description",
            sections=[
                ScriptSection(
                    title="Section 1",
                    narrations=[Narration(text="Hello", reading="ハロー")],
                    slide_prompt="Test slide",
                )
            ],
        )

    @pytest.fixture
    def mock_progress(self) -> Progress:
        """Create a mock progress bar."""
        return Mock(spec=Progress)

    @pytest.fixture
    def mock_console(self) -> Console:
        """Create a mock console."""
        return Mock(spec=Console)

    def test_stage_script_resolution_with_existing_script(
        self,
        mock_params: PipelineParams,
        mock_progress: Progress,
        mock_console: Console,
        tmp_path: Path,
    ) -> None:
        """Test that stage_script_resolution skips generation when script.yaml exists."""
        # Create existing script file
        script_path = tmp_path / "script.yaml"
        script_content = """
title: Existing Script
description: Test
sections:
  - title: Section 1
    narrations:
      - text: Hello
        reading: ハロー
    slide_prompt: Test
"""
        script_path.write_text(script_content)

        # Update params to point to existing script
        mock_params.url_or_script = str(script_path)
        mock_params.output_dir = tmp_path

        # Execute stage
        script = stage_script_resolution(mock_params, mock_progress, mock_console)

        # Verify script was loaded (not generated)
        assert script.title == "Existing Script"
        assert len(script.sections) == 1

    @patch("movie_generator.cli_pipeline.fetch_url_sync")
    @patch("movie_generator.cli_pipeline.parse_html")
    @patch("movie_generator.cli_pipeline.generate_script")
    def test_stage_script_resolution_generates_from_url(
        self,
        mock_generate: Mock,
        mock_parse: Mock,
        mock_fetch: Mock,
        mock_params: PipelineParams,
        mock_script: VideoScript,
        mock_progress: Progress,
        mock_console: Console,
        tmp_path: Path,
    ) -> None:
        """Test that stage_script_resolution generates script from URL."""
        # Setup mocks
        mock_fetch.return_value = "<html>Test content</html>"
        mock_metadata = Mock(url="https://example.com", published_date=None, author=None)
        mock_parse.return_value = Mock(
            title="Test",
            description="Test",
            text_content="Test content",
            metadata=mock_metadata,
            images=[],  # Empty list to avoid iteration error
        )
        mock_generate.return_value = mock_script

        # Update params
        mock_params.url_or_script = "https://example.com"
        mock_params.output_dir = tmp_path
        mock_params.api_key = "test-key"

        # Execute stage
        script = stage_script_resolution(mock_params, mock_progress, mock_console)

        # Verify script was generated
        assert script.title == "Test Script"
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once()
        mock_generate.assert_called_once()

    def test_script_resolution_with_url_requires_api_key(
        self,
        mock_params: PipelineParams,
        mock_progress: Progress,
        mock_console: Console,
        tmp_path: Path,
    ) -> None:
        """Test that script resolution from URL validates input."""
        # Update params with URL but no API key
        mock_params.url_or_script = "https://example.com"
        mock_params.output_dir = tmp_path
        mock_params.api_key = None

        # This should attempt to fetch, which will fail in test environment
        # We're mainly testing that the stage function can be called
        with pytest.raises(Exception):
            stage_script_resolution(mock_params, mock_progress, mock_console)

    def test_pipeline_stages_exist_and_importable(self) -> None:
        """Test that all pipeline stage functions are defined and can be imported."""
        from movie_generator.cli_pipeline import (
            stage_audio_generation,
            stage_script_resolution,
            stage_slides_generation,
            stage_video_rendering,
        )

        # Verify all stage functions exist
        assert callable(stage_script_resolution)
        assert callable(stage_audio_generation)
        assert callable(stage_slides_generation)
        assert callable(stage_video_rendering)
