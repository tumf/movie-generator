"""Tests for subtitle color propagation across the system.

This test suite ensures subtitle colors are correctly:
1. Defined in constants.py (Single Source of Truth)
2. Used as default in config.py
3. Propagated through remotion_renderer.py
4. Embedded in generated VideoGenerator.tsx

CRITICAL: These tests prevent regression of subtitle color issues.
"""

import json
import tempfile
from pathlib import Path

import pytest

from movie_generator.config import PersonaConfig, VoicevoxSynthesizerConfig
from movie_generator.constants import SubtitleConstants
from movie_generator.script.phrases import Phrase
from movie_generator.video.remotion_renderer import _get_persona_fields, update_composition_json
from movie_generator.video.templates import get_video_generator_tsx


class TestSubtitleColorConstants:
    """Test that subtitle color constants are properly defined."""

    def test_default_color_is_white(self) -> None:
        """Default subtitle color should be white (#FFFFFF)."""
        assert SubtitleConstants.DEFAULT_COLOR == "#FFFFFF"

    def test_default_color_is_valid_hex(self) -> None:
        """Default color should be a valid hex color."""
        color = SubtitleConstants.DEFAULT_COLOR
        assert color.startswith("#")
        assert len(color) == 7
        # Should be valid hex
        int(color[1:], 16)


class TestConfigSubtitleColor:
    """Test that config.py uses the constant for default subtitle color."""

    def test_persona_default_subtitle_color(self) -> None:
        """PersonaConfig should use SubtitleConstants.DEFAULT_COLOR as default."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
            # No subtitle_color specified - should use default
        )
        assert persona.subtitle_color == SubtitleConstants.DEFAULT_COLOR

    def test_persona_custom_subtitle_color(self) -> None:
        """PersonaConfig should accept custom subtitle colors."""
        custom_color = "#FF69B4"
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
            subtitle_color=custom_color,
        )
        assert persona.subtitle_color == custom_color


class TestRemotionRendererSubtitleColor:
    """Test that remotion_renderer.py correctly propagates subtitle colors."""

    def test_get_persona_fields_with_color(self) -> None:
        """_get_persona_fields should return persona's subtitle_color."""
        phrase = Phrase(text="test", persona_id="zundamon", persona_name="ずんだもん")
        persona_map = {
            "zundamon": {
                "id": "zundamon",
                "name": "ずんだもん",
                "subtitle_color": "#8FCF4F",
            }
        }
        persona_position_map = {"zundamon": "left"}
        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields["subtitleColor"] == "#8FCF4F"

    def test_get_persona_fields_without_color_uses_default(self) -> None:
        """_get_persona_fields should use default when persona has no color."""
        phrase = Phrase(text="test", persona_id="test", persona_name="Test")
        persona_map = {
            "test": {
                "id": "test",
                "name": "Test",
                # No subtitle_color
            }
        }
        persona_position_map = {"test": "center"}
        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields["subtitleColor"] == SubtitleConstants.DEFAULT_COLOR

    def test_get_persona_fields_no_persona_returns_empty(self) -> None:
        """_get_persona_fields should return empty dict when no persona_id."""
        phrase = Phrase(text="test")  # No persona_id
        persona_map = {}
        persona_position_map = {}
        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields == {}


