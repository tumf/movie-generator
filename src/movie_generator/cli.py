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
from .script.generator import generate_script
from .script.phrases import calculate_phrase_timings, split_into_phrases
from .slides.generator import generate_slides_for_sections
from .video.renderer import create_composition, render_video, save_composition

console = Console()


@click.group()
def cli() -> None:
    """Movie Generator - Generate YouTube videos from blog URLs."""
    pass


@cli.command()
@click.argument("url")
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
    "--allow-placeholder",
    is_flag=True,
    default=False,
    help="Allow running without VOICEVOX (generates placeholder audio for testing)",
)
def generate(
    url: str,
    config: Path | None,
    output: Path | None,
    api_key: str | None,
    allow_placeholder: bool,
) -> None:
    """Generate video from URL.

    Args:
        url: Blog URL to convert to video.
        config: Path to config file.
        output: Output directory.
        api_key: OpenRouter API key.
        allow_placeholder: Allow running without VOICEVOX (testing only).
    """
    # Load configuration
    cfg = load_config(config) if config else Config()

    # Set output directory
    output_dir = Path(output) if output else Path(cfg.project.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold]Generating video from:[/bold] {url}")
    console.print(f"[bold]Output directory:[/bold] {output_dir}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Fetch content
        task = progress.add_task("Fetching content...", total=None)
        html_content = fetch_url_sync(url)
        parsed = parse_html(html_content)
        progress.update(task, completed=True)
        console.print(f"✓ Fetched: {parsed.metadata.title}")

        # Step 2: Generate script
        script_path = output_dir / "script.yaml"
        if script_path.exists():
            console.print(f"[yellow]⊙ Script already exists, loading: {script_path}[/yellow]")
            with open(script_path, encoding="utf-8") as f:
                script_dict = yaml.safe_load(f)
            from .script.generator import ScriptSection, VideoScript

            script = VideoScript(
                title=script_dict["title"],
                description=script_dict["description"],
                sections=[
                    ScriptSection(
                        title=section["title"],
                        narration=section["narration"],
                        slide_prompt=section.get("slide_prompt"),
                    )
                    for section in script_dict["sections"]
                ],
            )
        else:
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
                    }
                    for section in script.sections
                ],
            }
            with open(script_path, "w", encoding="utf-8") as f:
                yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)
            console.print(f"✓ Script saved: {script_path}")

        # Step 3: Split into phrases
        task = progress.add_task("Splitting into phrases...", total=None)
        all_phrases = []
        for section in script.sections:
            phrases = split_into_phrases(section.narration)
            all_phrases.extend(phrases)
        progress.update(task, completed=True)
        console.print(f"✓ Split into {len(all_phrases)} phrases")

        # Step 4: Generate audio
        task = progress.add_task("Generating audio...", total=None)
        synthesizer = create_synthesizer_from_config(cfg, allow_placeholder=allow_placeholder)

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
        # Count existing audio files before generation
        existing_audio_count = sum(
            1 for i in range(len(all_phrases)) if (audio_dir / f"phrase_{i:04d}.wav").exists()
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
            slide_prompts = [
                (section.title, section.slide_prompt or section.title)
                for section in script.sections
            ]
            slide_dir = output_dir / "slides"
            # Count existing slides before generation
            existing_slide_count = sum(
                1
                for i in range(len(slide_prompts))
                if (slide_dir / f"slide_{i:04d}.png").exists()
                and (slide_dir / f"slide_{i:04d}.png").stat().st_size > 0
            )
            slide_paths = asyncio.run(
                generate_slides_for_sections(
                    slide_prompts, slide_dir, api_key, cfg.slides.llm.model
                )
            )
            progress.update(task, completed=True)
            new_slide_count = len(slide_paths) - existing_slide_count
            if existing_slide_count > 0:
                console.print(
                    f"✓ Slides: {new_slide_count} generated, {existing_slide_count} reused"
                )
            else:
                console.print(f"✓ Generated {len(slide_paths)} slides")
        else:
            console.print("[yellow]⚠ Skipping slides (no API key provided)[/yellow]")
            slide_paths = []

        # Step 6: Create composition
        composition_path = output_dir / "composition.json"
        if composition_path.exists():
            console.print(
                f"[yellow]⊙ Composition already exists, skipping: {composition_path}[/yellow]"
            )
        else:
            task = progress.add_task("Creating composition...", total=None)
            composition = create_composition(
                title=script.title,
                phrases=all_phrases,
                slide_paths=slide_paths,
                audio_paths=audio_paths,
                fps=cfg.style.fps,
                resolution=cfg.style.resolution,
            )
            save_composition(composition, composition_path)
            progress.update(task, completed=True)
            console.print(f"✓ Created composition: {composition_path}")

        # Step 7: Render video
        video_path = output_dir / "output.mp4"
        if video_path.exists():
            console.print(f"[yellow]⊙ Video already exists, skipping: {video_path}[/yellow]")
        else:
            task = progress.add_task("Rendering video...", total=None)
            render_video(composition_path, video_path)
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
