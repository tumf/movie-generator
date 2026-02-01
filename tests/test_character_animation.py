"""Tests for character animation feature (Phase 1-3: static, lip sync, blinking, animations)."""

from pathlib import Path

from movie_generator.config import PersonaConfig, VoicevoxSynthesizerConfig
from movie_generator.script.phrases import Phrase
from movie_generator.video.renderer import CompositionPhrase


class TestPersonaConfigCharacterFields:
    """Test PersonaConfig character image fields."""

    def test_character_image_defaults(self) -> None:
        """Test character image fields have correct defaults."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
        )
        assert persona.character_image is None
        # character_position defaults to None for auto-assignment
        # (first persona -> left, second -> right, third+ -> center)
        assert persona.character_position is None
        assert persona.mouth_open_image is None
        assert persona.eye_close_image is None
        assert persona.animation_style == "sway"

    def test_character_image_from_dict(self) -> None:
        """Test character image fields from dictionary."""
        data = {
            "id": "zundamon",
            "name": "ずんだもん",
            "synthesizer": {"speaker_id": 3},
            "character_image": "assets/characters/zundamon/base.png",
            "character_position": "right",
            "mouth_open_image": "assets/characters/zundamon/mouth_open.png",
            "eye_close_image": "assets/characters/zundamon/eye_close.png",
            "animation_style": "bounce",
        }
        persona = PersonaConfig(**data)
        assert persona.character_image == "assets/characters/zundamon/base.png"
        assert persona.character_position == "right"
        assert persona.mouth_open_image == "assets/characters/zundamon/mouth_open.png"
        assert persona.eye_close_image == "assets/characters/zundamon/eye_close.png"
        assert persona.animation_style == "bounce"

    def test_avatar_image_alias(self) -> None:
        """Test avatar_image works as alias for character_image."""
        data = {
            "id": "test",
            "name": "Test",
            "synthesizer": {"speaker_id": 3},
            "avatar_image": "assets/test.png",
        }
        persona = PersonaConfig(**data)
        assert persona.character_image == "assets/test.png"


class TestCompositionPhraseCharacterFields:
    """Test CompositionPhrase character image fields."""

    def test_character_fields_serialization(self) -> None:
        """Test character fields are serialized with camelCase aliases."""
        phrase = CompositionPhrase(
            text="Test",
            duration=1.0,
            start_time=0.0,
            audioFile="audio/test.wav",
            character_image="characters/test/base.png",
            character_position="center",
            mouth_open_image="characters/test/mouth_open.png",
            eye_close_image="characters/test/eye_close.png",
            animation_style="static",
        )
        data = phrase.model_dump(exclude_none=True, by_alias=True)
        assert data["characterImage"] == "characters/test/base.png"
        assert data["characterPosition"] == "center"
        assert data["mouthOpenImage"] == "characters/test/mouth_open.png"
        assert data["eyeCloseImage"] == "characters/test/eye_close.png"
        assert data["animationStyle"] == "static"

    def test_character_fields_optional(self) -> None:
        """Test character fields are optional and excluded when None."""
        phrase = CompositionPhrase(
            text="Test",
            duration=1.0,
            start_time=0.0,
            audioFile="audio/test.wav",
        )
        data = phrase.model_dump(exclude_none=True, by_alias=True)
        assert "characterImage" not in data
        assert "characterPosition" not in data
        assert "mouthOpenImage" not in data
        assert "eyeCloseImage" not in data
        assert "animationStyle" not in data


class TestCharacterImageIntegration:
    """Integration tests for character image in composition.json."""

    def test_character_image_in_composition(self, tmp_path: Path) -> None:
        """Test character image is included in composition.json."""
        from movie_generator.video.remotion_renderer import _get_persona_fields

        persona_map = {
            "zundamon": {
                "id": "zundamon",
                "name": "ずんだもん",
                "character_image": "assets/characters/zundamon/base.png",
                "character_position": "left",
                "subtitle_color": "#8FCF4F",
            }
        }

        persona_position_map = {"zundamon": "left"}

        phrase = Phrase(
            text="こんにちは",
            persona_id="zundamon",
            persona_name="ずんだもん",
        )

        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields["characterImage"] == "characters/zundamon/base.png"
        assert fields["characterPosition"] == "left"

    def test_character_image_path_conversion(self) -> None:
        """Test asset path is converted to public/ relative path."""
        from movie_generator.video.remotion_renderer import _convert_to_public_path

        # Test assets/ prefix removal
        assert (
            _convert_to_public_path("assets/characters/zundamon/base.png")
            == "characters/zundamon/base.png"
        )

        # Test path without assets/ prefix
        assert (
            _convert_to_public_path("characters/zundamon/base.png")
            == "characters/zundamon/base.png"
        )


class TestLipSyncAndBlinkingPhase2:
    """Tests for Phase 2: Lip sync and blinking functionality."""

    def test_lip_sync_images_in_persona_fields(self) -> None:
        """Test mouth_open_image and eye_close_image are included in persona fields."""
        from movie_generator.video.remotion_renderer import _get_persona_fields

        persona_map = {
            "zundamon": {
                "id": "zundamon",
                "name": "ずんだもん",
                "character_image": "assets/characters/zundamon/base.png",
                "mouth_open_image": "assets/characters/zundamon/mouth_open.png",
                "eye_close_image": "assets/characters/zundamon/eye_close.png",
                "character_position": "left",
                "subtitle_color": "#8FCF4F",
            }
        }

        persona_position_map = {"zundamon": "left"}

        phrase = Phrase(
            text="こんにちは",
            persona_id="zundamon",
            persona_name="ずんだもん",
        )

        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields["mouthOpenImage"] == "characters/zundamon/mouth_open.png"
        assert fields["eyeCloseImage"] == "characters/zundamon/eye_close.png"

    def test_lip_sync_images_optional(self) -> None:
        """Test lip sync images are optional (fallback to base image)."""
        from movie_generator.video.remotion_renderer import _get_persona_fields

        persona_map = {
            "speaker": {
                "id": "speaker",
                "name": "Speaker",
                "character_image": "assets/characters/speaker/base.png",
                # No mouth_open_image or eye_close_image
            }
        }

        persona_position_map = {"speaker": "center"}

        phrase = Phrase(text="Hello", persona_id="speaker", persona_name="Speaker")

        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert "mouthOpenImage" not in fields
        assert "eyeCloseImage" not in fields

    def test_full_character_animation_set(self) -> None:
        """Test complete character animation image set in CompositionPhrase."""
        phrase = CompositionPhrase(
            text="こんにちは",
            duration=2.5,
            start_time=0.0,
            audioFile="audio/phrase_0000.wav",
            character_image="characters/zundamon/base.png",
            character_position="left",
            mouth_open_image="characters/zundamon/mouth_open.png",
            eye_close_image="characters/zundamon/eye_close.png",
            animation_style="sway",
        )

        data = phrase.model_dump(exclude_none=True, by_alias=True)

        # Verify all Phase 2 fields are present
        assert data["characterImage"] == "characters/zundamon/base.png"
        assert data["characterPosition"] == "left"
        assert data["mouthOpenImage"] == "characters/zundamon/mouth_open.png"
        assert data["eyeCloseImage"] == "characters/zundamon/eye_close.png"
        assert data["animationStyle"] == "sway"


class TestAnimationStylePhase3:
    """Tests for Phase 3: Animation styles (sway, bounce, static)."""

    def test_animation_style_defaults_to_sway(self) -> None:
        """Test animation_style defaults to 'sway'."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
        )
        assert persona.animation_style == "sway"

    def test_animation_style_bounce(self) -> None:
        """Test animation_style can be set to 'bounce'."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
            animation_style="bounce",
        )
        assert persona.animation_style == "bounce"

    def test_animation_style_static(self) -> None:
        """Test animation_style can be set to 'static'."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
            animation_style="static",
        )
        assert persona.animation_style == "static"

    def test_animation_style_in_composition(self) -> None:
        """Test animation_style is included in composition data."""
        from movie_generator.video.remotion_renderer import _get_persona_fields

        persona_map = {
            "bouncer": {
                "id": "bouncer",
                "name": "Bouncer",
                "character_image": "assets/characters/bouncer/base.png",
                "animation_style": "bounce",
            }
        }

        persona_position_map = {"bouncer": "center"}

        phrase = Phrase(text="Bounce!", persona_id="bouncer", persona_name="Bouncer")

        fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        assert fields["animationStyle"] == "bounce"

    def test_static_animation_style(self) -> None:
        """Test static animation style (no animation)."""
        persona = PersonaConfig(
            id="static",
            name="Static",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
            character_image="assets/characters/static/base.png",
            animation_style="static",
        )
        assert persona.animation_style == "static"


