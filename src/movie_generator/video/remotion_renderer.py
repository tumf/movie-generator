"""Video rendering using Remotion CLI.

Generates video using Remotion's render functionality with subtitle animations.
Per-project Remotion setup with pnpm workspace integration.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from ..script.phrases import Phrase

console = Console()


@dataclass
class RemotionPhrase:
    """Phrase data for Remotion composition."""

    text: str
    audioFile: str
    slideFile: str | None
    duration: float


def create_remotion_input(
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None = None,
) -> list[dict[str, Any]]:
    """Create input data for Remotion composition.

    Args:
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths (relative to Remotion public/).
        slide_paths: Optional list of slide image paths (relative to Remotion public/).

    Returns:
        List of phrase dictionaries for Remotion.
    """
    remotion_phrases = []

    for i, phrase in enumerate(phrases):
        audio_file = str(audio_paths[i]) if i < len(audio_paths) else ""
        slide_file = str(slide_paths[i]) if slide_paths and i < len(slide_paths) else None

        remotion_phrases.append(
            {
                "text": phrase.text,
                "audioFile": audio_file,
                "slideFile": slide_file,
                "duration": phrase.duration,
            }
        )

    return remotion_phrases


def _get_slide_file_path(slide_paths: list[Path], index: int) -> str:
    """Get slide file path relative to Remotion public directory.

    Handles both legacy flat structure and new language-based structure.

    Args:
        slide_paths: List of slide paths.
        index: Index of the slide.

    Returns:
        Slide path relative to public directory (e.g., "slides/ja/slide_0000.png").
    """
    if not slide_paths or index >= len(slide_paths):
        return ""

    slide_path = slide_paths[index]

    # If slide_path is absolute, try to make it relative to find the structure
    # Expected structure: .../slides/[lang or provider]/slide_XXXX.png
    parts = slide_path.parts

    # Find 'slides' in the path
    try:
        slides_idx = parts.index("slides")
        # Get everything from 'slides' onwards
        relative_parts = parts[slides_idx:]
        return str(Path(*relative_parts))
    except (ValueError, IndexError):
        # Fallback: just use the filename under slides/
        return f"slides/{slide_path.name}"


def ensure_pnpm_dependencies(remotion_root: Path) -> None:
    """Ensure pnpm dependencies are installed in the Remotion project.

    Args:
        remotion_root: Path to Remotion project root directory.

    Raises:
        RuntimeError: If pnpm install fails.
    """
    node_modules = remotion_root / "node_modules"
    if node_modules.exists():
        return

    console.print("[cyan]Installing Remotion dependencies with pnpm...[/cyan]")
    try:
        subprocess.run(
            ["pnpm", "install"],
            cwd=remotion_root,
            check=True,
            capture_output=True,
            text=True,
        )
        console.print("[green]✓ Dependencies installed[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install dependencies:[/red]")
        console.print(f"[red]{e.stderr}[/red]")
        raise RuntimeError("pnpm install failed") from e


def update_composition_json(
    remotion_root: Path,
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    project_name: str,
) -> None:
    """Update composition.json with current phrase data.

    Args:
        remotion_root: Path to Remotion project root.
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths (relative to project).
        slide_paths: Optional list of slide image paths (relative to project).
        project_name: Name of the project.
    """
    composition_data = {
        "title": project_name,
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "phrases": [
            {
                "text": phrase.text,
                "audioFile": f"audio/{audio_paths[i].name}" if i < len(audio_paths) else "",
                "slideFile": _get_slide_file_path(slide_paths, phrase.section_index)
                if slide_paths and phrase.section_index < len(slide_paths)
                else None,
                "duration": phrase.duration,
            }
            for i, phrase in enumerate(phrases)
        ],
    }

    composition_path = remotion_root / "composition.json"
    with composition_path.open("w", encoding="utf-8") as f:
        json.dump(composition_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Updated composition.json with {len(phrases)} phrases[/green]")


def render_video_with_remotion(
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    output_path: Path,
    remotion_root: Path,
    project_name: str = "video",
) -> None:
    """Render video using Remotion CLI with per-project setup.

    Args:
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths.
        slide_paths: Optional list of slide image paths.
        output_path: Path to save rendered video.
        remotion_root: Path to Remotion project root directory.
        project_name: Name of the project for metadata.

    Raises:
        FileNotFoundError: If Remotion is not installed.
        RuntimeError: If video rendering fails.
    """
    # Skip if video already exists and is not empty
    if output_path.exists() and output_path.stat().st_size > 0:
        console.print(f"[yellow]↷ Skipping existing video: {output_path.name}[/yellow]")
        return

    # Ensure pnpm dependencies are installed
    ensure_pnpm_dependencies(remotion_root)

    # Update composition.json with current data
    update_composition_json(remotion_root, phrases, audio_paths, slide_paths, project_name)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate total duration
    total_duration = sum(p.duration for p in phrases)
    total_frames = int(total_duration * 30)  # 30 fps

    # Render video using Remotion CLI
    try:
        console.print(
            f"[cyan]🎬 Rendering video with Remotion ({total_duration:.1f}s, {total_frames} frames)...[/cyan]"
        )

        result = subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "VideoGenerator",
                str(output_path.absolute()),
                "--overwrite",
            ],
            cwd=remotion_root,
            check=True,
            capture_output=True,
            text=True,
        )

        console.print(f"[green]✓ Video rendered: {output_path}[/green]")

    except subprocess.CalledProcessError as e:
        error_msg = f"Remotion rendering failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        console.print(f"[red]{error_msg}[/red]")
        raise RuntimeError(error_msg) from e
