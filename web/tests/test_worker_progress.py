"""Tests for worker progress monitoring."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from worker.generator import MovieGeneratorWrapper
from worker.settings import WorkerSettings


class TestProgressMonitoring:
    """Test progress monitoring functionality."""

    @pytest.fixture
    def temp_job_dir(self, tmp_path: Path) -> Path:
        """Create temporary job directory."""
        return tmp_path / "test_job"

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> WorkerSettings:
        """Create mock WorkerSettings instance."""
        config = WorkerSettings()
        config.job_data_dir = tmp_path
        config.config_path = None
        config.mcp_config_path = None
        return config

    @pytest.fixture
    def wrapper(self, tmp_path: Path, mock_config: WorkerSettings) -> MovieGeneratorWrapper:
        """Create MovieGeneratorWrapper instance."""
        return MovieGeneratorWrapper(job_data_dir=tmp_path, config=mock_config)

    def test_count_script_items(self, wrapper: MovieGeneratorWrapper, tmp_path: Path) -> None:
        """Test counting phrases and slides from script.yaml."""
        script_path = tmp_path / "script.yaml"
        script_content = """
title: Test Script
description: Test description
sections:
  - title: Section 1
    narrations:
      - text: "First phrase"
        reading: "ファーストフレーズ"
      - text: "Second phrase"
        reading: "セカンドフレーズ"
    slide_prompt: "Slide 1"
  - title: Section 2
    narrations:
      - text: "Third phrase"
        reading: "サードフレーズ"
    slide_prompt: "Slide 2"
"""
        script_path.write_text(script_content, encoding="utf-8")

        phrase_count, slide_count = wrapper._count_script_items(script_path)

        assert phrase_count == 3  # 2 in section 1 + 1 in section 2
        assert slide_count == 2  # 2 sections

    def test_count_script_items_missing_file(
        self, wrapper: MovieGeneratorWrapper, tmp_path: Path
    ) -> None:
        """Test counting with missing script file."""
        script_path = tmp_path / "nonexistent.yaml"

        phrase_count, slide_count = wrapper._count_script_items(script_path)

        assert phrase_count == 0
        assert slide_count == 0

    @pytest.mark.asyncio
    async def test_monitor_file_progress(
        self, wrapper: MovieGeneratorWrapper, tmp_path: Path
    ) -> None:
        """Test file progress monitoring."""
        directory = tmp_path / "audio"
        directory.mkdir(parents=True, exist_ok=True)

        progress_updates = []

        async def mock_callback(progress: int, message: str, step: str) -> None:
            progress_updates.append({"progress": progress, "message": message, "step": step})

        # Start monitoring in background
        monitor_task = asyncio.create_task(
            wrapper._monitor_file_progress(
                directory=directory,
                pattern="phrase_*.wav",
                total=3,
                progress_callback=mock_callback,
                progress_start=20,
                progress_end=50,
                step_name="audio",
                item_name="音声",
            )
        )

        # Simulate file creation
        await asyncio.sleep(0.5)
        (directory / "phrase_0001.wav").touch()
        await asyncio.sleep(2.5)  # Wait for poll

        (directory / "phrase_0002.wav").touch()
        await asyncio.sleep(2.5)

        (directory / "phrase_0003.wav").touch()
        await asyncio.sleep(2.5)

        # Wait for monitor to complete
        await monitor_task

        # Check progress updates
        assert len(progress_updates) >= 3

        # First update: 1/3 files
        assert "音声生成中 (1/3)" in progress_updates[0]["message"]
        assert progress_updates[0]["progress"] > 20
        assert progress_updates[0]["progress"] < 50

        # Last update: 3/3 files (complete)
        assert "音声生成完了 (3/3)" in progress_updates[-1]["message"]
        assert progress_updates[-1]["progress"] == 50

    @pytest.mark.asyncio
    async def test_monitor_file_progress_zero_total(
        self, wrapper: MovieGeneratorWrapper, tmp_path: Path
    ) -> None:
        """Test monitoring with zero total files."""
        directory = tmp_path / "audio"
        directory.mkdir(parents=True, exist_ok=True)

        mock_callback = AsyncMock()

        # Should return immediately without monitoring
        await wrapper._monitor_file_progress(
            directory=directory,
            pattern="phrase_*.wav",
            total=0,
            progress_callback=mock_callback,
            progress_start=20,
            progress_end=50,
            step_name="audio",
            item_name="音声",
        )

        # No callbacks should be made
        mock_callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_video_progress_flow(
        self, wrapper: MovieGeneratorWrapper, temp_job_dir: Path
    ) -> None:
        """Test that generate_video updates progress correctly."""
        progress_updates = []

        async def mock_callback(progress: int, message: str, step: str) -> None:
            progress_updates.append(
                {
                    "progress": progress,
                    "message": message,
                    "step": step,
                    "timestamp": len(progress_updates),
                }
            )

        # Prepare script path (but don't create it yet - let the mock do it)
        script_path = temp_job_dir / "script.yaml"
        temp_job_dir.mkdir(parents=True, exist_ok=True)
        script_content = """
