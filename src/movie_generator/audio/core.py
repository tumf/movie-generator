"""Core audio generation functionality.

Provides library functions for audio synthesis that can be called
directly by worker processes or other Python code, without CLI overhead.
"""

import logging
import os
import wave
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from ..config import Config, load_config
from ..script.generator import Narration, ScriptSection, VideoScript
from ..script.phrases import Phrase, calculate_phrase_timings
from .voicevox import VoicevoxSynthesizer, create_synthesizer_from_config

logger = logging.getLogger(__name__)


def validate_persona_ids(
    phrases: list[Phrase],
    synthesizers: dict[str, Any],
    *,
    strict: bool = False,
) -> list[str]:
    """Validate that all persona_ids in phrases exist in synthesizers.

    Args:
        phrases: List of phrases to validate.
        synthesizers: Dictionary of available synthesizers keyed by persona_id.
        strict: If True, raises ValueError when unknown persona_ids are found.
                If False, only logs warnings.

    Returns:
        List of unknown persona_ids found in phrases.

    Raises:
        ValueError: If strict mode is enabled and unknown persona_ids exist.
    """
    unknown_ids = []
    seen_unknowns = set()

    for phrase in phrases:
        persona_id = phrase.persona_id
        if persona_id and persona_id not in synthesizers:
            if persona_id not in seen_unknowns:
                unknown_ids.append(persona_id)
                seen_unknowns.add(persona_id)
                logger.warning(
                    f"Unknown persona_id '{persona_id}' in phrase: {phrase.text[:50]}..."
                )

    if unknown_ids and strict:
        raise ValueError(
            f"Unknown persona_id(s) found: {', '.join(unknown_ids)}. "
            f"Available personas: {', '.join(synthesizers.keys())}"
        )

    return unknown_ids


