"""Pronunciation dictionary management for VOICEVOX.

Manages user dictionary for correct pronunciation of proper nouns.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..utils.text import clean_katakana_reading, is_valid_katakana_reading  # type: ignore[import]


class DictionaryEntry(BaseModel):
    """A pronunciation dictionary entry."""

    surface: str  # Original text
    reading: str  # Katakana reading
    accent: int = 0  # Accent position (0=auto)
    word_type: str = "PROPER_NOUN"
    priority: int = 10


class PronunciationDictionary:
    """Manager for pronunciation dictionary."""

    def __init__(self) -> None:
        """Initialize empty dictionary."""
        self.entries: dict[str, DictionaryEntry] = {}

    def add_entry(self, entry: DictionaryEntry) -> bool:
        """Add an entry to the dictionary.

        Args:
            entry: Dictionary entry to add.

        Returns:
            True if entry was added, False if skipped due to invalid reading.
        """
        # Ensure reading has no spaces and only katakana (final validation)
        entry.reading = clean_katakana_reading(entry.reading)

        # Skip if reading is empty or invalid after cleaning
        if not is_valid_katakana_reading(entry.reading):
            return False

        self.entries[entry.surface] = entry
        return True

    def add_word(
        self,
        word: str,
        reading: str,
        accent: int = 0,
        word_type: str = "COMMON_NOUN",
        priority: int = 10,
    ) -> bool:
        """Add a single word to the dictionary.

        Args:
            word: The word/phrase to add.
            reading: Katakana reading (spaces will be removed automatically).
            accent: Accent position (0=auto).
            word_type: Word type (PROPER_NOUN, COMMON_NOUN, etc).
            priority: Priority (1-10, higher = more priority).

        Returns:
            True if entry was added, False if skipped due to invalid reading.
        """
        # Remove spaces from reading (VOICEVOX requires katakana-only)
        entry = DictionaryEntry(
            surface=word,
            reading=clean_katakana_reading(reading),
            accent=accent,
            word_type=word_type,
            priority=priority,
        )
        return self.add_entry(entry)

    def add_from_config(self, config_dict: dict[str, Any]) -> None:
        """Add entries from configuration dictionary.

        Args:
            config_dict: Dictionary from YAML config.
        """
        for surface, value in config_dict.items():
            if isinstance(value, str):
                # Simple format: just reading
                entry = DictionaryEntry(surface=surface, reading=clean_katakana_reading(value))
            elif isinstance(value, dict):
                # Full format with all fields
                entry = DictionaryEntry(
                    surface=surface,
                    reading=clean_katakana_reading(value["reading"]),
                    accent=value.get("accent", 0),
                    word_type=value.get("word_type", "PROPER_NOUN"),
                    priority=value.get("priority", 10),
                )
            else:
                continue

            self.add_entry(entry)

    def save(self, path: Path) -> None:
        """Save dictionary to JSON file.

        Args:
            path: Path to save dictionary.
        """
        data = {
            surface: {
                "reading": entry.reading,
                "accent": entry.accent,
                "word_type": entry.word_type,
                "priority": entry.priority,
            }
            for surface, entry in self.entries.items()
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: Path) -> None:
        """Load dictionary from JSON file.

        Args:
            path: Path to load dictionary from.
        """
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.entries.clear()
        self.add_from_config(data)

    def add_from_morphemes(
        self,
        readings: dict[str, str],
        priority: int = 5,
        word_type: str = "COMMON_NOUN",
    ) -> int:
        """Add entries from morphological analysis results.

        Auto-generated readings have lower priority than manual entries,
        so manual/LLM-specified readings take precedence.

        Args:
            readings: Dictionary mapping surface forms to readings.
            priority: Priority for auto-generated entries (default 5, lower than manual 10).
            word_type: Word type for auto-generated entries.

        Returns:
            Number of new entries actually added.
        """
        added = 0
        for surface, reading in readings.items():
            # Skip if already registered (manual entries take precedence)
            if surface in self.entries:
                continue
            success = self.add_word(
                word=surface,
                reading=reading,
                word_type=word_type,
                priority=priority,
            )
            if success:
                added += 1
        return added

    def apply_to_text(self, text: str) -> str:
        """Apply dictionary to text (simple replacement for testing).

        This is a simplified version for testing without VOICEVOX Core.
        Real implementation should use VOICEVOX UserDict API.

        Args:
            text: Input text.

        Returns:
            Text with replacements applied.
        """
        result = text
        for entry in self.entries.values():
            # Note: This is NOT the correct way - just for testing
            # Real implementation uses VOICEVOX UserDict
            result = result.replace(entry.surface, entry.reading)
        return result
