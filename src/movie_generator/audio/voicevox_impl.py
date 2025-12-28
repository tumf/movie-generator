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
    wav_bytes = synthesizer.tts(text, speaker_id, style_id=speaker_id)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(wav_bytes)

    # Calculate duration
    with wave.open(str(output_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / rate

    return duration
