"""Script generation and phrase management module."""

from .generator import ScriptSection, VideoScript, generate_script
from .phrases import Phrase, calculate_phrase_timings, split_into_phrases

__all__ = [
    "generate_script",
    "VideoScript",
    "ScriptSection",
    "Phrase",
    "split_into_phrases",
    "calculate_phrase_timings",
]
