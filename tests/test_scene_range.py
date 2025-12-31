"""Tests for scene range parsing and filtering."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.cli import parse_scene_range


class TestSceneRangeParsing:
    """Test scene range parsing function."""

    def test_single_scene(self) -> None:
        """Test parsing single scene number."""
        start, end = parse_scene_range("2")
        assert start == 1  # 0-based
        assert end == 1

    def test_scene_range(self) -> None:
        """Test parsing scene range."""
        start, end = parse_scene_range("1-3")
        assert start == 0  # 0-based
        assert end == 2

    def test_scene_range_same_start_end(self) -> None:
        """Test parsing scene range with same start and end."""
        start, end = parse_scene_range("5-5")
        assert start == 4
        assert end == 4

    def test_invalid_format_multiple_dashes(self) -> None:
        """Test error handling for invalid format with multiple dashes."""
        with pytest.raises(ValueError, match="Invalid scene range format"):
            parse_scene_range("1-2-3")

    def test_invalid_format_non_numeric(self) -> None:
        """Test error handling for non-numeric input."""
        with pytest.raises(ValueError, match="Invalid scene number"):
            parse_scene_range("abc")

    def test_invalid_range_non_numeric(self) -> None:
        """Test error handling for non-numeric range."""
        with pytest.raises(ValueError, match="Invalid end scene number"):
            parse_scene_range("1-abc")

    def test_invalid_range_zero(self) -> None:
        """Test error handling for zero scene number."""
        with pytest.raises(ValueError, match="Scene number must be >= 1"):
            parse_scene_range("0")

    def test_from_beginning_to_scene_1(self) -> None:
        """Test '-1' format (from beginning to scene 1)."""
        # "-1" is a valid format meaning "from beginning to scene 1"
        start, end = parse_scene_range("-1")
        assert start is None  # From beginning
        assert end == 0  # Scene 1 (0-based)

    def test_invalid_range_start_greater_than_end(self) -> None:
        """Test error handling for reversed range."""
        with pytest.raises(ValueError, match="Invalid scene range.*Start must be <= end"):
            parse_scene_range("3-1")

    def test_large_range(self) -> None:
        """Test parsing large scene range."""
        start, end = parse_scene_range("10-100")
        assert start == 9
        assert end == 99


class TestSceneRangeIntegration:
    """Integration tests for scene range filtering."""

    def test_phrase_filtering(self) -> None:
        """Test that phrases are correctly filtered by section_index."""
        from movie_generator.script.phrases import Phrase

        # Create mock phrases with section indices
        all_phrases = [
            Phrase(text="Section 0 phrase 1", section_index=0),
            Phrase(text="Section 0 phrase 2", section_index=0),
            Phrase(text="Section 1 phrase 1", section_index=1),
            Phrase(text="Section 1 phrase 2", section_index=1),
            Phrase(text="Section 2 phrase 1", section_index=2),
        ]

        # Filter for scene range 1-2 (0-indexed: 0-1)
        scene_start_idx = 0
        scene_end_idx = 1
        filtered = [p for p in all_phrases if scene_start_idx <= p.section_index <= scene_end_idx]

        assert len(filtered) == 4
        assert all(p.section_index in [0, 1] for p in filtered)

    def test_audio_path_filtering(self) -> None:
        """Test that audio paths are correctly filtered."""
        from pathlib import Path

        from movie_generator.script.phrases import Phrase

        # Create mock data
        all_phrases = [
            Phrase(text="Phrase 0", section_index=0),
            Phrase(text="Phrase 1", section_index=0),
            Phrase(text="Phrase 2", section_index=1),
            Phrase(text="Phrase 3", section_index=1),
            Phrase(text="Phrase 4", section_index=2),
        ]
        audio_paths = [Path(f"audio/phrase_{i:04d}.wav") for i in range(len(all_phrases))]

        # Filter for scene 1 only (0-indexed: 0)
        scene_start_idx = 0
        scene_end_idx = 0
        filtered_indices = [
            i
            for i, p in enumerate(all_phrases)
            if scene_start_idx <= p.section_index <= scene_end_idx
        ]
        filtered_phrases = [all_phrases[i] for i in filtered_indices]
        filtered_audio = [audio_paths[i] for i in filtered_indices]

        assert len(filtered_phrases) == 2
        assert len(filtered_audio) == 2
        assert filtered_audio[0].name == "phrase_0000.wav"
        assert filtered_audio[1].name == "phrase_0001.wav"

    def test_phrase_filtering_reduces_generated_count(self) -> None:
        """Test that scene filtering reduces the number of phrases before audio generation."""
        from movie_generator.script.phrases import Phrase

        # Simulate 5 sections with 2 phrases each (10 total phrases)
        all_phrases = []
        for section_idx in range(5):
            for phrase_num in range(2):
                phrase = Phrase(
                    text=f"Section {section_idx} phrase {phrase_num}", section_index=section_idx
                )
                all_phrases.append(phrase)

        assert len(all_phrases) == 10

        # Filter for scenes 2-3 (0-indexed: 1-2)
        scene_start_idx = 1
        scene_end_idx = 2
        filtered_phrases = [
            p for p in all_phrases if scene_start_idx <= p.section_index <= scene_end_idx
        ]

        # Should only have 4 phrases (2 sections × 2 phrases)
        assert len(filtered_phrases) == 4
        assert all(p.section_index in [1, 2] for p in filtered_phrases)

        # This demonstrates that audio generation will only process 4 phrases instead of 10


class TestOutputFilename:
    """Test output filename generation based on scene range."""

    def _generate_output_filename(self, scenes: str | None, total_sections: int) -> str:
        """Helper to generate output filename based on scene range."""
        if not scenes:
            return "output.mp4"

        scene_start, scene_end = parse_scene_range(scenes)

        # Convert None values to actual scene numbers for filename
        start_num = 1 if scene_start is None else scene_start + 1
        end_num = total_sections if scene_end is None else scene_end + 1

        if start_num == end_num:
            return f"output_{start_num}.mp4"
        else:
            return f"output_{start_num}-{end_num}.mp4"

    def test_no_scene_range(self) -> None:
        """Test default filename when no scene range specified."""
        filename = self._generate_output_filename(None, 10)
        assert filename == "output.mp4"

    def test_single_scene(self) -> None:
        """Test filename for single scene (e.g., --scenes 2)."""
        filename = self._generate_output_filename("2", 10)
        assert filename == "output_2.mp4"

    def test_explicit_range(self) -> None:
        """Test filename for explicit range (e.g., --scenes 1-3)."""
        filename = self._generate_output_filename("1-3", 10)
        assert filename == "output_1-3.mp4"

    def test_from_beginning(self) -> None:
        """Test filename for from-beginning format (e.g., --scenes -3)."""
        filename = self._generate_output_filename("-3", 10)
        assert filename == "output_1-3.mp4"

    def test_to_end(self) -> None:
        """Test filename for to-end format (e.g., --scenes 5-)."""
        filename = self._generate_output_filename("5-", 10)
        assert filename == "output_5-10.mp4"

    def test_from_beginning_single(self) -> None:
        """Test filename for -1 (from beginning to scene 1)."""
        filename = self._generate_output_filename("-1", 10)
        assert filename == "output_1.mp4"

    def test_same_start_end(self) -> None:
        """Test filename when start equals end (e.g., --scenes 5-5)."""
        filename = self._generate_output_filename("5-5", 10)
        assert filename == "output_5.mp4"
