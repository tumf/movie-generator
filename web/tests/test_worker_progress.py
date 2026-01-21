"""Tests for worker progress monitoring."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from web.worker.main import MovieGeneratorWrapper


class TestProgressMonitoring:
    """Test progress monitoring functionality."""

    @pytest.fixture
    def temp_job_dir(self, tmp_path: Path) -> Path:
        """Create temporary job directory."""
        return tmp_path / "test_job"

    @pytest.fixture
    def wrapper(self, temp_job_dir: Path) -> MovieGeneratorWrapper:
        """Create MovieGeneratorWrapper instance."""
        return MovieGeneratorWrapper(job_data_dir=temp_job_dir.parent)

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

        # Mock subprocess.run to avoid actual execution
        with patch("subprocess.run") as mock_run:
            # Script generation success
            mock_run.return_value = Mock(returncode=0, stderr="")

            # Create mock script.yaml
            script_path = temp_job_dir / "script.yaml"
            temp_job_dir.mkdir(parents=True, exist_ok=True)
            script_content = """
title: Test
sections:
  - title: S1
    narrations:
      - text: "P1"
      - text: "P2"
  - title: S2
    narrations:
      - text: "P3"
"""
            script_path.write_text(script_content, encoding="utf-8")

            # Create audio and slide files to simulate generation
            audio_dir = temp_job_dir / "audio" / "ja"
            audio_dir.mkdir(parents=True, exist_ok=True)
            slides_dir = temp_job_dir / "slides" / "ja"
            slides_dir.mkdir(parents=True, exist_ok=True)

            # Create output file
            output_file = temp_job_dir / "output.mp4"
            output_file.touch()

            # Start generation in background
            async def simulate_file_creation():
                await asyncio.sleep(3)
                (audio_dir / "phrase_0001.wav").touch()
                await asyncio.sleep(2)
                (audio_dir / "phrase_0002.wav").touch()
                await asyncio.sleep(2)
                (audio_dir / "phrase_0003.wav").touch()
                await asyncio.sleep(2)
                (slides_dir / "slide_0001.png").touch()
                await asyncio.sleep(2)
                (slides_dir / "slide_0002.png").touch()

            simulation_task = asyncio.create_task(simulate_file_creation())

            # Run generate_video
            result = await wrapper.generate_video("test_job", "http://example.com", mock_callback)

            await simulation_task

            # Verify result
            assert result == output_file

            # Verify progress updates
            assert len(progress_updates) > 0

            # Check script generation progress
            script_updates = [u for u in progress_updates if u["step"] == "script"]
            assert len(script_updates) >= 2
            assert "スクリプトを生成中" in script_updates[0]["message"]
            assert "スクリプト生成完了" in script_updates[-1]["message"]

            # Check audio generation progress
            audio_updates = [u for u in progress_updates if u["step"] == "audio"]
            assert len(audio_updates) > 0
            # Should have updates showing progress like "音声生成中 (1/3)"
            assert any("音声生成中" in u["message"] for u in audio_updates)

            # Check slide generation progress
            slide_updates = [u for u in progress_updates if u["step"] == "slides"]
            assert len(slide_updates) > 0
            assert any("スライド生成中" in u["message"] for u in slide_updates)

            # Check final video progress
            video_updates = [u for u in progress_updates if u["step"] == "video"]
            assert len(video_updates) >= 2
            assert progress_updates[-1]["progress"] == 100
            assert "動画生成完了" in progress_updates[-1]["message"]
