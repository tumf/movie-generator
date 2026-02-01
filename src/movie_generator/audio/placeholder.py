"""Placeholder audio synthesizer for testing without VOICEVOX.

Generates silent audio files for testing and development when VOICEVOX is not available.
"""

import wave
from dataclasses import dataclass
from pathlib import Path

from ..constants import ProjectPaths
from ..script.phrases import Phrase
from .synthesizer import AudioSynthesizer


@dataclass
class AudioMetadata:
    """Metadata for generated audio."""

    duration: float
    sample_rate: int


class PlaceholderSynthesizer(AudioSynthesizer):
    """Generates placeholder silent audio files.

    This synthesizer is used when VOICEVOX is not available but audio generation
    is still needed for testing or development purposes.
    """

    def __init__(
        self,
        duration_per_char: float = 0.1,
        speaker_id: int = 0,
        speed_scale: float = 1.0,
        dictionary: object | None = None,
    ) -> None:
        """Initialize placeholder synthesizer.

        Args:
            duration_per_char: Duration in seconds per character (default: 0.1s).
            speaker_id: Dummy speaker ID (for compatibility).
            speed_scale: Dummy speed scale (for compatibility).
            dictionary: Dummy dictionary (for compatibility).
        """
        self.duration_per_char = duration_per_char
        self.speaker_id = speaker_id
        self.speed_scale = speed_scale
        self.dictionary = dictionary

    def initialize(
        self,
        dict_dir: Path | None = None,
        model_path: Path | None = None,
        onnxruntime_path: Path | None = None,
    ) -> None:
        """Initialize the synthesizer (no-op for placeholder).

        Args:
            dict_dir: Dummy dict_dir (for compatibility).
            model_path: Dummy model_path (for compatibility).
            onnxruntime_path: Dummy onnxruntime_path (for compatibility).
        """
        pass

    def synthesize_phrase(self, phrase: Phrase, output_path: Path) -> float:
        """Generate a silent audio file as placeholder.

        Args:
            phrase: Phrase object containing text.
            output_path: Path where audio file should be saved.

        Returns:
            Duration of generated audio in seconds.
        """
        # Calculate duration based on text length
        duration = len(phrase.text) * self.duration_per_char

        # Generate silent WAV file
        sample_rate = 24000  # Match VOICEVOX sample rate
        num_samples = int(duration * sample_rate)

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            # Write silent samples (all zeros)
            wav_file.writeframes(b"\x00\x00" * num_samples)

        return duration

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

        for phrase in phrases:
            output_path = output_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
                index=phrase.original_index
            )

            # Skip if audio file already exists and is not empty
            if output_path.exists() and output_path.stat().st_size > 0:
                try:
                    # Read existing metadata
                    with wave.open(str(output_path), "rb") as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration = frames / float(rate)
                    metadata = AudioMetadata(duration=duration, sample_rate=rate)
                    audio_paths.append(output_path)
                    metadata_list.append(metadata)
                    phrase.duration = duration
                    continue
                except Exception:
                    # File is corrupted, regenerate
                    pass

            # Synthesize phrase
            duration = self.synthesize_phrase(phrase, output_path)
            phrase.duration = duration

            metadata = AudioMetadata(duration=duration, sample_rate=24000)
            audio_paths.append(output_path)
            metadata_list.append(metadata)

        return audio_paths, metadata_list
