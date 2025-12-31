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

from ..exceptions import RenderingError
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


def _build_slide_map(slide_paths: list[Path]) -> dict[int, str]:
    """Build a map from section_index to slide file path.

    Args:
        slide_paths: List of slide paths.

    Returns:
        Dictionary mapping section_index to slide path string.
    """
    slide_map: dict[int, str] = {}
    for slide_path in slide_paths:
        filename = slide_path.name
        # Extract section index from filename (e.g., "slide_0003.png" -> 3)
        if filename.startswith("slide_") and filename.endswith(".png"):
            try:
                section_index = int(filename[6:10])
                # Determine if it's in a language subdirectory
                if slide_path.parent.name in ["ja", "en", "zh"]:
                    lang = slide_path.parent.name
                    slide_map[section_index] = f"slides/{lang}/{filename}"
                else:
                    slide_map[section_index] = f"slides/{filename}"
            except ValueError:
                pass
    return slide_map


def _get_slide_file_path(slide_paths: list[Path], section_index: int) -> str:
    """Get slide file path relative to Remotion public directory.

    Handles both legacy flat structure and new language-based structure.

    Args:
        slide_paths: List of slide paths.
        section_index: Section index to find slide for.

    Returns:
        Slide path relative to public directory (e.g., "slides/ja/slide_0000.png").
    """
    if not slide_paths:
        return ""

    # Build slide map and look up by section_index
    slide_map = _build_slide_map(slide_paths)
    return slide_map.get(section_index, "")


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
        console.print("[red]Failed to install dependencies:[/red]")
        console.print(f"[red]{e.stderr}[/red]")
        raise RenderingError("pnpm install failed") from e


def update_composition_json(
    remotion_root: Path,
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    project_name: str = "video",
    transition: dict[str, Any] | None = None,
    personas: list[dict[str, Any]] | None = None,
) -> None:
    """Update composition.json with current phrase data.

    Args:
        remotion_root: Path to Remotion project root.
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths (relative to project).
        slide_paths: Optional list of slide image paths (relative to project).
        project_name: Name of the project.
        transition: Transition configuration (type, duration_frames, timing).
        personas: Optional list of persona configurations for multi-speaker dialogue.
    """
    # Build slide map for efficient lookup
    slide_map = _build_slide_map(slide_paths) if slide_paths else {}

    # Build persona lookup map
    persona_map: dict[str, dict[str, Any]] = {}
    if personas:
        for persona in personas:
            persona_map[persona["id"]] = persona

    composition_data = {
        "title": project_name,
        "fps": 30,
        "width": 1920,
        "height": 1080,
        "phrases": [
            {
                "text": phrase.get_subtitle_text(),
                "audioFile": f"audio/phrase_{phrase.original_index:04d}.wav",
                "slideFile": slide_map.get(phrase.section_index),
                "duration": phrase.duration,
                # Add persona information if available
                **_get_persona_fields(phrase, persona_map),
            }
            for i, phrase in enumerate(phrases)
        ],
    }

    # Add transition config if provided
    if transition:
        composition_data["transition"] = transition

    composition_path = remotion_root / "composition.json"
    with composition_path.open("w", encoding="utf-8") as f:
        json.dump(composition_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Updated composition.json with {len(phrases)} phrases[/green]")


def _get_persona_fields(phrase: Phrase, persona_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Get persona-related fields for a phrase.

    Args:
        phrase: Phrase object.
        persona_map: Map of persona ID to persona config.

    Returns:
        Dictionary with personaId, personaName, and subtitleColor fields.
    """
    if not phrase.persona_id or not persona_map:
        return {}

    persona = persona_map.get(phrase.persona_id)
    if not persona:
        return {
            "personaId": phrase.persona_id,
            "personaName": phrase.persona_name,
        }

    return {
        "personaId": phrase.persona_id,
        "personaName": persona.get("name", phrase.persona_name),
        "subtitleColor": persona.get("subtitle_color", "#FFFFFF"),
    }


def render_video_with_remotion(
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    output_path: Path,
    remotion_root: Path,
    project_name: str = "video",
    show_progress: bool = False,
    transition: dict[str, Any] | None = None,
    personas: list[dict[str, Any]] | None = None,
) -> None:
    """Render video using Remotion CLI with per-project setup.

    Args:
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths.
        slide_paths: Optional list of slide image paths.
        output_path: Path to save rendered video.
        remotion_root: Path to Remotion project root directory.
        project_name: Name of the project for metadata.
        show_progress: If True, show real-time rendering progress. Default False.
        transition: Transition configuration (type, duration_frames, timing).
        personas: Optional list of persona configurations for multi-speaker dialogue.

    Raises:
        FileNotFoundError: If Remotion is not installed.
        RuntimeError: If video rendering fails.
    """
    # Ensure pnpm dependencies are installed
    ensure_pnpm_dependencies(remotion_root)

    # Update composition.json with current data
    update_composition_json(
        remotion_root, phrases, audio_paths, slide_paths, project_name, transition, personas
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate total duration
    total_duration = sum(p.duration for p in phrases)
    total_frames = int(total_duration * 30)  # 30 fps

    # Render video using Remotion CLI
    try:
        # Only show initial message when progress is hidden
        if not show_progress:
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
                "--concurrency",
                "8",  # Use 8 concurrent threads for faster rendering
            ],
            cwd=remotion_root,
            check=True,
            # Show progress only if requested
            capture_output=not show_progress,
            text=True,
        )

        # Only show completion message when progress is hidden
        if not show_progress:
            console.print(f"[green]✓ Video rendered: {output_path}[/green]")

    except subprocess.CalledProcessError as e:
        if show_progress:
            console.print(f"[red]Remotion rendering failed with exit code {e.returncode}[/red]")
        else:
            error_msg = f"Remotion rendering failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            console.print(f"[red]{error_msg}[/red]")
        raise RenderingError(f"Remotion rendering failed with exit code {e.returncode}") from e