def generate_audio_for_script(
    script_path: Path,
    output_dir: Path | None = None,
    config_path: Path | None = None,
    config: Config | None = None,
    scenes: tuple[int | None, int | None] | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> list[Phrase]:
    """Generate audio files from script.yaml.

    Reads the script, converts narrations to phrases, and synthesizes
    audio using VOICEVOX. This is the core function that can be called
    directly without CLI overhead.

    Args:
        script_path: Path to script.yaml file.
        output_dir: Output directory for audio files. If None, uses script.parent / "audio".
        config_path: Path to config file (mutually exclusive with config).
        config: Config object (mutually exclusive with config_path).
        scenes: Optional scene range (start_index, end_index), 0-based inclusive.
                Either value can be None to indicate "from beginning" or "to end".
        progress_callback: Optional callback(current, total, message) called during generation.

    Returns:
        List of generated phrases with timing information.

    Raises:
        FileNotFoundError: If script file doesn't exist.
        RuntimeError: If VOICEVOX initialization fails.
        ValueError: If config_path and config are both provided.

    Example:
        >>> phrases = generate_audio_for_script(
        ...     script_path=Path("script.yaml"),
        ...     output_dir=Path("audio"),
        ...     config_path=Path("config.yaml"),
        ...     progress_callback=lambda c, t, m: print(f"{c}/{t}: {m}")
        ... )
    """
    # Validate arguments
    if config_path and config:
        raise ValueError("Cannot specify both config_path and config")

    if not script_path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")

    # Load configuration
    if config is None:
        cfg = load_config(config_path) if config_path else Config()
    else:
        cfg = config

    # Determine output directory
    if output_dir is None:
        output_dir = script_path.parent
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Parse scene range
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes is not None:
        scene_start, scene_end = scenes

    # Load and parse script
    with open(script_path, encoding="utf-8") as f:
        script_dict = yaml.safe_load(f)

    sections = []
    for section in script_dict["sections"]:
        narrations: list[Narration] = []

        if "narrations" in section and section["narrations"]:
            for n in section["narrations"]:
                if isinstance(n, str):
                    narrations.append(Narration(text=n, reading=n))
                else:
                    reading = n.get("reading", n["text"])
                    narrations.append(
                        Narration(text=n["text"], reading=reading, persona_id=n.get("persona_id"))
                    )
        elif "dialogues" in section and section["dialogues"]:
            for d in section["dialogues"]:
                reading = d.get("reading", d["narration"])
                narrations.append(
                    Narration(text=d["narration"], reading=reading, persona_id=d["persona_id"])
                )
        elif "narration" in section:
            narrations.append(Narration(text=section["narration"], reading=section["narration"]))

        sections.append(
            ScriptSection(
                title=section["title"],
                narrations=narrations,
                slide_prompt=section.get("slide_prompt"),
                source_image_url=section.get("source_image_url"),
                background=section.get("background"),
            )
        )

    video_script = VideoScript(
        title=script_dict["title"],
        description=script_dict["description"],
        sections=sections,
    )

    # Convert to phrases
    all_sections_phrases = []
    for section_idx, section in enumerate(video_script.sections):
        section_phrases = []
        for narration in section.narrations:
            phrase = Phrase(text=narration.text, reading=narration.reading)
            phrase.section_index = section_idx
            if narration.persona_id:
                phrase.persona_id = narration.persona_id
                if cfg.personas:
                    for p in cfg.personas:
                        if p.id == narration.persona_id:
                            phrase.persona_name = p.name
                            break
            section_phrases.append(phrase)
        all_sections_phrases.append((section_idx, section_phrases))

    # Set original_index
    global_index = 0
    for section_idx, phrases in all_sections_phrases:
        for phrase in phrases:
            phrase.original_index = global_index
            global_index += 1

    # Filter by scene range
    all_phrases = []
    for section_idx, phrases in all_sections_phrases:
        if scene_start is not None and section_idx < scene_start:
            continue
        if scene_end is not None and section_idx > scene_end:
            continue
        all_phrases.extend(phrases)

    if len(all_phrases) == 0:
        raise ValueError("No phrases found in script for the specified scene range")

    total_phrases = len(all_phrases)
    if progress_callback:
        progress_callback(0, total_phrases, "Starting audio generation...")

    # Check for multi-speaker mode
    has_personas = hasattr(cfg, "personas") and len(cfg.personas) > 0

    if has_personas:
        # Multi-speaker mode
        synthesizers: dict[str, Any] = {}
        for persona_config in cfg.personas:
            synthesizer = VoicevoxSynthesizer(
                speaker_id=persona_config.synthesizer.speaker_id,
                speed_scale=persona_config.synthesizer.speed_scale,
                dictionary=None,
            )
            synthesizers[persona_config.id] = synthesizer

        # Initialize VOICEVOX
        dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
        model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
        onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

        if not dict_dir_str or not model_path_str:
            raise RuntimeError(
                "VOICEVOX environment variables not set.\n"
                "Please set VOICEVOX_DICT_DIR and VOICEVOX_MODEL_PATH.\n"
                "See docs/VOICEVOX_SETUP.md for instructions."
            )

        for persona_synthesizer in synthesizers.values():
            persona_synthesizer.initialize(
                dict_dir=Path(dict_dir_str),
                model_path=Path(model_path_str),
                onnxruntime_path=Path(onnxruntime_path_str) if onnxruntime_path_str else None,
            )

        # Debug: Log available synthesizers
        logger.debug(f"Available synthesizers: {list(synthesizers.keys())}")

        # Validate persona_ids before synthesis
        validate_persona_ids(all_phrases, synthesizers)

        # Synthesize audio per persona
        audio_paths = []
        generated_count = 0
        existing_count = 0

        for idx, phrase in enumerate(all_phrases):
            audio_file = audio_dir / f"phrase_{phrase.original_index:04d}.wav"
            persona_id = getattr(phrase, "persona_id", None)

            # Check if audio file already exists
            if audio_file.exists() and audio_file.stat().st_size > 0:
                existing_count += 1
                audio_paths.append(audio_file)
                # Read duration from existing file
                try:
                    with wave.open(str(audio_file), "rb") as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration = frames / float(rate)
                    phrase.duration = duration
                except Exception:
                    pass
                else:
                    if progress_callback:
                        progress_callback(
                            idx + 1,
                            total_phrases,
                            f"Reusing existing audio ({idx + 1}/{total_phrases})",
                        )
                    continue

            # Get appropriate synthesizer
            if persona_id and persona_id in synthesizers:
                persona_synthesizer = synthesizers[persona_id]
                logger.debug(f"Using synthesizer for persona_id: {persona_id}")
            else:
                fallback_id = next(iter(synthesizers.keys()))
                persona_synthesizer = synthesizers[fallback_id]
                if persona_id:
                    logger.warning(
                        f"persona_id '{persona_id}' not found in synthesizers. "
                        f"Falling back to '{fallback_id}'. "
                        f"Available: {list(synthesizers.keys())}"
                    )
                else:
                    logger.debug(f"No persona_id specified, using fallback: {fallback_id}")

            # Synthesize single phrase
            phrase_paths, phrase_metadata = persona_synthesizer.synthesize_phrases(
                [phrase], audio_dir
            )
            audio_paths.extend(phrase_paths)
            generated_count += 1

            if progress_callback:
                progress_callback(
                    idx + 1,
                    total_phrases,
                    f"Generating audio ({generated_count} new, {existing_count} reused)",
                )

    else:
        # Single-speaker mode
        synthesizer = create_synthesizer_from_config(cfg)

        # Initialize VOICEVOX
        dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
        model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
        onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

        if not dict_dir_str or not model_path_str:
            raise RuntimeError(
                "VOICEVOX environment variables not set.\n"
                "Please set VOICEVOX_DICT_DIR and VOICEVOX_MODEL_PATH.\n"
                "See docs/VOICEVOX_SETUP.md for instructions."
            )

        synthesizer.initialize(
            dict_dir=Path(dict_dir_str),
            model_path=Path(model_path_str),
            onnxruntime_path=Path(onnxruntime_path_str) if onnxruntime_path_str else None,
        )

        # Count existing audio files
        existing_count = sum(
            1
            for phrase in all_phrases
            if (audio_dir / f"phrase_{phrase.original_index:04d}.wav").exists()
            and (audio_dir / f"phrase_{phrase.original_index:04d}.wav").stat().st_size > 0
        )

        if progress_callback:
            progress_callback(
                0,
                total_phrases,
                f"Generating audio (found {existing_count} existing files)...",
            )

        audio_paths, metadata_list = synthesizer.synthesize_phrases(all_phrases, audio_dir)

        generated_count = len(audio_paths) - existing_count
        if progress_callback:
            progress_callback(
                total_phrases,
                total_phrases,
                f"Audio generation complete ({generated_count} new, {existing_count} reused)",
            )

    # Calculate timings
    calculate_phrase_timings(
        all_phrases,
        initial_pause=cfg.narration.initial_pause,
        speaker_pause=cfg.narration.speaker_pause,
        slide_pause=cfg.narration.slide_pause,
    )

    if progress_callback:
        progress_callback(total_phrases, total_phrases, "Audio generation complete")

    return all_phrases
