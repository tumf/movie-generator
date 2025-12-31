"""CLI for movie generator.

Command-line interface for generating YouTube videos from blog URLs.
"""

import asyncio
from pathlib import Path

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
from .script.phrases import calculate_phrase_timings, split_into_phrases
from .slides.generator import generate_slides_for_sections
from .utils.filesystem import is_valid_file  # type: ignore[import]
from .utils.text import clean_katakana_reading  # type: ignore[import]
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
@click.option(
    "--allow-placeholder",
    is_flag=True,
    default=False,
    help="Allow running without VOICEVOX (generates placeholder audio for testing)",
)
def generate(
    url_or_script: str | None,
    config: Path | None,
    output: Path | None,
    api_key: str | None,
    scenes: str | None,
    mcp_config: Path | None,
    show_progress: bool,
    allow_placeholder: bool,
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
        allow_placeholder: Allow running without VOICEVOX (testing only).
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
            from .script.generator import PronunciationEntry, ScriptSection, VideoScript

            # Load pronunciations if available
            pronunciations = None
            if "pronunciations" in script_dict and script_dict["pronunciations"]:
                pronunciations = [
                    PronunciationEntry(
                        word=entry["word"],
                        # Remove spaces from reading (VOICEVOX requires katakana-only)
                        reading=clean_katakana_reading(entry["reading"]),
                        word_type=entry.get("word_type", "COMMON_NOUN"),
                        accent=entry.get("accent", 0),
                    )
                    for entry in script_dict["pronunciations"]
                ]

            script = VideoScript(
                title=script_dict["title"],
                description=script_dict["description"],
                sections=[
                    ScriptSection(
                        title=section["title"],
                        narration=section["narration"],
                        slide_prompt=section.get("slide_prompt"),
                        source_image_url=section.get("source_image_url"),
                    )
                    for section in script_dict["sections"]
                ],
                pronunciations=pronunciations,
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
                    {
                        "src": img.src,
                        "alt": img.alt,
                        "title": img.title,
                        "aria_describedby": img.aria_describedby,
                    }
                    for img in parsed.images
                ]
                console.print(f"  Found {len(parsed.images)} usable images in content")

            task = progress.add_task("Generating script...", total=None)
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
                )
            )
            progress.update(task, completed=True)
            console.print(f"✓ Generated script: {script.title}")
            console.print(f"  Sections: {len(script.sections)}")

            # Save script to YAML
            script_dict = {
                "title": script.title,
                "description": script.description,
                "sections": [
                    {
                        "title": section.title,
                        "narration": section.narration,
                        "slide_prompt": section.slide_prompt,
                        "source_image_url": section.source_image_url,
                    }
                    for section in script.sections
                ],
            }
            # Add pronunciations if available
            if script.pronunciations:
                script_dict["pronunciations"] = [
                    {
                        "word": entry.word,
                        "reading": entry.reading,
                        "word_type": entry.word_type,
                        "accent": entry.accent,
                    }
                    for entry in script.pronunciations
                ]
            with open(script_path, "w", encoding="utf-8") as f:
                yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)
            console.print(f"✓ Script saved: {script_path}")
            if script.pronunciations:
                console.print(f"  Pronunciations: {len(script.pronunciations)} entries")

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

        # Step 4: Split into phrases
        task = progress.add_task("Splitting into phrases...", total=None)

        # First pass: generate all phrases to determine original_index
        all_sections_phrases = []
        for section_idx, section in enumerate(script.sections):
            phrases = split_into_phrases(section.narration)
            for phrase in phrases:
                phrase.section_index = section_idx
            all_sections_phrases.append((section_idx, phrases))

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
        console.print(f"✓ Split into {len(all_phrases)} phrases")

        # Step 4: Generate audio
        task = progress.add_task("Generating audio...", total=None)
        synthesizer = create_synthesizer_from_config(cfg)

        # Add pronunciations from script to dictionary (LLM-generated, high priority)
        if script.pronunciations:
            for entry in script.pronunciations:
                synthesizer.dictionary.add_word(
                    word=entry.word,
                    reading=entry.reading,
                    accent=entry.accent,
                    word_type=entry.word_type,
                    priority=10,  # High priority for LLM-generated pronunciations
                )
            console.print(f"  Added {len(script.pronunciations)} LLM pronunciations to dictionary")

        # Add morphological analysis pronunciations (auto-generated, lower priority)
        narration_texts = [section.narration for section in script.sections]
        morpheme_count = synthesizer.prepare_texts(narration_texts)
        if morpheme_count > 0:
            console.print(f"  Added {morpheme_count} morphological analysis pronunciations")

        # Initialize VOICEVOX if not in placeholder mode
        if not allow_placeholder:
            import os

            dict_dir_str = os.getenv("VOICEVOX_DICT_DIR")
            model_path_str = os.getenv("VOICEVOX_MODEL_PATH")
            onnxruntime_path_str = os.getenv("VOICEVOX_ONNXRUNTIME_PATH")

            if dict_dir_str and model_path_str:
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
            console.print(f"✓ Audio: {new_audio_count} generated, {existing_audio_count} reused")
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
        transition_config = {
            "type": cfg.video.transition.type,
            "duration_frames": cfg.video.transition.duration_frames,
            "timing": cfg.video.transition.timing,
        }

        # Step 7: Setup Remotion project and render video
        video_path = output_dir / "output.mp4"
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
        project.setup_remotion_project()
        project.project_dir = original_project_dir
        progress.update(task, completed=True)

        # Render video with Remotion
        task = progress.add_task("Rendering video with Remotion...", total=None)
        render_video_with_remotion(
            phrases=all_phrases,
            audio_paths=audio_paths,
            slide_paths=slide_paths,
            output_path=video_path,
            remotion_root=remotion_dir,
            project_name=project_name,
            show_progress=show_progress,
            transition=transition_config,
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
