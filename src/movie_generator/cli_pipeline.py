"""Pipeline stages for the generate command.

This module contains the extracted pipeline stages that were previously
embedded in the generate() CLI command. Each stage is a separate function
that can be tested independently.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.progress import Progress

from .audio.core import validate_persona_ids
from .audio.voicevox import VoicevoxSynthesizer, create_synthesizer_from_config
from .config import Config
from .constants import ProjectPaths
from .content.fetcher import fetch_url_sync
from .content.parser import ContentMetadata, ParsedContent, parse_html
from .project import Project
from .script.generator import Narration, ScriptSection, VideoScript, generate_script
from .script.phrases import Phrase, calculate_phrase_timings
from .slides.generator import generate_slides_for_sections
from .utils.filesystem import is_valid_file  # type: ignore[import]
from .video.remotion_renderer import render_video_with_remotion
from .video.renderer import CompositionConfig, RenderConfig

logger = logging.getLogger(__name__)


@dataclass
class PipelineParams:
    """Parameters passed between pipeline stages."""

    # Input parameters (required)
    url_or_script: str | None
    config: Config
    output_dir: Path
    api_key: str | None
    mcp_config: Path | None
    scenes: str | None
    show_progress: bool
    persona_pool_count: int | None
    persona_pool_seed: int | None
    strict: bool
    # Input parameters (optional with defaults)
    output_dir_explicit: bool = False  # True if --output was explicitly specified
    force: bool = False
    quiet: bool = False
    verbose: bool = False
    dry_run: bool = False

    # Working data (populated during pipeline execution)
    script_path: Path | None = None
    script: VideoScript | None = None
    language_id: str = "ja"
    scene_start: int | None = None
    scene_end: int | None = None
    all_phrases: list[Phrase] = field(default_factory=list)
    audio_paths: list[Path] = field(default_factory=list)
    slide_paths: list[Path] = field(default_factory=list)
    video_path: Path | None = None


class PipelineError(Exception):
    """Base exception for pipeline errors with context."""

    def __init__(self, stage: str, message: str, input_info: str | None = None):
        """Initialize pipeline error.

        Args:
            stage: Name of the pipeline stage (e.g., "script_generation", "audio_synthesis").
            message: Error message describing what went wrong.
            input_info: Optional context about the input (e.g., URL or script path).
        """
        self.stage = stage
        self.message = message
        self.input_info = input_info

        full_message = f"[{stage}] {message}"
        if input_info:
            full_message += f" (input: {input_info})"

        super().__init__(full_message)


def _fetch_content_from_url(
    url: str,
    mcp_config: Path | None,
    progress: Progress,
    console: Console,
) -> ParsedContent:
    """Fetch content from URL using MCP or standard fetcher.

    Args:
        url: URL to fetch content from.
        mcp_config: Optional MCP configuration file path.
        progress: Rich Progress instance.
        console: Rich Console instance.

    Returns:
        ParsedContent with markdown and metadata.

    Raises:
        PipelineError: If content fetching fails.
    """
    task = progress.add_task("Fetching content...", total=None)

    try:
        # Use MCP if config provided, otherwise use standard fetcher
        if mcp_config:
            try:
                from .mcp import fetch_content_with_mcp

                console.print(f"[dim]Using MCP server from: {mcp_config}[/dim]")
                markdown_content = asyncio.run(fetch_content_with_mcp(url, mcp_config))

                parsed = ParsedContent(
                    content=markdown_content,
                    markdown=markdown_content,
                    metadata=ContentMetadata(title="", description=""),
                )
                progress.update(task, completed=True)
                console.print(f"✓ Fetched via MCP: {len(markdown_content)} chars")
                return parsed
            except Exception as e:
                console.print(f"[yellow]⚠ MCP fetch failed: {e}[/yellow]")
                console.print("[dim]Falling back to standard fetcher...[/dim]")

        # Standard fetcher
        html_content = fetch_url_sync(url)
        parsed = parse_html(html_content, base_url=url)
        progress.update(task, completed=True)
        console.print(f"✓ Fetched: {parsed.metadata.title}")
        return parsed

    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="content_fetching",
            message=f"Failed to fetch content: {e}",
            input_info=url,
        )


def stage_script_resolution(
    params: PipelineParams,
    progress: Progress,
    console: Console,
) -> VideoScript:
    """Resolve or generate script (Stage 1).

    Either loads existing script.yaml or fetches URL and generates new script.

    Args:
        params: Pipeline parameters.
        progress: Rich Progress instance.
        console: Rich Console instance.

    Returns:
        VideoScript object.

    Raises:
        PipelineError: If script resolution or generation fails.
    """
    # Determine if input is a script file or URL
    script_path_input = None
    url = None

    if params.url_or_script:
        potential_script = Path(params.url_or_script)
        if potential_script.exists() and potential_script.suffix in [".yaml", ".yml"]:
            script_path_input = potential_script
            # Only override output_dir if --output was not explicitly specified
            if not params.output_dir_explicit:
                params.output_dir = potential_script.parent
        else:
            url = params.url_or_script

    params.output_dir.mkdir(parents=True, exist_ok=True)
    params.script_path = (
        script_path_input if script_path_input else (params.output_dir / "script.yaml")
    )

    # Extract language ID from script filename
    if params.script_path.stem.startswith("script_"):
        potential_lang = params.script_path.stem.replace("script_", "")
        if potential_lang:
            params.language_id = potential_lang

    # Load existing script or generate new one
    if params.script_path.exists() and not params.force:
        console.print(f"[yellow]⊙ Script already exists, loading: {params.script_path}[/yellow]")
        if params.dry_run:
            console.print("[dim]  (dry-run: would load existing script)[/dim]")
            # Still need to load for dry-run to show what happens next
        try:
            with open(params.script_path, encoding="utf-8") as f:
                script_dict = yaml.safe_load(f)

            # Parse sections with unified narrations format
            sections = []
            for section in script_dict["sections"]:
                narrations: list[Narration] = []

                if "narrations" in section and section["narrations"]:
                    # New unified format
                    for n in section["narrations"]:
                        if isinstance(n, str):
                            narrations.append(Narration(text=n, reading=n))
                        else:
                            reading = n.get("reading", n["text"])
                            narrations.append(
                                Narration(
                                    text=n["text"],
                                    reading=reading,
                                    persona_id=n.get("persona_id"),
                                )
                            )
                elif "dialogues" in section and section["dialogues"]:
                    # Legacy dialogue format
                    for d in section["dialogues"]:
                        reading = d.get("reading", d["narration"])
                        narrations.append(
                            Narration(
                                text=d["narration"],
                                reading=reading,
                                persona_id=d["persona_id"],
                            )
                        )
                elif "narration" in section:
                    # Legacy single narration format
                    narrations.append(
                        Narration(text=section["narration"], reading=section["narration"])
                    )

                sections.append(
                    ScriptSection(
                        title=section["title"],
                        narrations=narrations,
                        slide_prompt=section.get("slide_prompt"),
                        source_image_url=section.get("source_image_url"),
                        background=section.get("background"),
                    )
                )

            return VideoScript(
                title=script_dict["title"],
                description=script_dict["description"],
                sections=sections,
            )

        except Exception as e:
            raise PipelineError(
                stage="script_loading",
                message=f"Failed to load existing script: {e}",
                input_info=str(params.script_path),
            )
    else:
        # Generate new script if it doesn't exist or --force is specified
        # Force regeneration or no existing script
        if params.force and params.script_path.exists():
            console.print("[yellow]⊙ Script exists but --force specified, will regenerate[/yellow]")

        # Need URL to generate script
        if not url:
            if params.force:
                raise PipelineError(
                    stage="script_resolution",
                    message="--force specified but no URL provided to regenerate script",
                    input_info=None,
                )
            else:
                raise PipelineError(
                    stage="script_resolution",
                    message="No script.yaml found and no URL provided. "
                    "Please provide a URL or path to existing script.yaml",
                    input_info=None,
                )

        console.print(f"[bold]Generating video from URL:[/bold] {url}")
        if params.dry_run:
            console.print("[dim]  (dry-run: would fetch content and generate script)[/dim]")
            # For dry-run, create a minimal script to continue pipeline
            dummy_script = VideoScript(
                title="[Dry-run] Sample Script",
                description="This is a placeholder for dry-run mode",
                sections=[
                    ScriptSection(
                        title="Sample Section",
                        narrations=[Narration(text="Sample narration", reading="Sample narration")],
                        slide_prompt="Sample slide",
                    )
                ],
            )
            return dummy_script

        # Fetch content
        parsed = _fetch_content_from_url(url, params.mcp_config, progress, console)

        # Prepare images metadata (filter to candidates only)
        images_metadata = None
        if parsed.images:
            candidate_images = [img for img in parsed.images if img.is_candidate]
            images_metadata = [
                img.model_dump(
                    include={"src", "alt", "title", "aria_describedby"},
                    exclude_none=True,
                )
                for img in candidate_images
            ]
            console.print(
                f"  Found {len(candidate_images)} candidate images "
                f"({len(parsed.images)} total) in content"
            )

        # Generate script
        task = progress.add_task("Generating script...", total=None)

        try:
            # Prepare personas if defined
            # - For 1 persona: enables persona_id assignment in single-speaker mode
            # - For 2+ personas: enables multi-speaker dialogue mode
            personas_for_script = None
            if params.config.personas and len(params.config.personas) >= 1:
                personas_for_script = [
                    p.model_dump(include={"id", "name", "character"})
                    for p in params.config.personas
                ]

            # Prepare persona pool config
            pool_config = None
            if params.config.persona_pool:
                pool_config = params.config.persona_pool.model_dump()
                # Apply CLI overrides if provided
                if params.persona_pool_count is not None:
                    pool_config["count"] = params.persona_pool_count
                if params.persona_pool_seed is not None:
                    pool_config["seed"] = params.persona_pool_seed

            script = asyncio.run(
                generate_script(
                    content=parsed.markdown,
                    title=parsed.metadata.title,
                    description=parsed.metadata.description,
                    character=params.config.narration.character,
                    style=params.config.narration.style,
                    api_key=params.api_key,
                    model=params.config.content.llm.model,
                    images=images_metadata,
                    personas=personas_for_script,
                    pool_config=pool_config,
                )
            )
            progress.update(task, completed=True)
            console.print(f"✓ Generated script: {script.title}")
            console.print(f"  Sections: {len(script.sections)}")

            # Save script to YAML
            script_dict = script.model_dump(exclude_none=True)
            with open(params.script_path, "w", encoding="utf-8") as f:
                yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)
            console.print(f"✓ Script saved: {params.script_path}")

            return script

        except Exception as e:
            progress.update(task, completed=True)
            raise PipelineError(
                stage="script_generation",
                message=f"Failed to generate script: {e}",
                input_info=url,
            )


def stage_audio_generation(
    params: PipelineParams,
    script: VideoScript,
    progress: Progress,
    console: Console,
) -> tuple[list[Phrase], list[Path]]:
    """Generate audio files from script (Stage 2).

    Args:
        params: Pipeline parameters.
        script: VideoScript to generate audio from.
        progress: Rich Progress instance.
        console: Rich Console instance.

    Returns:
        Tuple of (all_phrases, audio_paths).

    Raises:
        PipelineError: If audio generation fails.
    """
    task = progress.add_task("Converting narrations to phrases...", total=None)

    try:
        # First pass: generate all phrases to determine original_index
        all_sections_phrases = []
        for section_idx, section in enumerate(script.sections):
            section_phrases = []
            for narration in section.narrations:
                phrase = Phrase(text=narration.text, reading=narration.reading)
                phrase.section_index = section_idx
                if narration.persona_id:
                    phrase.persona_id = narration.persona_id
                    # Look up persona name from config
                    if params.config.personas:
                        for p in params.config.personas:
                            if p.id == narration.persona_id:
                                phrase.persona_name = p.name
                                break
                section_phrases.append(phrase)
            all_sections_phrases.append((section_idx, section_phrases))

        # Set original_index for all phrases globally
        global_index = 0
        for section_idx, phrases in all_sections_phrases:
            for phrase in phrases:
                phrase.original_index = global_index
                global_index += 1

        # Second pass: filter by scene range if specified
        all_phrases = []
        for section_idx, phrases in all_sections_phrases:
            # Skip sections outside scene range
            if params.scene_start is not None and section_idx < params.scene_start:
                continue
            if params.scene_end is not None and section_idx > params.scene_end:
                continue
            all_phrases.extend(phrases)

        progress.update(task, completed=True)
        console.print(f"✓ Converted {len(all_phrases)} phrases")

        # Validate that we have phrases to process
        if len(all_phrases) == 0:
            total_sections = len(script.sections)
            if params.scenes:
                raise PipelineError(
                    stage="audio_generation",
                    message=f"No phrases found for scene range '{params.scenes}'. "
                    f"Script has {total_sections} sections (use --scenes 1-{total_sections}).",
                    input_info=params.scenes,
                )
            else:
                raise PipelineError(
                    stage="audio_generation",
                    message="No phrases found in script. "
                    "Please check that sections have narrations.",
                    input_info=str(params.script_path),
                )

    except PipelineError:
        raise
    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="audio_generation",
            message=f"Failed to convert narrations to phrases: {e}",
            input_info=str(params.script_path),
        )

    # Step 2: Generate audio
    task = progress.add_task("Generating audio...", total=None)

    try:
        audio_dir = params.output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        if params.dry_run:
            console.print(f"[dim]  (dry-run: would generate {len(all_phrases)} audio files)[/dim]")
            progress.update(task, completed=True)
            # Return empty paths for dry-run
            return all_phrases, []

        # Check if multi-speaker mode is enabled
        has_personas = hasattr(params.config, "personas") and len(params.config.personas) > 0

        if has_personas:
            # Multi-speaker mode: create synthesizer per persona
            audio_paths = _generate_audio_multi_speaker(
                all_phrases=all_phrases,
                audio_dir=audio_dir,
                config=params.config,
                strict=params.strict,
                progress=progress,
                console=console,
            )
        else:
            # Single-speaker mode (backward compatible)
            audio_paths = _generate_audio_single_speaker(
                all_phrases=all_phrases,
                audio_dir=audio_dir,
                config=params.config,
                progress=progress,
                console=console,
            )

        # Calculate phrase timings
        calculate_phrase_timings(
            all_phrases,
            initial_pause=params.config.narration.initial_pause,
            speaker_pause=params.config.narration.speaker_pause,
            slide_pause=params.config.narration.slide_pause,
        )

        progress.update(task, completed=True)
        return all_phrases, audio_paths

    except PipelineError:
        raise
    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="audio_generation",
            message=f"Failed to synthesize audio: {e}",
            input_info=str(params.script_path),
        )


def _generate_audio_multi_speaker(
    all_phrases: list[Phrase],
    audio_dir: Path,
    config: Config,
    strict: bool,
    progress: Progress,
    console: Console,
) -> list[Path]:
    """Generate audio for multi-speaker mode."""
    import os

    synthesizers: dict[str, Any] = {}
    for persona_config in config.personas:
        synthesizer = VoicevoxSynthesizer(
            speaker_id=persona_config.synthesizer.speaker_id,
            speed_scale=persona_config.synthesizer.speed_scale,
            dictionary=None,
        )
        synthesizers[persona_config.id] = synthesizer

    # Initialize VOICEVOX for all synthesizers
    dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
    model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
    onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

    if not dict_dir_str or not model_path_str:
        raise PipelineError(
            stage="audio_generation",
            message="VOICEVOX environment variables not set. "
            "Please set VOICEVOX_DICT_DIR and VOICEVOX_MODEL_PATH. "
            "See docs/VOICEVOX_SETUP.md for instructions.",
            input_info=None,
        )

    for persona_synthesizer in synthesizers.values():
        persona_synthesizer.initialize(
            dict_dir=Path(dict_dir_str),
            model_path=Path(model_path_str),
            onnxruntime_path=Path(onnxruntime_path_str) if onnxruntime_path_str else None,
        )

    # Validate persona_ids before synthesis
    validate_persona_ids(all_phrases, synthesizers, strict=strict)

    # Synthesize audio per persona
    audio_paths = []
    existing_audio_count = 0

    for phrase in all_phrases:
        audio_file = audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
            index=phrase.original_index
        )
        persona_id = getattr(phrase, "persona_id", None)

        # Count existing audio files and read their duration
        if audio_file.exists() and audio_file.stat().st_size > 0:
            existing_audio_count += 1
            audio_paths.append(audio_file)
            # Read duration from existing file
            try:
                import wave

                with wave.open(str(audio_file), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
                phrase.duration = duration
            except Exception:
                pass
            else:
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
        phrase_paths, _ = persona_synthesizer.synthesize_phrases([phrase], audio_dir)
        audio_paths.extend(phrase_paths)

    new_audio_count = len(audio_paths) - existing_audio_count
    if existing_audio_count > 0:
        console.print(
            f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused "
            f"({len(synthesizers)} personas)"
        )
    else:
        console.print(f"✓ Generated {len(audio_paths)} audio files ({len(synthesizers)} personas)")

    return audio_paths


def _generate_audio_single_speaker(
    all_phrases: list[Phrase],
    audio_dir: Path,
    config: Config,
    progress: Progress,
    console: Console,
) -> list[Path]:
    """Generate audio for single-speaker mode."""
    import os

    synthesizer = create_synthesizer_from_config(config)

    # Initialize VOICEVOX
    dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
    model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
    onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

    if not dict_dir_str or not model_path_str:
        raise PipelineError(
            stage="audio_generation",
            message="VOICEVOX environment variables not set. "
            "Please set VOICEVOX_DICT_DIR and VOICEVOX_MODEL_PATH. "
            "See docs/VOICEVOX_SETUP.md for instructions.",
            input_info=None,
        )

    synthesizer.initialize(
        dict_dir=Path(dict_dir_str),
        model_path=Path(model_path_str),
        onnxruntime_path=Path(onnxruntime_path_str) if onnxruntime_path_str else None,
    )

    # Count existing audio files before generation
    existing_audio_count = sum(
        1
        for phrase in all_phrases
        if (
            audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index)
        ).exists()
        and (audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index))
        .stat()
        .st_size
        > 0
    )

    audio_paths, _ = synthesizer.synthesize_phrases(all_phrases, audio_dir)

    new_audio_count = len(audio_paths) - existing_audio_count
    if existing_audio_count > 0:
        console.print(f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused")
    else:
        console.print(f"✓ Generated {len(audio_paths)} audio files")

    return audio_paths


def stage_slides_generation(
    params: PipelineParams,
    script: VideoScript,
    progress: Progress,
    console: Console,
) -> list[Path]:
    """Generate slide images (Stage 3).

    Args:
        params: Pipeline parameters.
        script: VideoScript with slide prompts.
        progress: Rich Progress instance.
        console: Rich Console instance.

    Returns:
        List of slide paths.

    Raises:
        PipelineError: If slide generation fails critically.
    """
    if not params.api_key:
        console.print("[yellow]⚠ Skipping slides (no API key provided)[/yellow]")
        return []

    task = progress.add_task("Generating slides...", total=None)

    try:
        # Filter slide prompts based on scene range and track original indices
        slide_prompts = []
        slide_indices = []
        for section_idx, section in enumerate(script.sections):
            # Skip sections outside scene range
            if params.scene_start is not None and section_idx < params.scene_start:
                continue
            if params.scene_end is not None and section_idx > params.scene_end:
                continue
            slide_prompts.append(
                (section.title, section.slide_prompt or section.title, section.source_image_url)
            )
            slide_indices.append(section_idx)

        slide_dir = params.output_dir / "slides"
        slide_dir.mkdir(parents=True, exist_ok=True)

        if params.dry_run:
            console.print(f"[dim]  (dry-run: would generate {len(slide_prompts)} slides)[/dim]")
            progress.update(task, completed=True)
            return []

        # Count existing slides
        lang_slide_dir = slide_dir / params.language_id
        existing_slide_count = sum(
            1
            for idx in slide_indices
            if (
                (lang_slide_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=idx)).exists()
                and (lang_slide_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=idx))
                .stat()
                .st_size
                > 0
            )
            or (
                (slide_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=idx)).exists()
                and (slide_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=idx))
                .stat()
                .st_size
                > 0
            )
        )

        slide_paths = asyncio.run(
            generate_slides_for_sections(
                sections=slide_prompts,
                output_dir=slide_dir,
                api_key=params.api_key,
                model=params.config.slides.llm.model,
                base_url=params.config.slides.llm.base_url,
                max_concurrent=2,
                section_indices=slide_indices,
            )
        )
        progress.update(task, completed=True)

        # Count successful slides
        successful_count = sum(1 for p in slide_paths if is_valid_file(p))
        failed_count = len(slide_paths) - successful_count
        new_slide_count = successful_count - existing_slide_count

        if existing_slide_count > 0:
            console.print(f"✓ Slides: {new_slide_count} generated, {existing_slide_count} reused")
        else:
            console.print(f"✓ Generated {successful_count} slides")

        if failed_count > 0:
            console.print(f"[yellow]⚠ Warning: {failed_count} slides failed to generate[/yellow]")
            console.print(
                f"[dim]  Run 'find {slide_dir} -size 0 -delete' "
                "to remove failed slides and retry[/dim]"
            )

        return slide_paths

    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="slides_generation",
            message=f"Failed to generate slides: {e}",
            input_info=str(params.script_path),
        )


def stage_video_rendering(
    params: PipelineParams,
    script: VideoScript,
    all_phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path],
    progress: Progress,
    console: Console,
) -> Path:
    """Render final video with Remotion (Stage 4).

    Args:
        params: Pipeline parameters.
        script: VideoScript.
        all_phrases: List of phrases with timings.
        audio_paths: List of audio file paths.
        slide_paths: List of slide image paths.
        progress: Rich Progress instance.
        console: Rich Console instance.

    Returns:
        Path to rendered video file.

    Raises:
        PipelineError: If video rendering fails.
    """
    # Generate output filename based on scene range and language
    if params.scenes:
        # Convert None values to actual scene numbers for filename
        start_num = 1 if params.scene_start is None else params.scene_start + 1
        end_num = len(script.sections) if params.scene_end is None else params.scene_end + 1

        if start_num == end_num:
            video_filename = f"output_{params.language_id}_{start_num}.mp4"
        else:
            video_filename = f"output_{params.language_id}_{start_num}-{end_num}.mp4"
        video_path = params.output_dir / video_filename
    else:
        video_path = params.output_dir / f"output_{params.language_id}.mp4"

    if params.dry_run:
        console.print(f"[dim]  (dry-run: would render video to {video_path})[/dim]")
        return video_path

    # Create/load project
    project_name = params.output_dir.name
    project = Project(project_name, params.output_dir.parent)

    # Setup Remotion project
    remotion_dir = params.output_dir / "remotion"
    task = progress.add_task("Setting up Remotion project...", total=None)

    try:
        # Temporarily override project_dir for setup_remotion_project
        original_project_dir = project.project_dir
        project.project_dir = params.output_dir
        project.audio_dir = params.output_dir / "audio"
        project.slides_dir = params.output_dir / "slides"
        project.characters_dir = params.output_dir / "assets" / "characters"

        # Copy character assets from project root to output
        project.copy_character_assets()
        project.setup_remotion_project()
        project.project_dir = original_project_dir

        progress.update(task, completed=True)

    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="video_rendering",
            message=f"Failed to setup Remotion project: {e}",
            input_info=str(params.output_dir),
        )

    # Render video
    task = progress.add_task("Rendering video with Remotion...", total=None)

    try:
        # Prepare transition, background, and BGM config
        transition_config = params.config.video.transition.model_dump()

        background_config = None
        if params.config.video.background:
            background_config = params.config.video.background.model_dump()

        bgm_config = None
        if params.config.video.bgm:
            bgm_config = params.config.video.bgm.model_dump()

        # Prepare section-level background overrides
        section_backgrounds: dict[int, dict[str, Any]] = {}
        for i, section in enumerate(script.sections):
            if section.background:
                section_backgrounds[i] = section.background

        # Prepare personas for Remotion if defined
        personas_for_render = None
        if params.config.personas:
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
                for p in params.config.personas
            ]

        composition_config = CompositionConfig(
            phrases=all_phrases,
            audio_paths=audio_paths,
            slide_paths=slide_paths,
            project_name=project_name,
            fps=params.config.style.fps,
            resolution=params.config.style.resolution,
            transition=transition_config,
            personas=personas_for_render,
            background=background_config,
            bgm=bgm_config,
            section_backgrounds=section_backgrounds,
        )

        render_config = RenderConfig(
            output_path=video_path,
            remotion_root=remotion_dir,
            show_progress=params.show_progress,
            crf=params.config.style.crf,
            render_concurrency=params.config.video.render_concurrency,
            render_timeout_seconds=params.config.video.render_timeout_seconds,
        )

        render_video_with_remotion(
            composition_config=composition_config,
            render_config=render_config,
        )

        progress.update(task, completed=True)
        console.print(f"✓ Video ready: {video_path}")
        return video_path

    except Exception as e:
        progress.update(task, completed=True)
        raise PipelineError(
            stage="video_rendering",
            message=f"Failed to render video: {e}",
            input_info=str(video_path),
        )
