"""CLI for movie generator.

Command-line interface for generating YouTube videos from blog URLs.
"""

import asyncio
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .audio.voicevox import create_synthesizer_from_config
from .config import Config, load_config, print_default_config, write_config_to_file
from .content.fetcher import fetch_url_sync
from .content.parser import parse_html
from .project import Project
from .script.generator import generate_script
from .script.phrases import Phrase, calculate_phrase_timings
from .slides.generator import generate_slides_for_sections
from .utils.filesystem import is_valid_file  # type: ignore[import]
from .video.remotion_renderer import render_video_with_remotion

console = Console()


def parse_scene_range(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range argument.

    Args:
        scenes_arg: Scene range string (e.g., "1-3", "6-" for 6 onwards, "-3" for up to 3, or "2").

    Returns:
        Tuple of (start_index, end_index) (0-based, inclusive).
        start_index can be None to indicate "from the beginning".
        end_index can be None to indicate "to the end".

    Raises:
        ValueError: If the format is invalid or range is invalid.
    """
    if "-" in scenes_arg:
        parts = scenes_arg.split("-")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid scene range format: '{scenes_arg}'. Expected format: '1-3', '6-', '-3', or '2'"
            )

        # Handle "-3" format (from beginning to scene 3)
        if parts[0] == "":
            if parts[1] == "":
                raise ValueError(
                    f"Invalid scene range format: '{scenes_arg}'. Cannot use '-' alone."
                )

            try:
                end = int(parts[1])
            except ValueError:
                raise ValueError(f"Invalid end scene number: '{parts[1]}'. Must be an integer.")

            if end < 1:
                raise ValueError(f"Scene number must be >= 1, got: {end}")

            # "-3" format - from beginning to scene 3
            return (None, end - 1)

        # Parse start
        try:
            start = int(parts[0])
        except ValueError:
            raise ValueError(f"Invalid start scene number: '{parts[0]}'. Must be an integer.")

        if start < 1:
            raise ValueError(f"Scene number must be >= 1, got: {start}")

        # Parse end (can be empty for "N-" format)
        if parts[1] == "":
            # "6-" format - from scene 6 to the end
            return (start - 1, None)

        try:
            end = int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid end scene number: '{parts[1]}'. Must be an integer.")

        if end < 1:
            raise ValueError(f"Scene numbers must be >= 1, got: {scenes_arg}")
        if start > end:
            raise ValueError(
                f"Invalid scene range: {scenes_arg}. Start must be <= end. "
                f"Example: '1-3' for scenes 1 through 3."
            )
        # Convert to 0-based indexing
        return (start - 1, end - 1)
    else:
        try:
            scene_num = int(scenes_arg)
        except ValueError:
            raise ValueError(f"Invalid scene number: '{scenes_arg}'. Must be an integer.")

        if scene_num < 1:
            raise ValueError(f"Scene number must be >= 1, got: {scene_num}")
        # Convert to 0-based indexing
        return (scene_num - 1, scene_num - 1)


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
def generate(
    url_or_script: str | None,
    config: Path | None,
    output: Path | None,
    api_key: str | None,
    scenes: str | None,
    mcp_config: Path | None,
    show_progress: bool,
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
            task = progress.add_task("Fetching content...", total=None)

            # Use MCP if config provided, otherwise use standard fetcher
            if mcp_config:
                try:
                    from .mcp import fetch_content_with_mcp

                    console.print(f"[dim]Using MCP server from: {mcp_config}[/dim]")
                    markdown_content = asyncio.run(fetch_content_with_mcp(url, mcp_config))
                    # Create a simple metadata-like structure
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

            # Prepare images metadata for script generation
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

            # Prepare personas if defined (enables multi-speaker mode automatically)
            personas_for_script = None
            if cfg.personas:
                personas_for_script = [
                    p.model_dump(include={"id", "name", "character"}) for p in cfg.personas
                ]

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
                )
            )
            progress.update(task, completed=True)
            console.print(f"✓ Generated script: {script.title}")
            console.print(f"  Sections: {len(script.sections)}")

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

            # Synthesize audio per persona
            audio_dir = output_dir / "audio"
            audio_paths = []
            metadata_list = []
            existing_audio_count = 0

            for phrase in all_phrases:
                audio_file = audio_dir / f"phrase_{phrase.original_index:04d}.wav"
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
                else:
                    # Fallback to first persona if no persona_id specified
                    persona_synthesizer = next(iter(synthesizers.values()))

                # Synthesize single phrase
                phrase_paths, phrase_metadata = persona_synthesizer.synthesize_phrases(
                    [phrase], audio_dir
                )
                audio_paths.extend(phrase_paths)
                metadata_list.extend(phrase_metadata)

            calculate_phrase_timings(all_phrases)
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
                if (audio_dir / f"phrase_{phrase.original_index:04d}.wav").exists()
                and (audio_dir / f"phrase_{phrase.original_index:04d}.wav").stat().st_size > 0
            )
            audio_paths, metadata_list = synthesizer.synthesize_phrases(all_phrases, audio_dir)
            calculate_phrase_timings(all_phrases)
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
                    (lang_slide_dir / f"slide_{idx:04d}.png").exists()
                    and (lang_slide_dir / f"slide_{idx:04d}.png").stat().st_size > 0
                )
                or (
                    (slide_dir / f"slide_{idx:04d}.png").exists()
                    and (slide_dir / f"slide_{idx:04d}.png").stat().st_size > 0
                )
            )

            try:
                slide_paths = asyncio.run(
                    generate_slides_for_sections(
                        sections=slide_prompts,
                        output_dir=slide_dir,
                        api_key=api_key,
                        model=cfg.slides.llm.model,
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
                        f"[dim]  Run 'find {slide_dir} -size 0 -delete' to remove failed slides and retry[/dim]"
                    )
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]✗ Error generating slides: {e}[/red]")
                slide_paths = []
        else:
            console.print("[yellow]⚠ Skipping slides (no API key provided)[/yellow]")
            slide_paths = []

        # Step 6: Prepare transition config for Remotion
        transition_config = cfg.video.transition.model_dump()

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
        # Note: character_position is auto-assigned in remotion_renderer, not from config
        personas_for_render = None
        if cfg.personas:
            personas_for_render = [
                p.model_dump(
                    include={
                        "id",
                        "name",
                        "subtitle_color",
                        "character_image",
                        # character_position is excluded - it's auto-assigned by order
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
        )
        progress.update(task, completed=True)
        console.print(f"✓ Video ready: {video_path}")

    console.print("\n[bold green]✓ Video generation complete![/bold green]")


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


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