title: Test
sections:
  - title: S1
    narrations:
      - text: "P1"
        reading: "ピーワン"
      - text: "P2"
        reading: "ピーツー"
    slide_prompt: "Slide 1"
  - title: S2
    narrations:
      - text: "P3"
        reading: "ピースリー"
    slide_prompt: "Slide 2"
"""

        # Create output file path
        output_file = temp_job_dir / "output.mp4"

        # Mock the movie-generator functions
        async def mock_generate_script(url, output_dir, config_path, api_key, progress_callback):
            """Mock script generation."""
            # Write the script file as part of the mock
            script_path.write_text(script_content, encoding="utf-8")

            if progress_callback:
                progress_callback(1, 3, "スクリプト生成中 (1/3)")
                progress_callback(2, 3, "スクリプト生成中 (2/3)")
                progress_callback(3, 3, "スクリプト生成完了")
            return script_path

        def mock_generate_audio(
            script_path, output_dir, config_path, config, scenes, progress_callback
        ):
            """Mock audio generation."""
            audio_dir = output_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            # Create mock audio files
            (audio_dir / "phrase_0001.wav").touch()
            (audio_dir / "phrase_0002.wav").touch()
            (audio_dir / "phrase_0003.wav").touch()

            if progress_callback:
                progress_callback(1, 3, "音声生成中 (1/3)")
                progress_callback(2, 3, "音声生成中 (2/3)")
                progress_callback(3, 3, "音声生成完了")

        async def mock_generate_slides(
            script_path, output_dir, api_key, model, progress_callback, resolution
        ):
            """Mock slide generation."""
            slides_dir = output_dir / "slides"
            slides_dir.mkdir(parents=True, exist_ok=True)

            # Create mock slide files
            (slides_dir / "slide_0001.png").touch()
            (slides_dir / "slide_0002.png").touch()

            if progress_callback:
                progress_callback(1, 2, "スライド生成中 (1/2)")
                progress_callback(2, 2, "スライド生成完了")

        def mock_render_video(
            script_path,
            output_path,
            output_dir,
            config_path,
            config,
            scenes,
            show_progress,
            progress_callback,
        ):
            """Mock video rendering."""
            output_path.touch()

            if progress_callback:
                progress_callback(1, 10, "レンダリング中 (10%)")
                progress_callback(5, 10, "レンダリング中 (50%)")
                progress_callback(10, 10, "レンダリング完了")

        # Patch the movie-generator functions
        with (
            patch("movie_generator.script.generate_script_from_url", mock_generate_script),
            patch("movie_generator.audio.generate_audio_for_script", mock_generate_audio),
            patch("movie_generator.slides.generate_slides_for_script", mock_generate_slides),
            patch("movie_generator.video.render_video_for_script", mock_render_video),
            patch("os.getenv", return_value="mock_api_key"),
        ):
            # Run generate_video
            result = await wrapper.generate_video("test_job", "http://example.com", mock_callback)

            # Verify result
            assert result == output_file

            # Verify progress updates
            assert len(progress_updates) > 0

            # Check script generation progress (0-20%)
            script_updates = [u for u in progress_updates if u["step"] == "script"]
            assert len(script_updates) >= 2
            assert any("スクリプト" in u["message"] for u in script_updates)
            # Verify progress is in expected range
            for update in script_updates:
                assert 0 <= update["progress"] <= 20, (
                    f"Script progress {update['progress']} out of range [0, 20]"
                )

            # Check audio generation progress (20-55%)
            audio_updates = [u for u in progress_updates if u["step"] == "audio"]
            assert len(audio_updates) > 0
            # Verify progress is in expected range
            for update in audio_updates:
                assert 20 <= update["progress"] <= 55, (
                    f"Audio progress {update['progress']} out of range [20, 55]"
                )

            # Check slide generation progress (55-80%)
            slide_updates = [u for u in progress_updates if u["step"] == "slides"]
            assert len(slide_updates) > 0
            # Verify progress is in expected range
            for update in slide_updates:
                assert 55 <= update["progress"] <= 80, (
                    f"Slide progress {update['progress']} out of range [55, 80]"
                )

            # Check final video progress (80-100%)
            video_updates = [u for u in progress_updates if u["step"] == "video"]
            assert len(video_updates) >= 1
            # Verify progress is in expected range
            for update in video_updates:
                assert 80 <= update["progress"] <= 100, (
                    f"Video progress {update['progress']} out of range [80, 100]"
                )

            # Final progress should be 100
            assert progress_updates[-1]["progress"] == 100
            assert "動画生成完了" in progress_updates[-1]["message"]
