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
    original_index: int = 0  # Global phrase index across all sections (for file naming)

    def get_subtitle_text(self) -> str:
        """Get text suitable for subtitle display.

        Removes trailing punctuation marks that are not necessary for display.

        Returns:
            Text with trailing punctuation removed.
        """
        text = self.text
        # Remove trailing Japanese punctuation
        while text and text[-1] in ["。", "、"]:
            text = text[:-1]
        return text


def split_into_phrases(text: str, max_chars: int = 40) -> list[Phrase]:
    """Split text into phrases based on punctuation and length.

    Respects quotation marks and prioritizes natural break points.

    Args:
        text: Input text to split.
        max_chars: Maximum characters per phrase.

    Returns:
        List of Phrase objects.
    """
    # Prioritized delimiters (higher priority = better split point)
    primary_delimiters = ["。", "！", "？"]
    secondary_delimiters = ["、", "\n"]

    phrases: list[Phrase] = []
    current_phrase = ""
    in_quote = False  # Track if we're inside quotation marks

    for i, char in enumerate(text):
        current_phrase += char

        # Track quotation mark state
        if char == "「":
            in_quote = True
        elif char == "」":
            in_quote = False

        # Check if we should split here
        should_split = False

        # Primary: hit a strong delimiter outside quotes
        if not in_quote and char in primary_delimiters:
            should_split = True
        # Secondary: hit a weak delimiter outside quotes
        elif not in_quote and char in secondary_delimiters:
            should_split = True
        # Emergency: reached max length and not in quote
        elif not in_quote and len(current_phrase) >= max_chars:
            should_split = True
        # Very long phrase even with quote - split at quote boundary
        elif len(current_phrase) >= max_chars * 1.5 and char == "」":
            should_split = True

        if should_split:
            phrase_text = current_phrase.strip()
            # Only add if not just punctuation
            if phrase_text and not all(c in "。、！？\n" for c in phrase_text):
                phrases.append(Phrase(text=phrase_text))
            current_phrase = ""

    # Add remaining text
    remaining = current_phrase.strip()
    if remaining and not all(c in "。、！？\n" for c in remaining):
        phrases.append(Phrase(text=remaining))

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