class TestPositionAutoAssignment:
    """Tests for character position auto-assignment.

    When character_position is not explicitly set in config, positions should be
    auto-assigned based on persona order:
    - 1st persona -> left
    - 2nd persona -> right
    - 3rd+ persona -> center

    This prevents the bug where all personas defaulted to "left".
    """

    def test_position_defaults_to_none_for_auto_assignment(self) -> None:
        """Test character_position defaults to None to enable auto-assignment."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
        )
        # Default must be None, NOT "left"
        # This allows update_composition_json to auto-assign based on order
        assert persona.character_position is None

    def test_position_excluded_from_model_dump_when_none(self) -> None:
        """Test character_position is excluded from model_dump when None."""
        persona = PersonaConfig(
            id="test",
            name="Test",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
        )
        data = persona.model_dump(exclude_none=True)
        # Should NOT have character_position key when it's None
        assert "character_position" not in data

    def test_multi_persona_auto_position_assignment(self) -> None:
        """Test that multiple personas get different auto-assigned positions."""
        import json
        import tempfile

        from movie_generator.video.remotion_renderer import update_composition_json

        # Create personas WITHOUT explicit position (simulating real config)
        personas = [
            {"id": "persona1", "name": "First"},
            {"id": "persona2", "name": "Second"},
            {"id": "persona3", "name": "Third"},
        ]

        # Create phrases using different personas
        phrases = [
            Phrase(text="A", reading="A", duration=1.0, start_time=0.0),
            Phrase(text="B", reading="B", duration=1.0, start_time=1.0),
            Phrase(text="C", reading="C", duration=1.0, start_time=2.0),
        ]
        phrases[0].persona_id = "persona1"
        phrases[1].persona_id = "persona2"
        phrases[2].persona_id = "persona3"

        with tempfile.TemporaryDirectory() as tmpdir:
            remotion_root = Path(tmpdir)
            (remotion_root / "public").mkdir()

            update_composition_json(
                remotion_root=remotion_root,
                phrases=phrases,
                audio_paths=[Path(f"audio/phrase_{i:04d}.wav") for i in range(3)],
                slide_paths=None,
                project_name="test",
                personas=personas,
            )

            with open(remotion_root / "composition.json") as f:
                data = json.load(f)

            # Verify each persona gets a DIFFERENT position
            positions = [p.get("character_position") for p in data["personas"]]
            assert positions == ["left", "right", "center"], (
                f"Expected ['left', 'right', 'center'], got {positions}. "
                "Position auto-assignment is broken!"
            )
