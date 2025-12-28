"""Tests for VOICEVOX integration."""

import pytest
from pathlib import Path
from movie_generator.audio.dictionary import PronunciationDictionary, DictionaryEntry
from movie_generator.audio.voicevox import VoicevoxSynthesizer, VOICEVOX_AVAILABLE
from movie_generator.script.phrases import Phrase


def test_dictionary_creation():
    """Test pronunciation dictionary creation."""
    dictionary = PronunciationDictionary()

    entry = DictionaryEntry(
        surface="GitHub",
        reading="ギットハブ",
        accent=4,
        word_type="PROPER_NOUN",
        priority=10,
    )
    dictionary.add_entry(entry)

    assert "GitHub" in dictionary.entries
    assert dictionary.entries["GitHub"].reading == "ギットハブ"


def test_dictionary_from_config():
    """Test loading dictionary from config."""
    dictionary = PronunciationDictionary()

    config = {
        "GitHub": {
            "reading": "ギットハブ",
            "accent": 4,
            "word_type": "PROPER_NOUN",
            "priority": 10,
        },
        "Ratatui": "ラタトゥイ",  # Simple format
    }

    dictionary.add_from_config(config)

    assert len(dictionary.entries) == 2
    assert dictionary.entries["GitHub"].reading == "ギットハブ"
    assert dictionary.entries["GitHub"].accent == 4
    assert dictionary.entries["Ratatui"].reading == "ラタトゥイ"
    assert dictionary.entries["Ratatui"].accent == 0  # Default


def test_dictionary_save_load(tmp_path: Path):
    """Test dictionary serialization."""
    dictionary = PronunciationDictionary()

    dictionary.add_entry(
        DictionaryEntry(
            surface="Test",
            reading="テスト",
            accent=2,
        )
    )

    dict_file = tmp_path / "dict.json"
    dictionary.save(dict_file)

    loaded_dict = PronunciationDictionary()
    loaded_dict.load(dict_file)

    assert "Test" in loaded_dict.entries
    assert loaded_dict.entries["Test"].reading == "テスト"
    assert loaded_dict.entries["Test"].accent == 2


def test_synthesizer_initialization():
    """Test synthesizer initialization."""
    dictionary = PronunciationDictionary()
    dictionary.add_entry(
        DictionaryEntry(
            surface="Test",
            reading="テスト",
        )
    )

    synth = VoicevoxSynthesizer(
        speaker_id=3,
        speed_scale=1.0,
        dictionary=dictionary,
    )

    assert synth.speaker_id == 3
    assert synth.speed_scale == 1.0
    assert len(synth.dictionary.entries) == 1


@pytest.mark.skipif(not VOICEVOX_AVAILABLE, reason="voicevox_core not installed")
def test_synthesizer_real_init(tmp_path: Path):
    """Test real VOICEVOX initialization (if available)."""
    # This test requires actual VOICEVOX files to be present
    # Skip if files don't exist
    dict_dir = Path("/path/to/open_jtalk_dict")
    model_path = Path("/path/to/model.vvm")

    if not dict_dir.exists() or not model_path.exists():
        pytest.skip("VOICEVOX files not available")

    synth = VoicevoxSynthesizer()
    synth.initialize(dict_dir=dict_dir, model_path=model_path)

    assert synth._initialized is True


def test_synthesizer_placeholder_mode(tmp_path: Path):
    """Test synthesizer in placeholder mode."""
    synth = VoicevoxSynthesizer()
    # Don't initialize - test placeholder synthesis

    phrase = Phrase(text="これはテストです")

    # In placeholder mode, should raise error if not initialized
    output_path = tmp_path / "test.wav"

    with pytest.raises(RuntimeError, match="not initialized"):
        synth.synthesize_phrase(phrase, output_path)
