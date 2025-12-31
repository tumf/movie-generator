"""Text processing utilities."""


def clean_katakana_reading(text: str) -> str:
    """Remove spaces from katakana reading text.

    Removes both ASCII space and full-width space (　) characters.

    Args:
        text: Katakana reading text to clean.

    Returns:
        Text with all spaces removed.
    """
    return text.replace(" ", "").replace("　", "")
