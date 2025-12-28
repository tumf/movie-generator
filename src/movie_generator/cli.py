"""CLI for movie generator.

Command-line interface for generating YouTube videos from blog URLs.
"""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .audio.voicevox import create_synthesizer_from_config
from .config import Config, load_config
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
def generate(url: str, config: Path | None, output: Path | None, api_key: str | None) -> None:
    """Generate video from URL.

    Args:
        url: Blog URL to convert to video.
        config: Path to config file.
        output: Output directory.
        api_key: OpenRouter API key.
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
        task = progress.add_task("Generating script...", total=None)
        script = asyncio.run(
            generate_script(
                content=parsed.markdown,
                title=parsed.metadata.title,
                description=parsed.metadata.description,
                character=cfg.narration.character,
                style=cfg.narration.style,
                api_key=api_key,
                model=cfg.content.model,
            )
        )
        progress.update(task, completed=True)
        console.print(f"✓ Generated script: {script.title}")
        console.print(f"  Sections: {len(script.sections)}")

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
        synthesizer = create_synthesizer_from_config(cfg)
        # Note: Placeholder - real implementation would initialize VOICEVOX
        # synthesizer.initialize(dict_dir, model_path)
        audio_dir = output_dir / "audio"
        audio_paths, metadata_list = synthesizer.synthesize_phrases(all_phrases, audio_dir)
        calculate_phrase_timings(all_phrases)
        progress.update(task, completed=True)
        console.print(f"✓ Generated {len(audio_paths)} audio files")

        # Step 5: Generate slides
        if api_key:
            task = progress.add_task("Generating slides...", total=None)
            slide_prompts = [
                (section.title, section.slide_prompt or section.title)
                for section in script.sections
            ]
            slide_dir = output_dir / "slides"
            slide_paths = asyncio.run(
                generate_slides_for_sections(slide_prompts, slide_dir, api_key, cfg.slides.model)
            )
            progress.update(task, completed=True)
            console.print(f"✓ Generated {len(slide_paths)} slides")
        else:
            console.print("[yellow]⚠ Skipping slides (no API key provided)[/yellow]")
            slide_paths = []

        # Step 6: Create composition
        task = progress.add_task("Creating composition...", total=None)
        composition = create_composition(
            title=script.title,
            phrases=all_phrases,
            slide_paths=slide_paths,
            audio_paths=audio_paths,
            fps=cfg.style.fps,
            resolution=cfg.style.resolution,
        )
        composition_path = output_dir / "composition.json"
        save_composition(composition, composition_path)
        progress.update(task, completed=True)
        console.print(f"✓ Created composition: {composition_path}")

        # Step 7: Render video (placeholder)
        task = progress.add_task("Rendering video...", total=None)
        video_path = output_dir / "output.mp4"
        render_video(composition_path, video_path)
        progress.update(task, completed=True)
        console.print(f"✓ Video ready: {video_path}")

    console.print("\n[bold green]✓ Video generation complete![/bold green]")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
