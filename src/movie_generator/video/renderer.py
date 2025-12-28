"""Video rendering using Remotion.

Generates composition.json and renders video using Remotion.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..script.phrases import Phrase


@dataclass
class CompositionData:
    """Data for Remotion composition."""

    title: str
    fps: int
    width: int
    height: int
    phrases: list[dict[str, Any]]
    slides: list[str]
    audio_files: list[str]


def create_composition(
    title: str,
    phrases: list[Phrase],
    slide_paths: list[Path],
    audio_paths: list[Path],
    fps: int = 30,
    resolution: tuple[int, int] = (1920, 1080),
) -> CompositionData:
    """Create composition data for Remotion.

    Args:
        title: Video title.
        phrases: List of phrases with timing.
        slide_paths: List of slide image paths.
        audio_paths: List of audio file paths.
        fps: Frames per second.
        resolution: Video resolution (width, height).

    Returns:
        Composition data object.
    """
    phrase_dicts = [
        {
            "text": p.text,
            "duration": p.duration,
            "start_time": p.start_time,
        }
        for p in phrases
    ]

    return CompositionData(
        title=title,
        fps=fps,
        width=resolution[0],
        height=resolution[1],
        phrases=phrase_dicts,
        slides=[str(p) for p in slide_paths],
        audio_files=[str(p) for p in audio_paths],
    )


def save_composition(composition: CompositionData, output_path: Path) -> None:
    """Save composition data to JSON file.

    Args:
        composition: Composition data.
        output_path: Path to save JSON file.
    """
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(composition), f, ensure_ascii=False, indent=2)


def render_video(
    composition_path: Path, output_path: Path, remotion_root: Path | None = None
) -> None:
    """Render video using Remotion.

    Args:
        composition_path: Path to composition.json.
        output_path: Path to save rendered video.
        remotion_root: Path to Remotion project root.

    Note:
        This is a placeholder. Real implementation would call:
        npx remotion render <composition> <output>
    """
    # Placeholder implementation
    # Real implementation would:
    # 1. Call npx remotion render with composition data
    # 2. Wait for rendering to complete
    # 3. Move output to specified path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"")
