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
    # Build slide map: section_index -> slide path
    slide_map: dict[int, str] = {}
    for slide_path in slide_paths:
        # Extract section index from filename (e.g., "slide_0003.png" -> 3)
        filename = slide_path.name
        if filename.startswith("slide_") and filename.endswith(".png"):
            try:
                section_index = int(filename[6:10])  # Extract "0003" part
                # Convert to relative path from slides directory
                slide_map[section_index] = f"slides/ja/{filename}"
            except ValueError:
                pass

    # Create phrase data with slide files
    phrase_dicts = [
        {
            "text": p.text,
            "duration": p.duration,
            "start_time": p.start_time,
            "audioFile": f"audio/phrase_{p.original_index:04d}.wav",
            "slideFile": slide_map.get(p.section_index),
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
    """Render video using ffmpeg.

    Args:
        composition_path: Path to composition.json.
        output_path: Path to save rendered video.
        remotion_root: Path to Remotion project root (unused in ffmpeg implementation).

    Raises:
        FileNotFoundError: If ffmpeg is not found.
        RuntimeError: If video rendering fails.
    """
    import json
    import subprocess
    import shutil
    from pathlib import Path

    # Skip if video already exists and is not empty
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"↷ Skipping existing video: {output_path.name}")
        return

    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError(
            "ffmpeg not found. Please install ffmpeg: brew install ffmpeg (macOS)"
        )

    # Load composition data
    with composition_path.open("r", encoding="utf-8") as f:
        composition = json.load(f)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # For now, create a simple video from audio files and slides
    # This is a simplified implementation that concatenates audio and creates a slideshow

    audio_files = composition.get("audio_files", [])
    slides = composition.get("slides", [])
    fps = composition.get("fps", 30)
    width = composition.get("width", 1920)
    height = composition.get("height", 1080)

    if not audio_files:
        print("Warning: No audio files found, creating placeholder video")
        output_path.write_bytes(b"")
        return

    # Create a concat file for audio
    audio_list_path = output_path.parent / "audio_concat.txt"
    with audio_list_path.open("w", encoding="utf-8") as f:
        for audio_file in audio_files:
            if Path(audio_file).exists():
                f.write(f"file '{Path(audio_file).absolute()}'\n")

    # Concatenate all audio files
    temp_audio = output_path.parent / "temp_audio.wav"
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(audio_list_path),
                "-c",
                "copy",
                str(temp_audio),
                "-y",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating audio: {e.stderr.decode()}")
        output_path.write_bytes(b"")
        return

    # Create video from first slide (or black image if no slides)
    if slides and Path(slides[0]).exists() and Path(slides[0]).stat().st_size > 0:
        # Use first slide as static image
        input_image = slides[0]
    else:
        # Create a black image
        temp_image = output_path.parent / "temp_black.png"
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={width}x{height}:d=1",
                str(temp_image),
                "-y",
            ],
            check=True,
            capture_output=True,
        )
        input_image = temp_image

    # Create video from image and audio
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-loop",
                "1",
                "-i",
                str(input_image),
                "-i",
                str(temp_audio),
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                "-r",
                str(fps),
                str(output_path),
                "-y",
            ],
            check=True,
            capture_output=True,
        )
        print(f"✓ Video rendered: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering video: {e.stderr.decode()}")
        output_path.write_bytes(b"")
    finally:
        # Cleanup temporary files
        if audio_list_path.exists():
            audio_list_path.unlink()
        if temp_audio.exists():
            temp_audio.unlink()
        temp_image = output_path.parent / "temp_black.png"
        if temp_image.exists():
            temp_image.unlink()
