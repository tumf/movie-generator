"""Automatic furigana generation using morphological analysis.

Uses fugashi (MeCab wrapper) with UniDic to analyze Japanese text
and generate accurate readings for all words.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fugashi import Tagger


@dataclass
class MorphemeReading:
    """A morpheme with its surface form and reading."""

    surface: str  # Original text (e.g., "表計算")
    reading: str  # Katakana reading (e.g., "ヒョウケイサン")
    pos: str  # Part of speech (e.g., "名詞")


class FuriganaGenerator:
    """Generate furigana readings using morphological analysis.

    Uses fugashi with UniDic dictionary for accurate Japanese text analysis.
    Provides readings for kanji and other words that may be mispronounced
    by text-to-speech engines.
    """

    def __init__(self) -> None:
        """Initialize the morphological analyzer.

        The tagger is lazily initialized on first use.
        """
        self._tagger: Tagger | None = None

    @property
    def tagger(self) -> "Tagger":
        """Lazy initialization of fugashi Tagger.

        Returns:
            Initialized Tagger instance.

        Raises:
            ImportError: If fugashi or unidic is not installed.
        """
        if self._tagger is None:
            try:
                from fugashi import Tagger as FugashiTagger

                self._tagger = FugashiTagger()
            except ImportError as e:
                raise ImportError(
                    "fugashi is required for furigana generation. "
                    "Install it with: pip install fugashi unidic"
                ) from e
        return self._tagger

    def analyze(self, text: str) -> list[MorphemeReading]:
        """Analyze text and return morphemes with readings.

        Args:
            text: Japanese text to analyze.

        Returns:
            List of morphemes with surface forms and readings.
        """
        result: list[MorphemeReading] = []
        for word in self.tagger(text):
            surface: str = word.surface
            # UniDic provides reading in feature.kana
            feature: Any = word.feature
            reading: str = getattr(feature, "kana", None) or surface
            pos: str = getattr(feature, "pos1", None) or "Unknown"
            result.append(MorphemeReading(surface=surface, reading=reading, pos=pos))
        return result

    def get_readings_dict(self, text: str) -> dict[str, str]:
        """Get a dictionary mapping surface forms to readings.

        Only includes entries where surface differs from reading
        (i.e., words containing kanji or special readings).

        Args:
            text: Japanese text to analyze.

        Returns:
            Dictionary of {surface: reading} pairs.
        """
        readings: dict[str, str] = {}
        for morpheme in self.analyze(text):
            # Only add if reading differs from surface (i.e., has kanji)
            if morpheme.surface != morpheme.reading and morpheme.reading:
                # Skip single characters that are punctuation or symbols
                if len(morpheme.surface) == 1 and not morpheme.surface.isalnum():
                    continue
                readings[morpheme.surface] = morpheme.reading
        return readings

    def analyze_texts(self, texts: list[str]) -> dict[str, str]:
        """Analyze multiple texts and return combined readings dictionary.

        Useful for batch processing all phrases before audio generation.

        Args:
            texts: List of Japanese texts to analyze.

        Returns:
            Combined dictionary of {surface: reading} pairs from all texts.
        """
        combined: dict[str, str] = {}
        for text in texts:
            readings = self.get_readings_dict(text)
            # Later texts don't override earlier readings
            for surface, reading in readings.items():
                if surface not in combined:
                    combined[surface] = reading
        return combined
