"""CLI for movie generator.

Command-line interface for generating YouTube videos from blog URLs.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .audio.core import validate_persona_ids
from .audio.voicevox import create_synthesizer_from_config
from .config import (
    Config,
    load_config,
    print_default_config,
    validate_config,
    write_config_to_file,
)
from .constants import ProjectPaths
from .content.fetcher import fetch_url_sync
from .content.parser import parse_html
from .project import Project
from .script.generator import generate_script, validate_script
from .script.phrases import Phrase, calculate_phrase_timings
from .slides.generator import generate_slides_for_sections
from .utils.filesystem import is_valid_file  # type: ignore[import]
from .utils.scene_range import parse_scene_range
from .video.remotion_renderer import render_video_with_remotion

console = Console()
logger = logging.getLogger(__name__)


# ============================================================================
# Common CLI options decorator
# ============================================================================


def common_options(func: Any) -> Any:
    """Decorator to add common options to commands."""
    func = click.option(
        "--force",
        "-f",
        is_flag=True,
        help="Force overwrite existing files without confirmation",
    )(func)
    func = click.option(
        "--quiet",
        "-q",
        is_flag=True,
        help="Suppress progress output, only show final result",
    )(func)
    func = click.option(
        "--verbose",
        "-v",
        is_flag=True,
        help="Show detailed debug information",
    )(func)
    func = click.option(
        "--dry-run",
        is_flag=True,
        help="Show what would be done without actually executing",
    )(func)
    return func


def _fetch_and_generate_script(
    url: str,
    cfg: Config,
    api_key: str | None,
    mcp_config: Path | None,
    persona_pool_count: int | None,
    persona_pool_seed: int | None,
    progress: Any,
    console: Console,
) -> Any:
    """Fetch content from URL and generate script.

    Common function used by both `generate` and `script create` commands.

    Args:
        url: Blog URL to fetch.
        cfg: Configuration object.
        api_key: OpenRouter API key.
        mcp_config: Path to MCP configuration file.
        persona_pool_count: Override persona pool count.
        persona_pool_seed: Random seed for persona selection.
        progress: Rich Progress object.
        console: Rich Console object.

    Returns:
        VideoScript object.
    """
    task = progress.add_task("Fetching content...", total=None)

    # Use MCP if config provided, otherwise use standard fetcher
    if mcp_config:
        try:
            from .mcp import fetch_content_with_mcp

            console.print(f"[dim]Using MCP server from: {mcp_config}[/dim]")
            markdown_content = asyncio.run(fetch_content_with_mcp(url, mcp_config))
            from .content.parser import ContentMetadata, ParsedContent

            parsed = ParsedContent(
                content=markdown_content,
                markdown=markdown_content,
                metadata=ContentMetadata(title="", description=""),
            )
            progress.update(task, completed=True)
            console.print(f"✓ Fetched via MCP: {len(markdown_content)} chars")
        except Exception as e:
            console.print(f"[yellow]⚠ MCP fetch failed: {e}[/yellow]")
            console.print("[dim]Falling back to standard fetcher...[/dim]")
            html_content = fetch_url_sync(url)
            parsed = parse_html(html_content, base_url=url)
            progress.update(task, completed=True)
            console.print(f"✓ Fetched: {parsed.metadata.title}")
    else:
        html_content = fetch_url_sync(url)
        parsed = parse_html(html_content, base_url=url)
        progress.update(task, completed=True)
        console.print(f"✓ Fetched: {parsed.metadata.title}")

    # Prepare images metadata
    images_metadata = None
    if parsed.images:
        images_metadata = [
            img.model_dump(
                include={"src", "alt", "title", "aria_describedby"},
                exclude_none=True,
            )
            for img in parsed.images
        ]
        console.print(f"  Found {len(parsed.images)} usable images in content")

    task = progress.add_task("Generating script...", total=None)

    # Prepare personas if defined
    personas_for_script = None
    if cfg.personas:
        personas_for_script = [
            p.model_dump(include={"id", "name", "character"}) for p in cfg.personas
        ]

    # Prepare persona pool config
    pool_config = None
    if cfg.persona_pool:
        pool_config = cfg.persona_pool.model_dump()
        # Apply CLI overrides if provided
        if persona_pool_count is not None:
            pool_config["count"] = persona_pool_count
        if persona_pool_seed is not None:
            pool_config["seed"] = persona_pool_seed

    script = asyncio.run(
        generate_script(
            content=parsed.markdown,
            title=parsed.metadata.title,
            description=parsed.metadata.description,
            character=cfg.narration.character,
            style=cfg.narration.style,
            api_key=api_key,
            model=cfg.content.llm.model,
            images=images_metadata,
            personas=personas_for_script,
            pool_config=pool_config,
        )
    )
    progress.update(task, completed=True)
    console.print(f"✓ Generated script: {script.title}")
    console.print(f"  Sections: {len(script.sections)}")

    return script


@click.group()
def cli() -> None:
    """Movie Generator - Generate YouTube videos from blog URLs."""
    pass


@cli.command()
@click.argument("url_or_script", required=False)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory",
)
@click.option("--api-key", envvar="OPENROUTER_API_KEY", help="OpenRouter API key")
@click.option(
    "--scenes",
    type=str,
    help="Scene range to render (e.g., '1-3' for scenes 1-3, '2' for scene 2 only)",
)
@click.option(
    "--mcp-config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to MCP configuration file (enables web scraping via MCP servers)",
)
@click.option(
    "--progress",
    "show_progress",
    is_flag=True,
    default=False,
    help="Show real-time rendering progress (default: hide)",
)
@click.option(
    "--persona-pool-count",
    type=int,
    help="Override persona pool count (number of personas to randomly select)",
)
@click.option(
    "--persona-pool-seed",
    type=int,
    help="Random seed for reproducible persona selection (testing only)",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Enable strict persona validation (fail if persona_id mismatch)",
)
def generate(
    url_or_script: str | None,
    config: Path | None,
    output: Path | None,
    api_key: str | None,
    scenes: str | None,
    mcp_config: Path | None,
    show_progress: bool,
    persona_pool_count: int | None,
    persona_pool_seed: int | None,
    strict: bool,
) -> None:
    """Generate video from URL or existing script.yaml.

    Args:
        url_or_script: Blog URL to convert OR path to existing script.yaml.
        config: Path to config file.
        output: Output directory.
        api_key: OpenRouter API key.
        scenes: Scene range to render (e.g., "1-3" or "2").
        mcp_config: Path to MCP configuration file for enhanced web scraping.
        show_progress: Show real-time rendering progress.
        persona_pool_count: Override persona pool count from config.
        persona_pool_seed: Random seed for reproducible persona selection.
        strict: Enable strict persona validation (fail if persona_id mismatch).
    """
    # Load configuration
    cfg = load_config(config) if config else Config()

    # Determine if input is a script file or URL
    script_path_input = None
    url = None

    if url_or_script:
        potential_script = Path(url_or_script)
        if potential_script.exists() and potential_script.suffix in [".yaml", ".yml"]:
            script_path_input = potential_script
            # Extract output directory from script path if not specified
            if not output:
                output_dir = potential_script.parent
            else:
                output_dir = Path(output)
        else:
            url = url_or_script
            output_dir = Path(output) if output else Path(cfg.project.output_dir)
    else:
        output_dir = Path(output) if output else Path(cfg.project.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_path_input if script_path_input else (output_dir / "script.yaml")

    # Extract language ID from script filename (e.g., "script_ja.yaml" -> "ja")
    language_id = "ja"  # Default language
    if script_path.stem.startswith("script_"):
        # Extract language code from filename like "script_ja" or "script_en"
        potential_lang = script_path.stem.replace("script_", "")
        if potential_lang:  # Ensure we got a language code
            language_id = potential_lang

    console.print(f"[bold]Output directory:[/bold] {output_dir}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Fetch content (only if URL provided and script doesn't exist)
        if script_path.exists():
            console.print(f"[yellow]⊙ Script already exists, loading: {script_path}[/yellow]")
            with open(script_path, encoding="utf-8") as f:
                script_dict = yaml.safe_load(f)
            from .script.generator import (
                Narration,
                ScriptSection,
                VideoScript,
            )

            # Parse sections with unified narrations format
            sections = []
            for section in script_dict["sections"]:
                narrations: list[Narration] = []

                if "narrations" in section and section["narrations"]:
                    # New unified format
                    for n in section["narrations"]:
                        if isinstance(n, str):
                            # Legacy string format - use text as reading
                            narrations.append(Narration(text=n, reading=n))
                        else:
                            # Object format - use reading field or fallback to text
                            reading = n.get("reading", n["text"])
                            narrations.append(
                                Narration(
                                    text=n["text"], reading=reading, persona_id=n.get("persona_id")
                                )
                            )
                elif "dialogues" in section and section["dialogues"]:
                    # Legacy dialogue format
                    for d in section["dialogues"]:
                        reading = d.get("reading", d["narration"])
                        narrations.append(
                            Narration(
                                text=d["narration"], reading=reading, persona_id=d["persona_id"]
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

            script = VideoScript(
                title=script_dict["title"],
                description=script_dict["description"],
                sections=sections,
            )
        else:
            # Need URL to generate new script
            if not url:
                console.print("[red]Error: No script.yaml found and no URL provided[/red]")
                console.print("[yellow]Usage:[/yellow]")
                console.print("  movie-generator generate <URL>              # Generate from URL")
                console.print(
                    "  movie-generator generate <script.yaml>      # Generate from existing script"
                )
                raise click.Abort()

            console.print(f"[bold]Generating video from URL:[/bold] {url}")

            # Fetch content and generate script using common function
            script = _fetch_and_generate_script(
                url=url,
                cfg=cfg,
                api_key=api_key,
                mcp_config=mcp_config,
                persona_pool_count=persona_pool_count,
                persona_pool_seed=persona_pool_seed,
                progress=progress,
                console=console,
            )

            # Save script to YAML using Pydantic's model_dump()
            # This ensures all fields are included automatically
            script_dict = script.model_dump(exclude_none=True)
            with open(script_path, "w", encoding="utf-8") as f:
                yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)
            console.print(f"✓ Script saved: {script_path}")

        # Step 3: Parse scene range if specified
        scene_start: int | None = None
        scene_end: int | None = None
        if scenes:
            scene_start, scene_end = parse_scene_range(scenes)
            # Display scene range info
            if scene_start is not None and scene_end is not None:
                console.print(f"[cyan]Filtering to scenes {scene_start + 1}-{scene_end + 1}[/cyan]")
            elif scene_start is not None:
                console.print(f"[cyan]Filtering to scenes {scene_start + 1} onwards[/cyan]")
            elif scene_end is not None:
                console.print(f"[cyan]Filtering to scenes 1-{scene_end + 1}[/cyan]")

        # Step 4: Convert narrations to phrases (pre-split by LLM)
        task = progress.add_task("Converting narrations to phrases...", total=None)

        # First pass: generate all phrases to determine original_index
        all_sections_phrases = []
        for section_idx, section in enumerate(script.sections):
            section_phrases = []
            for narration in section.narrations:
                # Each narration is already split by LLM (~40 chars)
                phrase = Phrase(text=narration.text, reading=narration.reading)
                phrase.section_index = section_idx
                if narration.persona_id:
                    phrase.persona_id = narration.persona_id
                    # Look up persona name from config
                    if cfg.personas:
                        for p in cfg.personas:
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
            if scene_start is not None and section_idx < scene_start:
                continue
            if scene_end is not None and section_idx > scene_end:
                continue
            all_phrases.extend(phrases)

        progress.update(task, completed=True)
        console.print(f"✓ Converted {len(all_phrases)} phrases")

        # Validate that we have phrases to process
        if len(all_phrases) == 0:
            total_sections = len(script.sections)
            if scenes:
                raise click.ClickException(
                    f"No phrases found for scene range '{scenes}'. "
                    f"Script has {total_sections} sections (use --scenes 1-{total_sections})."
                )
            else:
                raise click.ClickException(
                    "No phrases found in script. Please check that sections have narrations."
                )

        # Step 4: Generate audio
        task = progress.add_task("Generating audio...", total=None)

        # Check if multi-speaker mode is enabled
        has_personas = hasattr(cfg, "personas") and len(cfg.personas) > 0
        if has_personas:
            # Multi-speaker mode: create synthesizer per persona
            from .audio.voicevox import VoicevoxSynthesizer

            synthesizers: dict[str, Any] = {}
            for persona_config in cfg.personas:
                synthesizer = VoicevoxSynthesizer(
                    speaker_id=persona_config.synthesizer.speaker_id,
                    speed_scale=persona_config.synthesizer.speed_scale,
                    dictionary=None,  # Will be set below
                )
                synthesizers[persona_config.id] = synthesizer

            # Initialize VOICEVOX for all synthesizers
            import os

            dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
            model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
            onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

            if not dict_dir_str or not model_path_str:
                raise click.ClickException(
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

            # Validate persona_ids before synthesis (strict mode for strict persona enforcement)
            validate_persona_ids(all_phrases, synthesizers, strict=strict)

            # Synthesize audio per persona
            audio_dir = output_dir / "audio"
            audio_paths = []
            metadata_list: list[Any] = []
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
                        # If file is corrupt, will be regenerated below
                        pass
                    else:
                        metadata_list.append(None)  # Placeholder for existing files
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
                metadata_list.extend(phrase_metadata)

            calculate_phrase_timings(
                all_phrases,
                initial_pause=cfg.narration.initial_pause,
                speaker_pause=cfg.narration.speaker_pause,
                slide_pause=cfg.narration.slide_pause,
            )
            progress.update(task, completed=True)
            new_audio_count = len(audio_paths) - existing_audio_count
            if existing_audio_count > 0:
                console.print(
                    f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused "
                    f"({len(synthesizers)} personas)"
                )
            else:
                console.print(
                    f"✓ Generated {len(audio_paths)} audio files ({len(synthesizers)} personas)"
                )

        else:
            # Single-speaker mode (backward compatible)
            synthesizer = create_synthesizer_from_config(cfg)

            # Initialize VOICEVOX
            import os

            dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
            model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
            onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

            if not dict_dir_str or not model_path_str:
                raise click.ClickException(
                    "VOICEVOX environment variables not set.\n"
                    "Please set VOICEVOX_DICT_DIR and VOICEVOX_MODEL_PATH.\n"
                    "See docs/VOICEVOX_SETUP.md for instructions."
                )

            synthesizer.initialize(
                dict_dir=Path(dict_dir_str),
                model_path=Path(model_path_str),
                onnxruntime_path=Path(onnxruntime_path_str) if onnxruntime_path_str else None,
            )

            audio_dir = output_dir / "audio"
            # Count existing audio files before generation (use original_index)
            existing_audio_count = sum(
                1
                for phrase in all_phrases
                if (
                    audio_dir
                    / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index)
                ).exists()
                and (
                    audio_dir
                    / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index)
                )
                .stat()
                .st_size
                > 0
            )
            audio_paths, metadata_list = synthesizer.synthesize_phrases(all_phrases, audio_dir)
            calculate_phrase_timings(
                all_phrases,
                initial_pause=cfg.narration.initial_pause,
                speaker_pause=cfg.narration.speaker_pause,
                slide_pause=cfg.narration.slide_pause,
            )
            progress.update(task, completed=True)
            new_audio_count = len(audio_paths) - existing_audio_count
            if existing_audio_count > 0:
                console.print(
                    f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused"
                )
            else:
                console.print(f"✓ Generated {len(audio_paths)} audio files")

        # Step 5: Generate slides
        if api_key:
            task = progress.add_task("Generating slides...", total=None)
            # Filter slide prompts based on scene range and track original indices
            slide_prompts = []
            slide_indices = []  # Track original section indices for correct file naming
            for section_idx, section in enumerate(script.sections):
                # Skip sections outside scene range
                if scene_start is not None and section_idx < scene_start:
                    continue
                if scene_end is not None and section_idx > scene_end:
                    continue
                slide_prompts.append(
                    (section.title, section.slide_prompt or section.title, section.source_image_url)
                )
                slide_indices.append(section_idx)
            slide_dir = output_dir / "slides"
            # Count existing slides before generation (use original indices)
            # Check in language subdirectory (ja by default) or root
            lang_slide_dir = slide_dir / "ja"
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

            try:
                slide_paths = asyncio.run(
                    generate_slides_for_sections(
                        sections=slide_prompts,
                        output_dir=slide_dir,
                        api_key=api_key,
                        model=cfg.slides.llm.model,
                        base_url=cfg.slides.llm.base_url,
                        max_concurrent=2,  # Conservative to avoid rate limits
                        section_indices=slide_indices,
                    )
                )
                progress.update(task, completed=True)

                # Count successful slides
                successful_count = sum(1 for p in slide_paths if is_valid_file(p))
                failed_count = len(slide_paths) - successful_count
                new_slide_count = successful_count - existing_slide_count

                if existing_slide_count > 0:
                    console.print(
                        f"✓ Slides: {new_slide_count} generated, {existing_slide_count} reused"
                    )
                else:
                    console.print(f"✓ Generated {successful_count} slides")

                if failed_count > 0:
                    console.print(
                        f"[yellow]⚠ Warning: {failed_count} slides failed to generate[/yellow]"
                    )
                    console.print(
                        f"[dim]  Run 'find {slide_dir} -size 0 -delete' "
                        "to remove failed slides and retry[/dim]"
                    )
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]✗ Error generating slides: {e}[/red]")
                slide_paths = []
        else:
            console.print("[yellow]⚠ Skipping slides (no API key provided)[/yellow]")
            slide_paths = []

        # Step 6: Prepare transition, background, and BGM config for Remotion
        transition_config = cfg.video.transition.model_dump()

        # Prepare background config
        background_config = None
        if cfg.video.background:
            background_config = cfg.video.background.model_dump()

        # Prepare BGM config
        bgm_config = None
        if cfg.video.bgm:
            bgm_config = cfg.video.bgm.model_dump()

        # Prepare section-level background overrides
        section_backgrounds: dict[int, dict[str, Any]] = {}
        for i, section in enumerate(script.sections):
            if section.background:
                section_backgrounds[i] = section.background

        # Step 7: Setup Remotion project and render video
        # Generate output filename based on scene range and language
        if scenes:
            # Convert None values to actual scene numbers for filename
            start_num = 1 if scene_start is None else scene_start + 1
            end_num = len(script.sections) if scene_end is None else scene_end + 1

            if start_num == end_num:
                # Single scene with language: "output_ja_2.mp4"
                video_filename = f"output_{language_id}_{start_num}.mp4"
            else:
                # Range with language: "output_ja_1-3.mp4"
                video_filename = f"output_{language_id}_{start_num}-{end_num}.mp4"
            video_path = output_dir / video_filename
        else:
            # Full video with language: "output_ja.mp4"
            video_path = output_dir / f"output_{language_id}.mp4"
        # Create/load project
        project_name = output_dir.name
        project = Project(project_name, output_dir.parent)

        # Setup Remotion project (creates or updates templates)
        remotion_dir = output_dir / "remotion"
        task = progress.add_task("Setting up Remotion project...", total=None)
        # Temporarily override project_dir for setup_remotion_project
        original_project_dir = project.project_dir
        project.project_dir = output_dir
        project.audio_dir = output_dir / "audio"
        project.slides_dir = output_dir / "slides"
        project.characters_dir = output_dir / "assets" / "characters"

        # Copy character assets from project root to output
        project.copy_character_assets()

        project.setup_remotion_project()
        project.project_dir = original_project_dir
        progress.update(task, completed=True)

        # Render video with Remotion
        task = progress.add_task("Rendering video with Remotion...", total=None)
        # Prepare personas for Remotion if defined
        personas_for_render = None
        if cfg.personas:
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
            ]

        render_video_with_remotion(
            phrases=all_phrases,
            audio_paths=audio_paths,
            slide_paths=slide_paths,
            output_path=video_path,
            remotion_root=remotion_dir,
            project_name=project_name,
            show_progress=show_progress,
            transition=transition_config,
            personas=personas_for_render,
            background=background_config,
            bgm=bgm_config,
            section_backgrounds=section_backgrounds,
            crf=cfg.style.crf,
            fps=cfg.style.fps,
            resolution=cfg.style.resolution,
            render_concurrency=cfg.video.render_concurrency,
            render_timeout_seconds=cfg.video.render_timeout_seconds,
        )
        progress.update(task, completed=True)
        console.print(f"✓ Video ready: {video_path}")

    console.print("\n[bold green]✓ Video generation complete![/bold green]")


@cli.group()
def script() -> None:
    """Script generation commands."""
    pass


@script.command()
@click.argument("url", required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for script.yaml (default: current directory)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option("--api-key", envvar="OPENROUTER_API_KEY", help="OpenRouter API key")
@click.option(
    "--mcp-config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to MCP configuration file",
)
@click.option("--character", help="Character personality for narration")
@click.option("--style", help="Narration style")
@click.option("--model", help="LLM model to use for script generation")
@click.option(
    "--persona-pool-count",
    type=int,
    help="Override persona pool count (number of personas to randomly select)",
)
@click.option(
    "--persona-pool-seed",
    type=int,
    help="Random seed for reproducible persona selection (testing only)",
)
@common_options
def create(
    url: str,
    output: Path | None,
    config: Path | None,
    api_key: str | None,
    mcp_config: Path | None,
    character: str | None,
    style: str | None,
    model: str | None,
    persona_pool_count: int | None,
    persona_pool_seed: int | None,
    force: bool,
    quiet: bool,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Generate script from URL.

    Fetches content from the URL, generates narration script using LLM,
    and saves it to script.yaml.

    Example:
        movie-generator script create https://example.com/blog
        movie-generator script create https://example.com --output ./my-project
    """
    # Validate mutually exclusive options
    if quiet and verbose:
        console.print("[red]Error: --quiet and --verbose are mutually exclusive[/red]")
        raise click.Abort()

    # Configure console output based on flags
    if quiet:
        console.quiet = True  # type: ignore

    # Load configuration
    cfg = load_config(config) if config else Config()

    # Override config with CLI options
    if character:
        cfg.narration.character = character
    if style:
        cfg.narration.style = style
    if model:
        cfg.content.llm.model = model

    output_dir = Path(output) if output else Path.cwd()
    script_path = output_dir / "script.yaml"

    # Check for existing script file
    if script_path.exists() and not force:
        console.print(f"[yellow]Script already exists: {script_path}[/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise click.Abort()

    if dry_run:
        console.print("[cyan][DRY-RUN] Would fetch content from:[/cyan] " + url)
        console.print(f"[cyan][DRY-RUN] Would save script to:[/cyan] {script_path}")
        console.print(f"[cyan][DRY-RUN] Model:[/cyan] {cfg.content.llm.model}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    if not quiet:
        console.print(f"[bold]Generating script from URL:[/bold] {url}")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Fetch content and generate script using common function
        script = _fetch_and_generate_script(
            url=url,
            cfg=cfg,
            api_key=api_key,
            mcp_config=mcp_config,
            persona_pool_count=persona_pool_count,
            persona_pool_seed=persona_pool_seed,
            progress=progress,
            console=console,
        )

        # Save script
        script_dict = script.model_dump(exclude_none=True)
        with open(script_path, "w", encoding="utf-8") as f:
            yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)

        if verbose:
            import os

            file_size = os.path.getsize(script_path)
            console.print(f"✓ Script saved: {script_path} ({file_size} bytes)")
            console.print(f"  Title: {script.title}")
            console.print(f"  Sections: {len(script.sections)}")
            console.print(f"  Total narrations: {sum(len(s.narrations) for s in script.sections)}")
        elif not quiet:
            console.print(f"✓ Script saved: {script_path}")

    if quiet:
        console.print(str(script_path))
    elif not verbose:
        console.print("\n[bold green]✓ Script generation complete![/bold green]")


@script.command("validate")
@click.argument("path", type=click.Path(path_type=Path), required=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file for persona_id validation (optional)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Only show errors, suppress success message",
)
def validate_script_cmd(path: Path, config: Path | None, quiet: bool) -> None:
    """Validate script file.

    Checks YAML syntax, required fields, and narration format.
    Optionally validates persona_id references against config.

    Examples:
        movie-generator script validate script.yaml
        movie-generator script validate script.yaml --config config.yaml
        movie-generator script validate script.yaml -c config.yaml --quiet
    """
    # Load config personas if provided
    config_personas = None
    if config:
        try:
            cfg = load_config(config)
            if cfg.personas:
                config_personas = [p.model_dump(include={"id", "name"}) for p in cfg.personas]
        except Exception as e:
            console.print(f"[yellow]⚠ Warning: Failed to load config file: {e}[/yellow]")

    # Validate script
    result = validate_script(path, config_personas)

    # Display errors
    if result.errors:
        console.print("[red]✗ Script validation failed:[/red]")
        for error in result.errors:
            console.print(f"  [red]• {error}[/red]")

    # Display warnings
    if result.warnings:
        for warning in result.warnings:
            console.print(f"  [yellow]⚠ {warning}[/yellow]")

    # Display success message and statistics
    if result.is_valid:
        if not quiet:
            console.print("[green]✓ Script is valid[/green]")
            console.print(f"  Sections: {result.section_count}")
            console.print(f"  Total narrations: {result.narration_count}")
        raise SystemExit(0)
    else:
        raise SystemExit(1)


@cli.group()
def audio() -> None:
    """Audio generation commands."""
    pass


@audio.command("generate")
@click.argument("script", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option(
    "--scenes",
    type=str,
    help="Scene range to generate audio for (e.g., '1-3')",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Enable strict persona validation (fail if persona_id mismatch)",
)
@click.option("--speaker-id", type=int, help="VOICEVOX speaker ID (override config)")
@click.option(
    "--allow-placeholder",
    is_flag=True,
    help="Allow placeholder audio for missing VOICEVOX",
)
@common_options
def generate_audio_cmd(
    script: Path,
    config: Path | None,
    scenes: str | None,
    speaker_id: int | None,
    allow_placeholder: bool,
    strict: bool,
    force: bool,
    quiet: bool,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Generate audio files from script.yaml.

    Reads the script, splits narrations into phrases, and synthesizes
    audio using VOICEVOX. Saves audio files to audio/ directory.

    --strict flag: Enable strict persona validation (fail if persona_id mismatch).
                   If unknown persona_id is found, raises ValueError.

    Example:
        movie-generator audio generate script.yaml
        movie-generator audio generate script.yaml --scenes 1-3
        movie-generator audio generate script.yaml --strict
    """
    # Validate mutually exclusive options
    if quiet and verbose:
        console.print("[red]Error: --quiet and --verbose are mutually exclusive[/red]")
        raise click.Abort()

    # Load configuration
    cfg = load_config(config) if config else Config()

    # Override speaker ID if provided
    if speaker_id is not None:
        cfg.audio.speaker_id = speaker_id

    output_dir = script.parent
    audio_dir = output_dir / "audio"

    if dry_run:
        console.print(f"[cyan][DRY-RUN] Would generate audio from:[/cyan] {script}")
        console.print(f"[cyan][DRY-RUN] Would save audio to:[/cyan] {audio_dir}")
        if scenes:
            console.print(f"[cyan][DRY-RUN] Scene range:[/cyan] {scenes}")
        return

    audio_dir.mkdir(parents=True, exist_ok=True)

    if not quiet:
        console.print(f"[bold]Generating audio from script:[/bold] {script}")
        console.print(f"[bold]Output directory:[/bold] {audio_dir}")

    # Load script
    from .script.generator import Narration, ScriptSection, VideoScript

    with open(script, encoding="utf-8") as f:
        script_dict = yaml.safe_load(f)

    # Parse sections (reuse logic from generate command)
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

    # Parse scene range if specified
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes:
        scene_start, scene_end = parse_scene_range(scenes)
        if scene_start is not None and scene_end is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1}-{scene_end + 1}[/cyan]")
        elif scene_start is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1} onwards[/cyan]")
        elif scene_end is not None:
            console.print(f"[cyan]Filtering to scenes 1-{scene_end + 1}[/cyan]")

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

    console.print(f"✓ Converted {len(all_phrases)} phrases")

    if len(all_phrases) == 0:
        raise click.ClickException("No phrases found in script")

    # Generate audio
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating audio...", total=None)

        # Check for multi-speaker mode
        has_personas = hasattr(cfg, "personas") and len(cfg.personas) > 0

        if has_personas:
            # Multi-speaker mode
            from .audio.voicevox import VoicevoxSynthesizer

            synthesizers: dict[str, Any] = {}
            for persona_config in cfg.personas:
                synthesizer = VoicevoxSynthesizer(
                    speaker_id=persona_config.synthesizer.speaker_id,
                    speed_scale=persona_config.synthesizer.speed_scale,
                    dictionary=None,
                )
                synthesizers[persona_config.id] = synthesizer

            # Initialize VOICEVOX
            import os

            dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
            model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
            onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

            if not dict_dir_str or not model_path_str:
                raise click.ClickException(
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

            # Validate persona_ids before synthesis (strict mode for strict persona enforcement)
            validate_persona_ids(all_phrases, synthesizers, strict=strict)

            # Synthesize audio per persona
            audio_paths = []
            existing_audio_count = 0

            for phrase in all_phrases:
                audio_file = audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
                    index=phrase.original_index
                )
                persona_id = getattr(phrase, "persona_id", None)

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
                phrase_paths, phrase_metadata = persona_synthesizer.synthesize_phrases(
                    [phrase], audio_dir
                )
                audio_paths.extend(phrase_paths)

            calculate_phrase_timings(
                all_phrases,
                initial_pause=cfg.narration.initial_pause,
                speaker_pause=cfg.narration.speaker_pause,
                slide_pause=cfg.narration.slide_pause,
            )
            progress.update(task, completed=True)
            new_audio_count = len(audio_paths) - existing_audio_count
            if existing_audio_count > 0:
                console.print(
                    f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused "
                    f"({len(synthesizers)} personas)"
                )
            else:
                console.print(
                    f"✓ Generated {len(audio_paths)} audio files ({len(synthesizers)} personas)"
                )
        else:
            # Single-speaker mode
            synthesizer = create_synthesizer_from_config(cfg)

            # Initialize VOICEVOX
            import os

            dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
            model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
            onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

            if not dict_dir_str or not model_path_str:
                raise click.ClickException(
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
            existing_audio_count = sum(
                1
                for phrase in all_phrases
                if (
                    audio_dir
                    / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index)
                ).exists()
                and (
                    audio_dir
                    / ProjectPaths.PHRASE_FILENAME_FORMAT.format(index=phrase.original_index)
                )
                .stat()
                .st_size
                > 0
            )
            audio_paths, metadata_list = synthesizer.synthesize_phrases(all_phrases, audio_dir)
            calculate_phrase_timings(
                all_phrases,
                initial_pause=cfg.narration.initial_pause,
                speaker_pause=cfg.narration.speaker_pause,
                slide_pause=cfg.narration.slide_pause,
            )
            progress.update(task, completed=True)
            new_audio_count = len(audio_paths) - existing_audio_count
            if existing_audio_count > 0:
                console.print(
                    f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused"
                )
            else:
                console.print(f"✓ Generated {len(audio_paths)} audio files")

    console.print("\n[bold green]✓ Audio generation complete![/bold green]")


@cli.group()
def slides() -> None:
    """Slide generation commands."""
    pass


@slides.command("generate")
@click.argument("script", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option("--api-key", envvar="OPENROUTER_API_KEY", help="OpenRouter API key")
@click.option(
    "--scenes",
    type=str,
    help="Scene range to generate slides for (e.g., '1-3')",
)
@click.option("--model", help="LLM model to use for slide generation")
@click.option("--language", default="ja", help="Language code (e.g., 'ja', 'en')")
@click.option("--max-concurrent", type=int, default=2, help="Max concurrent slide generation")
@common_options
def generate_slides_cmd(
    script: Path,
    config: Path | None,
    api_key: str | None,
    scenes: str | None,
    model: str | None,
    language: str,
    max_concurrent: int,
    force: bool,
    quiet: bool,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Generate slide images from script.yaml.

    Uses LLM to generate slides based on slide_prompt in each section.
    Saves slide images to slides/ directory.

    Example:
        movie-generator slides generate script.yaml
        movie-generator slides generate script.yaml --scenes 1-3
    """
    # Validate mutually exclusive options
    if quiet and verbose:
        console.print("[red]Error: --quiet and --verbose are mutually exclusive[/red]")
        raise click.Abort()

    if not api_key and not dry_run:
        console.print("[red]Error: API key required for slide generation[/red]")
        console.print("Set OPENROUTER_API_KEY environment variable or use --api-key")
        raise click.Abort()

    # Load configuration
    cfg = load_config(config) if config else Config()

    # Override model if provided
    if model:
        cfg.slides.llm.model = model

    output_dir = script.parent
    slide_dir = output_dir / "slides"

    if dry_run:
        console.print(f"[cyan][DRY-RUN] Would generate slides from:[/cyan] {script}")
        console.print(f"[cyan][DRY-RUN] Would save slides to:[/cyan] {slide_dir}")
        console.print(f"[cyan][DRY-RUN] Model:[/cyan] {cfg.slides.llm.model}")
        if scenes:
            console.print(f"[cyan][DRY-RUN] Scene range:[/cyan] {scenes}")
        return

    slide_dir.mkdir(parents=True, exist_ok=True)

    if not quiet:
        console.print(f"[bold]Generating slides from script:[/bold] {script}")
        console.print(f"[bold]Output directory:[/bold] {slide_dir}")

    # Load script
    from .script.generator import Narration, ScriptSection, VideoScript

    with open(script, encoding="utf-8") as f:
        script_dict = yaml.safe_load(f)

    # Parse sections
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

    # Parse scene range if specified
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes:
        scene_start, scene_end = parse_scene_range(scenes)
        if scene_start is not None and scene_end is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1}-{scene_end + 1}[/cyan]")
        elif scene_start is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1} onwards[/cyan]")
        elif scene_end is not None:
            console.print(f"[cyan]Filtering to scenes 1-{scene_end + 1}[/cyan]")

    # Filter slide prompts based on scene range
    slide_prompts = []
    slide_indices = []
    for section_idx, section in enumerate(video_script.sections):
        if scene_start is not None and section_idx < scene_start:
            continue
        if scene_end is not None and section_idx > scene_end:
            continue
        slide_prompts.append(
            (section.title, section.slide_prompt or section.title, section.source_image_url)
        )
        slide_indices.append(section_idx)

    console.print(f"✓ Will generate {len(slide_prompts)} slides")

    # Generate slides
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating slides...", total=None)

        # Check for existing slides
        lang_slide_dir = slide_dir / language
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

        try:
            # api_key is guaranteed to be str here due to earlier check
            assert api_key is not None
            slide_paths = asyncio.run(
                generate_slides_for_sections(
                    sections=slide_prompts,
                    output_dir=slide_dir,
                    api_key=api_key,
                    model=cfg.slides.llm.model,
                    base_url=cfg.slides.llm.base_url,
                    max_concurrent=max_concurrent,
                    section_indices=slide_indices,
                )
            )
            progress.update(task, completed=True)

            # Count successful slides
            successful_count = sum(1 for p in slide_paths if is_valid_file(p))
            failed_count = len(slide_paths) - successful_count
            new_slide_count = successful_count - existing_slide_count

            if existing_slide_count > 0:
                console.print(
                    f"✓ Slides: {new_slide_count} generated, {existing_slide_count} reused"
                )
            else:
                console.print(f"✓ Generated {successful_count} slides")

            if failed_count > 0:
                console.print(
                    f"[yellow]⚠ Warning: {failed_count} slides failed to generate[/yellow]"
                )
                console.print(
                    f"[dim]  Run 'find {slide_dir} -size 0 -delete' "
                    "to remove failed slides and retry[/dim]"
                )
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗ Error generating slides: {e}[/red]")
            raise click.Abort()

    console.print("\n[bold green]✓ Slide generation complete![/bold green]")


@cli.group()
def video() -> None:
    """Video rendering commands."""
    pass


@video.command("render")
@click.argument("script", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option(
    "--scenes",
    type=str,
    help="Scene range to render (e.g., '1-3')",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output video file path",
)
@click.option(
    "--progress",
    "show_progress",
    is_flag=True,
    default=False,
    help="Show real-time rendering progress",
)
@click.option("--transition", help="Transition type (fade, slide, etc.)")
@click.option("--fps", type=int, help="Frames per second (default: 30)")
@common_options
def render_video_cmd(
    script: Path,
    config: Path | None,
    scenes: str | None,
    output: Path | None,
    show_progress: bool,
    transition: str | None,
    fps: int | None,
    force: bool,
    quiet: bool,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Render video from script, audio, and slides.

    Combines audio files and slide images using Remotion to create
    the final video output.

    Example:
        movie-generator video render script.yaml
        movie-generator video render script.yaml --output my-video.mp4
    """
    # Validate mutually exclusive options
    if quiet and verbose:
        console.print("[red]Error: --quiet and --verbose are mutually exclusive[/red]")
        raise click.Abort()

    # Load configuration
    cfg = load_config(config) if config else Config()

    # Override transition if provided
    if transition:
        cfg.video.transition.type = transition
    # Note: fps is not directly configurable in VideoConfig, handled by Remotion defaults

    output_dir = script.parent
    audio_dir = output_dir / "audio"
    slide_dir = output_dir / "slides"

    if dry_run:
        console.print(f"[cyan][DRY-RUN] Would render video from:[/cyan] {script}")
        console.print(f"[cyan][DRY-RUN] Audio source:[/cyan] {audio_dir}")
        console.print(f"[cyan][DRY-RUN] Slides source:[/cyan] {slide_dir}")
        if output:
            console.print(f"[cyan][DRY-RUN] Output:[/cyan] {output}")
        if scenes:
            console.print(f"[cyan][DRY-RUN] Scene range:[/cyan] {scenes}")
        return

    # Check if audio and slides exist
    if not audio_dir.exists():
        console.print(f"[red]Error: Audio directory not found: {audio_dir}[/red]")
        console.print("[yellow]Run 'movie-generator audio generate' first[/yellow]")
        raise click.Abort()

    if not slide_dir.exists() and not quiet:
        console.print(f"[yellow]⚠ Warning: Slides directory not found: {slide_dir}[/yellow]")
        console.print("[dim]Video will be rendered without slides[/dim]")

    if not quiet:
        console.print(f"[bold]Rendering video from script:[/bold] {script}")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")

    # Load script
    from .script.generator import Narration, ScriptSection, VideoScript

    with open(script, encoding="utf-8") as f:
        script_dict = yaml.safe_load(f)

    # Parse sections
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
    if script.stem.startswith("script_"):
        potential_lang = script.stem.replace("script_", "")
        if potential_lang:
            language_id = potential_lang

    # Parse scene range if specified
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes:
        scene_start, scene_end = parse_scene_range(scenes)
        if scene_start is not None and scene_end is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1}-{scene_end + 1}[/cyan]")
        elif scene_start is not None:
            console.print(f"[cyan]Filtering to scenes {scene_start + 1} onwards[/cyan]")
        elif scene_end is not None:
            console.print(f"[cyan]Filtering to scenes 1-{scene_end + 1}[/cyan]")

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

    console.print(f"✓ Will render {len(all_phrases)} phrases")

    # Load audio files and calculate timings
    audio_paths = []
    for phrase in all_phrases:
        audio_file = audio_dir / ProjectPaths.PHRASE_FILENAME_FORMAT.format(
            index=phrase.original_index
        )
        if not audio_file.exists():
            console.print(f"[red]Error: Audio file not found: {audio_file}[/red]")
            console.print("[yellow]Run 'movie-generator audio generate' first[/yellow]")
            raise click.Abort()
        audio_paths.append(audio_file)

        # Read duration
        try:
            import wave

            with wave.open(str(audio_file), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
            phrase.duration = duration
        except Exception as e:
            console.print(f"[red]Error reading audio file {audio_file}: {e}[/red]")
            raise click.Abort()

    calculate_phrase_timings(
        all_phrases,
        initial_pause=cfg.narration.initial_pause,
        speaker_pause=cfg.narration.speaker_pause,
        slide_pause=cfg.narration.slide_pause,
    )

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
            console.print(f"[yellow]⚠ Warning: Slide not found for section {section_idx}[/yellow]")
            slide_paths.append(None)  # type: ignore

    # Determine output path
    if output:
        video_path = Path(output)
    else:
        if scenes:
            start_num = 1 if scene_start is None else scene_start + 1
            end_num = len(video_script.sections) if scene_end is None else scene_end + 1

            if start_num == end_num:
                video_filename = f"output_{language_id}_{start_num}.mp4"
            else:
                video_filename = f"output_{language_id}_{start_num}-{end_num}.mp4"
            video_path = output_dir / video_filename
        else:
            video_path = output_dir / f"output_{language_id}.mp4"

    console.print(f"[bold]Output video:[/bold] {video_path}")

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
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        project_name = output_dir.name
        project = Project(project_name, output_dir.parent)

        remotion_dir = output_dir / "remotion"
        task = progress.add_task("Setting up Remotion project...", total=None)

        # Setup project directories
        original_project_dir = project.project_dir
        project.project_dir = output_dir
        project.audio_dir = output_dir / "audio"
        project.slides_dir = output_dir / "slides"
        project.characters_dir = output_dir / "assets" / "characters"

        # Copy character assets
        project.copy_character_assets()
        project.setup_remotion_project()
        project.project_dir = original_project_dir
        progress.update(task, completed=True)

        # Render video
        task = progress.add_task("Rendering video with Remotion...", total=None)

        # Prepare personas for rendering
        personas_for_render = None
        if cfg.personas:
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
            ]

        render_video_with_remotion(
            phrases=all_phrases,
            audio_paths=audio_paths,
            slide_paths=slide_paths,
            output_path=video_path,
            remotion_root=remotion_dir,
            project_name=project_name,
            show_progress=show_progress,
            transition=transition_config,
            personas=personas_for_render,
            background=background_config,
            bgm=bgm_config,
            section_backgrounds=section_backgrounds,
            crf=cfg.style.crf,
            render_concurrency=cfg.video.render_concurrency,
            render_timeout_seconds=cfg.video.render_timeout_seconds,
            fps=cfg.style.fps,
            resolution=cfg.style.resolution,
        )
        progress.update(task, completed=True)
        console.print(f"✓ Video ready: {video_path}")

    console.print("\n[bold green]✓ Video rendering complete![/bold green]")


@cli.group()
def config() -> None:
    """Configuration management commands."""
    pass


@config.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing file without confirmation",
)
def init(output: Path | None, force: bool) -> None:
    """Generate default configuration file.

    By default, outputs to stdout. Use --output to write to a file.

    Examples:
        movie-generator config init
        movie-generator config init --output config.yaml
        movie-generator config init -o my-config.yaml --force
    """
    if output is None:
        # Output to stdout
        print_default_config()
    else:
        # Output to file
        try:
            # Check if file exists and handle confirmation
            if output.exists() and not force:
                if click.confirm(
                    f"File '{output}' already exists. Overwrite?",
                    default=False,
                ):
                    write_config_to_file(output, overwrite=True)
                    console.print(f"[green]✓ Configuration written to {output}[/green]")
                else:
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return
            else:
                write_config_to_file(output, overwrite=force)
                console.print(f"[green]✓ Configuration written to {output}[/green]")
        except OSError as e:
            console.print(f"[red]Error: Unable to write to {output}[/red]")
            console.print(f"[red]{e}[/red]")
            raise click.Abort()


@config.command("validate")
@click.argument("path", type=click.Path(path_type=Path), required=True)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Only show errors, suppress success message",
)
def validate_config_cmd(path: Path, quiet: bool) -> None:
    """Validate configuration file.

    Checks YAML syntax, schema validity, and referenced file existence.

    Examples:
        movie-generator config validate config.yaml
        movie-generator config validate config.yaml --quiet
    """
    result = validate_config(path)

    # Display errors
    if result.errors:
        console.print("[red]✗ Configuration validation failed:[/red]")
        for error in result.errors:
            console.print(f"  [red]• {error}[/red]")

    # Display warnings
    if result.warnings:
        for warning in result.warnings:
            console.print(f"  [yellow]⚠ {warning}[/yellow]")

    # Display success message
    if result.is_valid:
        if not quiet:
            console.print("[green]✓ Configuration is valid[/green]")
        raise SystemExit(0)
    else:
        raise SystemExit(1)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