class TestCompositionJsonSubtitleColor:
    """Test that composition.json contains correct subtitle colors."""

    def test_composition_json_includes_subtitle_color(self) -> None:
        """update_composition_json should include subtitleColor in phrases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            remotion_root = Path(tmpdir)
            (remotion_root / "public").mkdir()
            (remotion_root / "public" / "audio").mkdir(parents=True)

            phrases = [
                Phrase(text="Hello", persona_id="alice", persona_name="Alice", duration=1.0),
                Phrase(text="Hi", persona_id="bob", persona_name="Bob", duration=1.0),
            ]
            # Set original_index
            for i, p in enumerate(phrases):
                p.original_index = i

            audio_paths = [
                remotion_root / "public" / "audio" / "phrase_0000.wav",
                remotion_root / "public" / "audio" / "phrase_0001.wav",
            ]
            # Create dummy audio files
            for path in audio_paths:
                path.touch()

            personas = [
                {"id": "alice", "name": "Alice", "subtitle_color": "#FF0000"},
                {"id": "bob", "name": "Bob", "subtitle_color": "#00FF00"},
            ]

            update_composition_json(
                remotion_root=remotion_root,
                phrases=phrases,
                audio_paths=audio_paths,
                slide_paths=None,
                project_name="test",
                personas=personas,
            )

            composition_path = remotion_root / "composition.json"
            with composition_path.open() as f:
                data = json.load(f)

            assert data["phrases"][0]["subtitleColor"] == "#FF0000"
            assert data["phrases"][1]["subtitleColor"] == "#00FF00"


class TestVideoGeneratorTsxSubtitleColor:
    """Test that VideoGenerator.tsx uses the correct default color."""

    def test_template_contains_default_color_constant(self) -> None:
        """Generated template should use SubtitleConstants.DEFAULT_COLOR."""
        template = get_video_generator_tsx()
        # The template should contain the default color from constants
        assert SubtitleConstants.DEFAULT_COLOR in template

    def test_template_does_not_contain_hardcoded_green(self) -> None:
        """Generated template should NOT contain hardcoded green (#8FCF4F)."""
        template = get_video_generator_tsx()
        # This was the previous bug - green was hardcoded as default
        assert "#8FCF4F" not in template

    def test_template_uses_subtitle_color_prop(self) -> None:
        """Template should pass subtitleColor to AudioSubtitleLayer."""
        template = get_video_generator_tsx()
        assert "subtitleColor={scene.subtitleColor}" in template

    def test_template_stroke_color_fallback(self) -> None:
        """Template should have fallback for strokeColor."""
        template = get_video_generator_tsx()
        # Should have fallback pattern: subtitleColor || 'DEFAULT_COLOR'
        expected_fallback = f"subtitleColor || '{SubtitleConstants.DEFAULT_COLOR}'"
        assert expected_fallback in template


class TestSubtitleColorIntegration:
    """Integration tests for end-to-end subtitle color flow."""

    def test_zundamon_metan_colors_distinct(self) -> None:
        """Zundamon (green) and Metan (pink) should have distinct colors."""
        # Define expected colors based on multi-speaker-example.yaml
        zundamon_color = "#8FCF4F"  # Green
        metan_color = "#FF69B4"  # Pink

        # Create personas
        zundamon = PersonaConfig(
            id="zundamon",
            name="ずんだもん",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
            subtitle_color=zundamon_color,
        )
        metan = PersonaConfig(
            id="metan",
            name="四国めたん",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
            subtitle_color=metan_color,
        )

        assert zundamon.subtitle_color != metan.subtitle_color
        assert zundamon.subtitle_color == zundamon_color
        assert metan.subtitle_color == metan_color

    def test_persona_colors_propagate_to_composition(self) -> None:
        """Persona colors from config should propagate to composition.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            remotion_root = Path(tmpdir)
            (remotion_root / "public" / "audio").mkdir(parents=True)

            # Simulate zundamon and metan phrases
            phrases = [
                Phrase(
                    text="こんにちは",
                    persona_id="zundamon",
                    persona_name="ずんだもん",
                    duration=1.0,
                ),
                Phrase(
                    text="よろしく",
                    persona_id="metan",
                    persona_name="四国めたん",
                    duration=1.0,
                ),
            ]
            for i, p in enumerate(phrases):
                p.original_index = i

            audio_paths = [
                remotion_root / "public" / "audio" / "phrase_0000.wav",
                remotion_root / "public" / "audio" / "phrase_0001.wav",
            ]
            for path in audio_paths:
                path.touch()

            personas = [
                {"id": "zundamon", "name": "ずんだもん", "subtitle_color": "#8FCF4F"},
                {"id": "metan", "name": "四国めたん", "subtitle_color": "#FF69B4"},
            ]

            update_composition_json(
                remotion_root=remotion_root,
                phrases=phrases,
                audio_paths=audio_paths,
                slide_paths=None,
                project_name="test",
                personas=personas,
            )

            composition_path = remotion_root / "composition.json"
            with composition_path.open() as f:
                data = json.load(f)

            # Verify each phrase has the correct color
            zundamon_phrase = data["phrases"][0]
            metan_phrase = data["phrases"][1]

            assert zundamon_phrase["subtitleColor"] == "#8FCF4F", "Zundamon should be green"
            assert metan_phrase["subtitleColor"] == "#FF69B4", "Metan should be pink"
            assert zundamon_phrase["subtitleColor"] != metan_phrase["subtitleColor"], (
                "Colors should be different"
            )
