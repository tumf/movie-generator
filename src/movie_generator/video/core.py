"""Core video rendering functionality.

Provides library functions for video rendering that can be called
directly by worker processes or other Python code, without CLI overhead.
"""

import wave
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from ..config import Config, load_config
from ..constants import ProjectPaths
from ..project import Project
from ..script.generator import Narration, ScriptSection, VideoScript
from ..script.phrases import Phrase, calculate_phrase_timings
from .remotion_renderer import render_video_with_remotion
from .renderer import CompositionConfig, RenderConfig


def render_video_for_script(
    script_path: Path,
    output_path: Path | None = None,
    output_dir: Path | None = None,
    config_path: Path | None = None,
    config: Config | None = None,
    scenes: tuple[int | None, int | None] | None = None,
    show_progress: bool = False,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Path:
    """Render video from script, audio, and slides.

    Combines audio files and slide images using Remotion to create
    the final video output.

    Args:
        script_path: Path to script.yaml file.
        output_path: Path to save rendered video. If None, auto-generated based on language.
        output_dir: Output directory (used if output_path is None). If None, uses script.parent.
        config_path: Path to config file (mutually exclusive with config).
        config: Config object (mutually exclusive with config_path).
        scenes: Optional scene range (start_index, end_index), 0-based inclusive.
                Either value can be None to indicate "from beginning" or "to end".
        show_progress: If True, show real-time Remotion rendering progress.
        progress_callback: Optional callback(current, total, message) called during rendering.
                          Note: Currently limited to setup/completion, not frame-by-frame progress.

    Returns:
        Path to rendered video file.

    Raises:
        FileNotFoundError: If script, audio, or required files don't exist.
        RuntimeError: If rendering fails.
        ValueError: If config_path and config are both provided.

    Example:
        >>> from pathlib import Path
        >>> video_path = render_video_for_script(
        ...     script_path=Path("script.yaml"),
        ...     output_path=Path("output.mp4"),
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
    slide_dir = output_dir / "slides"

    # Check if audio directory exists
    if not audio_dir.exists():
        raise FileNotFoundError(
            f"Audio directory not found: {audio_dir}\n"
            "Please generate audio files first using audio generation."
        )

    if progress_callback:
        progress_callback(0, 100, "Loading script...")

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

    # Extract language ID from script filename
    language_id = "ja"
    if script_path.stem.startswith("script_"):
        potential_lang = script_path.stem.replace("script_", "")
        if potential_lang:
            language_id = potential_lang

    # Parse scene range if specified
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes is not None:
        scene_start, scene_end = scenes

    if progress_callback:
        progress_callback(5, 100, "Converting narrations to phrases...")

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
    for section_idx, phrases_list in all_sections_phrases:
        for phrase in phrases_list:
            phrase.original_index = global_index
            global_index += 1

    # Filter by scene range
    all_phrases = []
    for section_idx, phrases_list in all_sections_phrases:
        if scene_start is not None and section_idx < scene_start:
            continue
        if scene_end is not None and section_idx > scene_end:
            continue
        all_phrases.extend(phrases_list)

    if len(all_phrases) == 0:
        raise ValueError("No phrases found in script for the specified scene range")

    if progress_callback:
        progress_callback(10, 100, "Loading audio files and calculating timings...")

    # Load audio files and calculate timings
    audio_paths = []
    for phrase in all_phrases:
        audio_file = audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
            index=phrase.original_index
        )
        if not audio_file.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_file}\n"
                "Please generate audio files first using audio generation."
            )
        audio_paths.append(audio_file)

        # Read duration
        try:
            with wave.open(str(audio_file), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
            phrase.duration = duration
        except Exception as e:
            raise RuntimeError(f"Error reading audio file {audio_file}: {e}") from e

    calculate_phrase_timings(
        all_phrases,
        initial_pause=cfg.narration.initial_pause,
        speaker_pause=cfg.narration.speaker_pause,
        slide_pause=cfg.narration.slide_pause,
    )

    if progress_callback:
        progress_callback(20, 100, "Loading slide images...")

    # Load slide paths
    slide_paths = []
    for section_idx, section in enumerate(video_script.sections):
        if scene_start is not None and section_idx < scene_start:
            continue
        if scene_end is not None and section_idx > scene_end:
            continue

        # Try language-specific directory first, then fall back to root
        lang_slide_file = (
            slide_dir / language_id / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=section_idx)
        )
        root_slide_file = slide_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=section_idx)

        if lang_slide_file.exists():
            slide_paths.append(lang_slide_file)
        elif root_slide_file.exists():
            slide_paths.append(root_slide_file)
        else:
            # No slide for this section - will render without slide
            slide_paths.append(None)  # type: ignore

    # Determine output path
    if output_path is None:
        if scenes:
            start_num = 1 if scene_start is None else scene_start + 1
            end_num = len(video_script.sections) if scene_end is None else scene_end + 1

            if start_num == end_num:
                video_filename = f"output_{language_id}_{start_num}.mp4"
            else:
                video_filename = f"output_{language_id}_{start_num}-{end_num}.mp4"
            output_path = output_dir / video_filename
        else:
            output_path = output_dir / f"output_{language_id}.mp4"

    if progress_callback:
        progress_callback(30, 100, "Setting up Remotion project...")

    # Prepare transition, background, and BGM config
    transition_config = cfg.video.transition.model_dump()

    background_config = None
    if cfg.video.background:
        background_config = cfg.video.background.model_dump()

    bgm_config = None
    if cfg.video.bgm:
        bgm_config = cfg.video.bgm.model_dump()

    # Prepare section-level background overrides
    section_backgrounds: dict[int, dict[str, Any]] = {}
    for i, section in enumerate(video_script.sections):
        if section.background:
            section_backgrounds[i] = section.background

    # Setup Remotion project
    project_name = output_dir.name
    project = Project(project_name, output_dir.parent)

    remotion_dir = output_dir / "remotion"

    # Setup project directories
    original_project_dir = project.project_dir
    project.project_dir = output_dir
    project.audio_dir = output_dir / "audio"
    project.slides_dir = output_dir / "slides"
    project.characters_dir = output_dir / "assets" / "characters"

    # Copy character assets
    # Get project root based on environment (Docker or local)
    source_root = ProjectPaths.get_project_root()
    project.copy_character_assets(source_root=source_root)
    project.setup_remotion_project()
    project.project_dir = original_project_dir

    if progress_callback:
        progress_callback(40, 100, "Rendering video with Remotion...")

    # Prepare personas for rendering
    # CRITICAL: Only include personas that are actually used in the script
    personas_for_render = None
    if cfg.personas:
        # Collect unique persona_ids used in the script
        used_persona_ids = {phrase.persona_id for phrase in all_phrases if phrase.persona_id}

        # Filter personas to only those used in the script
        personas_for_render = [
            p.model_dump(
                include={
                    "id",
                    "name",
                    "subtitle_color",
                    "character_image",
                    "character_position",
                    "mouth_open_image",
                    "eye_close_image",
                    "animation_style",
                },
                exclude_none=True,
            )
            for p in cfg.personas
            if p.id in used_persona_ids
        ]

    # Render video
    composition_config = CompositionConfig(
        phrases=all_phrases,
        audio_paths=audio_paths,
        slide_paths=slide_paths,
        project_name=project_name,
        fps=cfg.style.fps,
        resolution=cfg.style.resolution,
        transition=transition_config,
        personas=personas_for_render,
        background=background_config,
        bgm=bgm_config,
        section_backgrounds=section_backgrounds,
    )

    render_config = RenderConfig(
        output_path=output_path,
        remotion_root=remotion_dir,
        show_progress=show_progress,
        crf=cfg.style.crf,
        render_concurrency=cfg.video.render_concurrency,
        render_timeout_seconds=cfg.video.render_timeout_seconds,
    )

    render_video_with_remotion(
        composition_config=composition_config,
        render_config=render_config,
    )

    if progress_callback:
        progress_callback(100, 100, "Video rendering complete")

    if not output_path.exists():
        raise RuntimeError("Video file was not created")

    return output_path
