"""Audio synthesis module."""

from .dictionary import DictionaryEntry, PronunciationDictionary
from .voicevox import AudioMetadata, VoicevoxSynthesizer, create_synthesizer_from_config

__all__ = [
    "PronunciationDictionary",
    "DictionaryEntry",
    "VoicevoxSynthesizer",
    "AudioMetadata",
    "create_synthesizer_from_config",
]
