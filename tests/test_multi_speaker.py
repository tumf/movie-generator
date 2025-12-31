"""Tests for multi-speaker dialogue functionality."""

import pytest
from pydantic import ValidationError

from movie_generator.config import Config, NarrationConfig, PersonaConfig, VoicevoxSynthesizerConfig
from movie_generator.script.phrases import Phrase


class TestPersonaConfig:
    """Test PersonaConfig model."""

    def test_persona_config_creation(self) -> None:
        """Test creating a valid PersonaConfig."""
        persona = PersonaConfig(
            id="zundamon",
            name="ずんだもん",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
            subtitle_color="#00FF00",
        )
        assert persona.id == "zundamon"
        assert persona.name == "ずんだもん"
        assert persona.synthesizer.speaker_id == 3
        assert persona.subtitle_color == "#00FF00"

    def test_persona_config_with_character(self) -> None:
        """Test PersonaConfig with character description."""
        persona = PersonaConfig(
            id="metan",
            name="四国めたん",
            character="A cheerful girl from Shikoku",
            synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
        )
        assert persona.id == "metan"
        assert persona.name == "四国めたん"
        assert persona.character == "A cheerful girl from Shikoku"


class TestConfigWithPersonas:
    """Test Config with personas."""

    def test_config_with_multiple_personas(self) -> None:
        """Test Config with multiple personas."""
        config = Config(
            personas=[
                PersonaConfig(
                    id="alice",
                    name="Alice",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
                    subtitle_color="#FF6B6B",
                ),
                PersonaConfig(
                    id="bob",
                    name="Bob",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
                    subtitle_color="#4ECDC4",
                ),
            ]
        )
        assert len(config.personas) == 2
        assert config.personas[0].id == "alice"
        assert config.personas[1].id == "bob"
        assert config.personas[0].synthesizer.speaker_id == 1
        assert config.personas[1].synthesizer.speaker_id == 2

    def test_config_without_personas(self) -> None:
        """Test Config without personas (backward compatible)."""
        config = Config()
        assert config.personas == []

    def test_config_duplicate_persona_ids_raises_error(self) -> None:
        """Test that duplicate persona IDs raise validation error."""
        with pytest.raises(Exception):  # ConfigurationError
            Config(
                personas=[
                    PersonaConfig(
                        id="alice",
                        name="Alice",
                        synthesizer=VoicevoxSynthesizerConfig(speaker_id=1),
                    ),
                    PersonaConfig(
                        id="alice",  # Duplicate ID
                        name="Alice2",
                        synthesizer=VoicevoxSynthesizerConfig(speaker_id=2),
                    ),
                ]
            )


class TestPhrasePersonaFields:
    """Test Phrase model with persona fields."""

    def test_phrase_with_persona(self) -> None:
        """Test Phrase with persona information."""
        phrase = Phrase(
            text="こんにちは",
            persona_id="alice",
            persona_name="Alice",
        )
        assert phrase.text == "こんにちは"
        assert phrase.persona_id == "alice"
        assert phrase.persona_name == "Alice"

    def test_phrase_without_persona(self) -> None:
        """Test Phrase without persona (backward compatible)."""
        phrase = Phrase(text="こんにちは")
        assert phrase.text == "こんにちは"
        # Empty string is the default for persona fields
        assert phrase.persona_id == ""
        assert phrase.persona_name == ""


class TestMultiSpeakerDialogue:
    """Test multi-speaker dialogue mode."""

    def test_multi_speaker_config(self) -> None:
        """Test Config with multiple personas (enables multi-speaker mode automatically)."""
        config = Config(
            narration=NarrationConfig(character="", style="casual"),
            personas=[
                PersonaConfig(
                    id="zundamon",
                    name="ずんだもん",
                    character="東北地方の妖精マスコット",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=3),
                    subtitle_color="#00FF00",
                ),
                PersonaConfig(
                    id="metan",
                    name="四国めたん",
                    character="四国地方のツンデレキャラ",
                    synthesizer=VoicevoxSynthesizerConfig(speaker_id=2, speed_scale=1.1),
                    subtitle_color="#FF6B9D",
                ),
            ],
        )
        # Multi-speaker mode is determined by presence of personas
        assert len(config.personas) == 2
        assert config.personas[0].id == "zundamon"
        assert config.personas[1].id == "metan"
        # Character in narration is not used in multi-speaker mode
        assert config.narration.character == ""
