"""End-to-end tests for video generation with Remotion."""

import tempfile
from pathlib import Path

import pytest

from src.movie_generator.script.phrases import Phrase, calculate_phrase_timings
from src.movie_generator.video.remotion_renderer import (
    create_remotion_input,
    render_video_with_remotion,
)


def test_create_remotion_input():
    """Test creating Remotion input data from phrases."""
    phrases = [
        Phrase(text="First phrase", duration=2.5, start_time=0.0),
        Phrase(text="Second phrase", duration=3.0, start_time=2.5),
    ]

    audio_paths = [Path("audio/001.wav"), Path("audio/002.wav")]
    slide_paths = [Path("slides/slide1.png"), Path("slides/slide2.png")]

    result = create_remotion_input(phrases, audio_paths, slide_paths)

    assert len(result) == 2
    assert result[0]["text"] == "First phrase"
    assert result[0]["audioFile"] == "audio/001.wav"
    assert result[0]["slideFile"] == "slides/slide1.png"
    assert result[0]["duration"] == 2.5

    assert result[1]["text"] == "Second phrase"
    assert result[1]["audioFile"] == "audio/002.wav"
    assert result[1]["slideFile"] == "slides/slide2.png"
    assert result[1]["duration"] == 3.0


def test_create_remotion_input_without_slides():
    """Test creating Remotion input without slides."""
    phrases = [
        Phrase(text="First phrase", duration=2.5, start_time=0.0),
    ]

    audio_paths = [Path("audio/001.wav")]

    result = create_remotion_input(phrases, audio_paths, None)

    assert len(result) == 1
    assert result[0]["text"] == "First phrase"
    assert result[0]["audioFile"] == "audio/001.wav"
    assert result[0]["slideFile"] is None


@pytest.mark.skip(reason="Requires Remotion installation and valid media files")
def test_render_video_with_remotion_e2e():
    """End-to-end test for Remotion video rendering.

    This test is skipped by default as it requires:
    - Remotion to be installed (npm install in remotion/)
    - Valid audio and slide files
    - More time to execute

    Run with: pytest -v tests/test_video_e2e.py::test_render_video_with_remotion_e2e -s
    """
    # Setup test data
    phrases = [
        Phrase(text="Test phrase one", duration=2.0, start_time=0.0),
        Phrase(text="Test phrase two", duration=2.0, start_time=2.0),
    ]

    # These would need to be actual files for a real test
    audio_paths = [
        Path("public/audio/test1.wav"),
        Path("public/audio/test2.wav"),
    ]
    slide_paths = [
        Path("public/slides/test1.png"),
        Path("public/slides/test2.png"),
    ]

    remotion_root = Path(__file__).parent.parent / "remotion"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.mp4"

        # This will fail if Remotion is not set up, but shows the intended usage
        try:
            render_video_with_remotion(
                phrases=phrases,
                audio_paths=audio_paths,
                slide_paths=slide_paths,
                output_path=output_path,
                remotion_root=remotion_root,
            )

            # Verify output was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0

        except FileNotFoundError as e:
            pytest.skip(f"Remotion not available: {e}")
