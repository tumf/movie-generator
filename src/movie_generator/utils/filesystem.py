"""Filesystem utility functions."""

from pathlib import Path


def is_valid_file(path: Path) -> bool:
    """Check if path exists and is a non-empty file.

    Args:
        path: Path to check.

    Returns:
        True if path exists and has non-zero size.
    """
    return path.exists() and path.stat().st_size > 0


def skip_if_exists(path: Path, item_type: str = "file") -> bool:
    """Check if path exists and print skip message if it does.

    Args:
        path: Path to check.
        item_type: Type of item for message (e.g., "image", "audio", "file").

    Returns:
        True if path exists (should skip), False otherwise.
    """
    if is_valid_file(path):
        print(f"  ↷ Skipping existing {item_type}: {path.name}")
        return True
    return False
