"""Phrase splitting for subtitle and audio synchronization.

Splits narration text into 3-6 second phrases for optimal subtitle display.
"""

from dataclasses import dataclass


@dataclass
class Phrase:
    """A single phrase with timing information."""

    text: str
    duration: float = 0.0  # In seconds, filled by audio generation
    start_time: float = 0.0  # Cumulative start time
    section_index: int = 0  # Index of the section this phrase belongs to


def split_into_phrases(text: str, max_chars: int = 50) -> list[Phrase]:
    """Split text into phrases based on punctuation and length.

    Args:
        text: Input text to split.
        max_chars: Maximum characters per phrase.

    Returns:
        List of Phrase objects.
    """
    # Split by Japanese punctuation marks
    delimiters = ["。", "、", "！", "？", "\n"]

    phrases: list[Phrase] = []
    current_phrase = ""

    for char in text:
        current_phrase += char

        # Check if we hit a delimiter or reached max length
        if char in delimiters or len(current_phrase) >= max_chars:
            phrase_text = current_phrase.strip()
            if phrase_text:
                phrases.append(Phrase(text=phrase_text))
            current_phrase = ""

    # Add remaining text
    if current_phrase.strip():
        phrases.append(Phrase(text=current_phrase.strip()))

    return phrases


def calculate_phrase_timings(phrases: list[Phrase]) -> list[Phrase]:
    """Calculate cumulative start times for phrases.

    Args:
        phrases: List of phrases with duration already set.

    Returns:
        Updated list with start_time filled.
    """
    cumulative_time = 0.0
    for phrase in phrases:
        phrase.start_time = cumulative_time
        cumulative_time += phrase.duration

    return phrases
