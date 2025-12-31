"""Text processing utilities."""

import re


def clean_katakana_reading(text: str) -> str:
    """Clean katakana reading text for VOICEVOX.

    Removes spaces and filters out non-katakana characters.
    VOICEVOX requires pure katakana readings (ァ-ヴ and ー).

    Args:
        text: Katakana reading text to clean.

    Returns:
        Text with only katakana characters.
    """
    # Remove spaces first
    text = text.replace(" ", "").replace("　", "")
    # Keep only katakana characters (ァ-ヴ) and long vowel mark (ー)
    return re.sub(r"[^ァ-ヴー]", "", text)


def is_valid_katakana_reading(text: str) -> bool:
    """Check if text is a valid katakana reading for VOICEVOX.

    Args:
        text: Text to validate.

    Returns:
        True if text contains only valid katakana characters.
    """
    if not text:
        return False
    # Must contain only katakana (ァ-ヴ) and long vowel mark (ー)
    return bool(re.fullmatch(r"[ァ-ヴー]+", text))
