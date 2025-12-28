"""VOICEVOX audio synthesis integration.

Integrates with VOICEVOX Core for text-to-speech generation.
"""

import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..script.phrases import Phrase
from .dictionary import PronunciationDictionary

try:
    from . import voicevox_impl  # type: ignore

    VOICEVOX_AVAILABLE = True
except ImportError:
    VOICEVOX_AVAILABLE = False
    voicevox_impl = None


@dataclass
class AudioMetadata:
    """Metadata for generated audio."""

    duration: float  # Duration in seconds
    sample_rate: int = 24000
    channels: int = 1


class VoicevoxSynthesizer:
    """VOICEVOX synthesizer wrapper.

    Integrates VOICEVOX Core with user dictionary support.
    Falls back to placeholder mode if voicevox_core is not available.
    """

    def __init__(
        self,
        speaker_id: int = 3,
        speed_scale: float = 1.0,
        dictionary: PronunciationDictionary | None = None,
        allow_placeholder: bool = False,
    ) -> None:
        """Initialize synthesizer.

        Args:
            speaker_id: VOICEVOX speaker ID (3=Zundamon).
            speed_scale: Speech speed scale.
            dictionary: Pronunciation dictionary.
            allow_placeholder: Allow placeholder mode when voicevox_core is not installed.
                              If False (default), raises ImportError when voicevox_core is unavailable.

        Raises:
            ImportError: If voicevox_core is not installed and allow_placeholder is False.
        """
        if not VOICEVOX_AVAILABLE and not allow_placeholder:
            raise ImportError(
                "VOICEVOX Core is not installed and is required for audio synthesis.\n"
                "Please install voicevox_core or see docs/VOICEVOX_SETUP.md for instructions.\n"
                "To run without VOICEVOX (placeholder mode for testing), "
                "set allow_placeholder=True."
            )

        self.speaker_id = speaker_id
        self.speed_scale = speed_scale
        self.dictionary = dictionary or PronunciationDictionary()
        self.allow_placeholder = allow_placeholder

        self._synthesizer: Any = None
        self._initialized = False

    def initialize(
        self,
        dict_dir: Path,
        model_path: Path,
        onnxruntime_path: Path | None = None,
    ) -> None:
        """Initialize VOICEVOX Core.

        Args:
            dict_dir: Path to OpenJTalk dictionary directory.
            model_path: Path to VOICEVOX model file (.vvm).
            onnxruntime_path: Path to ONNX Runtime library (optional).

        Raises:
            ImportError: If voicevox_core is not available.
            FileNotFoundError: If required files don't exist.
        """
        if not VOICEVOX_AVAILABLE:
            raise ImportError(
                "voicevox_core is not installed. Install it manually or run in placeholder mode."
            )

        # Create user dictionary if we have entries
        user_dict = None
        if self.dictionary.entries:
            user_dict = voicevox_impl.create_user_dict(self.dictionary.entries)  # type: ignore

        # Initialize synthesizer
        self._synthesizer = voicevox_impl.initialize_voicevox(  # type: ignore
            dict_dir=dict_dir,
            model_path=model_path,
            user_dict=user_dict,
            onnxruntime_path=onnxruntime_path,
        )

        self._initialized = True

    def synthesize_phrase(self, phrase: Phrase, output_path: Path) -> AudioMetadata:
        """Synthesize audio for a single phrase.

        Args:
            phrase: Phrase to synthesize.
            output_path: Path to save audio file.

        Returns:
            Audio metadata with duration.

        Raises:
            RuntimeError: If synthesizer not initialized.
        """
        if not self._initialized:
            raise RuntimeError("Synthesizer not initialized. Call initialize() first.")

        if VOICEVOX_AVAILABLE and self._synthesizer is not None:
            # Real VOICEVOX synthesis
            duration = voicevox_impl.synthesize_to_file(  # type: ignore
                synthesizer=self._synthesizer,
                text=phrase.text,
                speaker_id=self.speaker_id,
                output_path=output_path,
                speed_scale=self.speed_scale,
            )
        else:
            # Placeholder mode
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"")
            duration = len(phrase.text) * 0.15  # ~150ms per character

        return AudioMetadata(duration=duration)

    def synthesize_phrases(
        self, phrases: list[Phrase], output_dir: Path
    ) -> tuple[list[Path], list[AudioMetadata]]:
        """Synthesize audio for multiple phrases.

        Args:
            phrases: List of phrases to synthesize.
            output_dir: Directory to save audio files.

        Returns:
            Tuple of (audio file paths, metadata list).
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_paths: list[Path] = []
        metadata_list: list[AudioMetadata] = []

        for i, phrase in enumerate(phrases):
            output_path = output_dir / f"phrase_{i:04d}.wav"
            metadata = self.synthesize_phrase(phrase, output_path)

            # Update phrase duration
            phrase.duration = metadata.duration

            audio_paths.append(output_path)
            metadata_list.append(metadata)

        return audio_paths, metadata_list


def create_synthesizer_from_config(
    config: Any, allow_placeholder: bool = False
) -> VoicevoxSynthesizer:
    """Create synthesizer from configuration.

    Args:
        config: Configuration object.
        allow_placeholder: Allow placeholder mode when voicevox_core is not installed.

    Returns:
        Initialized synthesizer.

    Raises:
        ImportError: If voicevox_core is not installed and allow_placeholder is False.
    """
    dictionary = PronunciationDictionary()
    if hasattr(config, "pronunciation") and config.pronunciation.custom:
        dictionary.add_from_config(config.pronunciation.custom)

    return VoicevoxSynthesizer(
        speaker_id=config.audio.speaker_id,
        speed_scale=config.audio.speed_scale,
        dictionary=dictionary,
        allow_placeholder=allow_placeholder,
    )
