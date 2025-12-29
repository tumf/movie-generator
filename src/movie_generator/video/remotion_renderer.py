"""Video rendering using Remotion CLI.

Generates video using Remotion's render functionality with subtitle animations.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..script.phrases import Phrase


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


def render_video_with_remotion(
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    output_path: Path,
    remotion_root: Path,
) -> None:
    """Render video using Remotion CLI.

    Args:
        phrases: List of phrases with timing.
        audio_paths: List of audio file paths.
        slide_paths: Optional list of slide image paths.
        output_path: Path to save rendered video.
        remotion_root: Path to Remotion project root directory.

    Raises:
        FileNotFoundError: If Remotion is not installed.
        RuntimeError: If video rendering fails.
    """
    # Skip if video already exists and is not empty
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"↷ Skipping existing video: {output_path.name}")
        return

    # Check if Remotion is installed
    try:
        subprocess.run(
            ["npx", "remotion", "--version"],
            cwd=remotion_root,
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise FileNotFoundError("Remotion not found. Please install: cd remotion && npm install")

    # Create input data JSON
    remotion_data = create_remotion_input(phrases, audio_paths, slide_paths)
    input_props_path = remotion_root / "input_props.json"

    with input_props_path.open("w", encoding="utf-8") as f:
        json.dump({"phrases": remotion_data}, f, ensure_ascii=False, indent=2)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate total duration
    total_duration = sum(p.duration for p in phrases)
    total_frames = int(total_duration * 30)  # 30 fps

    # Render video using Remotion CLI
    try:
        print(f"🎬 Rendering video with Remotion ({total_duration:.1f}s, {total_frames} frames)...")

        result = subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "VideoGenerator",
                str(output_path.absolute()),
                "--props",
                str(input_props_path.absolute()),
            ],
            cwd=remotion_root,
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"✓ Video rendered: {output_path}")

        # Clean up input props file
        if input_props_path.exists():
            input_props_path.unlink()

    except subprocess.CalledProcessError as e:
        error_msg = f"Remotion rendering failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        print(error_msg)
        raise RuntimeError(error_msg) from e
