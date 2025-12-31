"""VOICEVOX Core implementation (requires voicevox_core package).

This module contains the actual VOICEVOX integration.
Separated to allow optional dependency.
"""

import wave
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dictionary import DictionaryEntry

from voicevox_core import UserDictWord  # type: ignore
from voicevox_core.blocking import (  # type: ignore
    Onnxruntime,
    OpenJtalk,
    Synthesizer,
    UserDict,
    VoiceModelFile,
)

from ..script.phrases import Phrase
from .synthesizer import AudioSynthesizer


def create_user_dict(entries: dict[str, "DictionaryEntry"]) -> UserDict:
    """Create VOICEVOX UserDict from dictionary entries.

    Args:
        entries: Dictionary entries mapping surface to entry.

    Returns:
        Initialized UserDict.
    """
    user_dict = UserDict()
    for entry in entries.values():
        # Cast to literal type for type checker
        word_type: str = entry.word_type
        user_dict.add_word(
            UserDictWord(
                surface=entry.surface,
                pronunciation=entry.reading,
                accent_type=entry.accent,
                word_type=word_type,  # type: ignore
                priority=entry.priority,
            )
        )
    return user_dict


def initialize_voicevox(
    dict_dir: Path,
    model_path: Path,
    user_dict: UserDict | None = None,
    onnxruntime_path: Path | None = None,
) -> Synthesizer:
    """Initialize VOICEVOX Core synthesizer.

    Args:
        dict_dir: Path to OpenJTalk dictionary directory.
        model_path: Path to VOICEVOX model file (.vvm).
        user_dict: Optional user dictionary.
        onnxruntime_path: Optional path to ONNX Runtime library.

    Returns:
        Initialized Synthesizer instance.

    Raises:
        FileNotFoundError: If required files don't exist.
    """
    if not dict_dir.exists():
        raise FileNotFoundError(f"OpenJTalk dictionary not found: {dict_dir}")
    if not model_path.exists():
        raise FileNotFoundError(f"Voice model not found: {model_path}")

    # Initialize OpenJTalk
    open_jtalk = OpenJtalk(dict_dir)
    if user_dict is not None:
        open_jtalk.use_user_dict(user_dict)

    # Initialize ONNX Runtime
    if onnxruntime_path and onnxruntime_path.exists():
        onnxruntime = Onnxruntime.load_once(filename=str(onnxruntime_path))
    else:
        onnxruntime = Onnxruntime.load_once()

    # Create synthesizer
    synthesizer = Synthesizer(onnxruntime, open_jtalk)

    # Load voice model
    model = VoiceModelFile.open(model_path)
    synthesizer.load_voice_model(model)

    return synthesizer


def synthesize_to_file(
    synthesizer: Synthesizer,
    text: str,
    speaker_id: int,
    output_path: Path,
    speed_scale: float = 1.0,
) -> float:
    """Synthesize speech and save to WAV file.

    Args:
        synthesizer: VOICEVOX Synthesizer instance.
        text: Text to synthesize.
        speaker_id: Speaker ID.
        output_path: Path to save WAV file.
        speed_scale: Speech speed scale.

    Returns:
        Duration of generated audio in seconds.
    """
    # Generate audio
    wav_bytes = synthesizer.tts(text, speaker_id)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(wav_bytes)

    # Calculate duration
    with wave.open(str(output_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / rate

    return duration


class VoicevoxSynthesizer(AudioSynthesizer):
    """VOICEVOX audio synthesizer implementation."""

    def __init__(
        self,
        speaker_id: int,
        speed_scale: float = 1.0,
        dict_dir: Path | None = None,
        model_path: Path | None = None,
        onnxruntime_path: Path | None = None,
        user_dict: UserDict | None = None,
    ):
        """Initialize VOICEVOX synthesizer.

        Args:
            speaker_id: VOICEVOX speaker ID.
            speed_scale: Speech speed multiplier.
            dict_dir: Path to OpenJTalk dictionary.
            model_path: Path to VOICEVOX model file.
            onnxruntime_path: Path to ONNX Runtime library.
            user_dict: Optional user dictionary.
        """
        self.speaker_id = speaker_id
        self.speed_scale = speed_scale
        self.dict_dir = dict_dir
        self.model_path = model_path
        self.onnxruntime_path = onnxruntime_path
        self.user_dict = user_dict
        self._synthesizer: Synthesizer | None = None

    def initialize(self) -> None:
        """Initialize the VOICEVOX synthesizer.

        Raises:
            RuntimeError: If initialization fails.
            FileNotFoundError: If required files are missing.
        """
        if self._synthesizer is not None:
            return  # Already initialized

        if self.dict_dir is None or self.model_path is None:
            raise RuntimeError(
                "dict_dir and model_path must be provided for VOICEVOX initialization"
            )

        self._synthesizer = initialize_voicevox(
            dict_dir=self.dict_dir,
            model_path=self.model_path,
            user_dict=self.user_dict,
            onnxruntime_path=self.onnxruntime_path,
        )

    def synthesize_phrase(self, phrase: Phrase, output_path: Path) -> float:
        """Synthesize a single phrase to audio file.

        Args:
            phrase: Phrase object containing text.
            output_path: Path where audio file should be saved.

        Returns:
            Duration of generated audio in seconds.

        Raises:
            RuntimeError: If synthesizer is not initialized.
        """
        if self._synthesizer is None:
            raise RuntimeError("Synthesizer not initialized. Call initialize() first.")

        return synthesize_to_file(
            synthesizer=self._synthesizer,
            text=phrase.text,
            speaker_id=self.speaker_id,
            output_path=output_path,
            speed_scale=self.speed_scale,
        )
