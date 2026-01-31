"""Audio synthesizer abstraction layer.

Provides an abstract interface for audio synthesis engines.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..constants import ProjectPaths
from ..script.phrases import Phrase


class AudioSynthesizer(ABC):
    """Abstract base class for audio synthesizers."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the synthesizer.

        This method should be called before any synthesis operations.
        Subclasses should implement engine-specific initialization here.

        Raises:
            RuntimeError: If initialization fails.
        """
        pass

    @abstractmethod
    def synthesize_phrase(
        self,
        phrase: Phrase,
        output_path: Path,
    ) -> float:
        """Synthesize a single phrase to audio file.

        Args:
            phrase: Phrase object containing text and metadata.
            output_path: Path where audio file should be saved.

        Returns:
            Duration of generated audio in seconds.

        Raises:
            RuntimeError: If synthesis fails.
        """
        pass

    def synthesize_phrases(
        self,
        phrases: list[Phrase],
        output_dir: Path,
    ) -> list[Phrase]:
        """Synthesize multiple phrases to audio files.

        Default implementation calls synthesize_phrase for each phrase.
        Subclasses can override for batch optimization.

        Args:
            phrases: List of Phrase objects.
            output_dir: Directory where audio files should be saved.

        Returns:
            List of Phrase objects with duration filled in.

        Raises:
            RuntimeError: If synthesis fails.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for phrase in phrases:
            output_path = output_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
                index=phrase.original_index
            )
            duration = self.synthesize_phrase(phrase, output_path)
            phrase.duration = duration

        return phrases


class SynthesizerFactory:
    """Factory for creating audio synthesizer instances."""

    @staticmethod
    def create(engine: str, **kwargs: Any) -> AudioSynthesizer:
        """Create an audio synthesizer instance.

        Args:
            engine: Synthesizer engine type (e.g., "voicevox", "placeholder").
            **kwargs: Engine-specific parameters.

        Returns:
            AudioSynthesizer instance.

        Raises:
            ValueError: If engine is not supported.
        """
        if engine == "voicevox":
            from .voicevox_impl import VoicevoxSynthesizer

            return VoicevoxSynthesizer(**kwargs)
        elif engine == "placeholder":
            from .placeholder import PlaceholderSynthesizer

            return PlaceholderSynthesizer(**kwargs)
        else:
            raise ValueError(
                f"Unsupported synthesizer engine: {engine}. "
                f"Supported engines: voicevox, placeholder"
            )
