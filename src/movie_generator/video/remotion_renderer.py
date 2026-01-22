"""Video rendering using Remotion CLI.

Generates video using Remotion's render functionality with subtitle animations.
Per-project Remotion setup with pnpm workspace integration.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console

from ..constants import SubtitleConstants, TimeoutConstants, VideoConstants
from ..exceptions import RenderingError
from ..script.phrases import Phrase
from .renderer import CompositionPhrase

console = Console()


def _get_video_duration_frames(video_path: Path, fps: int = 30) -> int | None:
    """Get video duration in frames using ffprobe.

    Args:
        video_path: Path to the video file.
        fps: Frames per second (default: 30).

    Returns:
        Duration in frames, or None if unable to determine.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration_seconds = float(result.stdout.strip())
        return int(duration_seconds * fps)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


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
    composition_phrases = []

    for i, phrase in enumerate(phrases):
        audio_file = str(audio_paths[i]) if i < len(audio_paths) else ""
        slide_file = str(slide_paths[i]) if slide_paths and i < len(slide_paths) else None

        composition_phrases.append(
            CompositionPhrase(
                text=phrase.text,
                duration=phrase.duration,
                start_time=phrase.start_time,
                audioFile=audio_file,
                slideFile=slide_file,
            )
        )

    return [p.model_dump(exclude_none=True) for p in composition_phrases]


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


def ensure_chrome_headless_shell(remotion_root: Path) -> None:
    """Ensure Chrome Headless Shell is downloaded for Remotion rendering.

    Uses a global cache directory to share the browser across all projects,
    avoiding redundant downloads.

    Args:
        remotion_root: Path to Remotion project root directory.

    Raises:
        RuntimeError: If browser download fails.
    """
    # Global cache directory for Chrome Headless Shell
    # Place it at the project root level (parent of output directories)
    # In Docker, use /app as project root; otherwise use cwd
    import os

    if os.getenv("DOCKER_ENV"):
        project_root = Path("/app")
    else:
        project_root = Path.cwd()
    global_cache = project_root / ".cache" / "remotion" / "chrome-headless-shell"

    # Target path in this project's node_modules
    local_remotion_dir = remotion_root / "node_modules" / ".remotion"
    local_browser_path = local_remotion_dir / "chrome-headless-shell"

    # If local path already exists (file or symlink), we're done
    if local_browser_path.exists() or local_browser_path.is_symlink():
        return

    # Ensure local .remotion directory exists
    local_remotion_dir.mkdir(parents=True, exist_ok=True)

    # If global cache doesn't exist, download it first
    if not global_cache.exists():
        console.print("[cyan]Downloading Chrome Headless Shell (shared cache)...[/cyan]")

        # Create a temporary project to download the browser
        temp_download_dir = project_root / ".cache" / "remotion" / "_temp_download"
        temp_download_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create minimal package.json for download
            temp_package_json = temp_download_dir / "package.json"
            temp_package_json.write_text('{"dependencies": {"@remotion/cli": "^4.0.0"}}')

            # Install remotion CLI in temp directory
            # NOTE: --ignore-workspace is required because the project may have
            # pnpm-workspace.yaml, and pnpm would otherwise refuse to install
            # dependencies outside the workspace-defined packages
            subprocess.run(
                ["pnpm", "install", "--no-frozen-lockfile", "--ignore-workspace"],
                cwd=temp_download_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            # Download browser
            # Use direct path to remotion binary instead of npx
            # npx does not work reliably in pnpm environments
            remotion_bin = temp_download_dir / "node_modules" / ".bin" / "remotion"
            subprocess.run(
                [str(remotion_bin), "browser", "ensure"],
                cwd=temp_download_dir,
                check=True,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.VIDEO_RENDER_DOWNLOAD,
            )

            # Move downloaded browser to global cache
            temp_browser = (
                temp_download_dir / "node_modules" / ".remotion" / "chrome-headless-shell"
            )
            if temp_browser.exists():
                global_cache.parent.mkdir(parents=True, exist_ok=True)
                import shutil

                shutil.move(str(temp_browser), str(global_cache))
                console.print("[green]✓ Chrome Headless Shell downloaded to shared cache[/green]")
            else:
                raise RenderingError("Browser download succeeded but files not found")

        except subprocess.TimeoutExpired as e:
            console.print("[red]Browser download timed out (5 minutes)[/red]")
            raise RenderingError("Chrome Headless Shell download timed out") from e
        except subprocess.CalledProcessError as e:
            console.print("[red]Failed to download Chrome Headless Shell:[/red]")
            console.print(f"[red]{e.stderr}[/red]")
            raise RenderingError("Chrome Headless Shell download failed") from e
        finally:
            # Clean up temp directory
            import shutil

            if temp_download_dir.exists():
                shutil.rmtree(temp_download_dir, ignore_errors=True)

    # Create symlink from local path to global cache
    try:
        local_browser_path.symlink_to(global_cache, target_is_directory=True)
        console.print("[green]✓ Chrome Headless Shell linked from shared cache[/green]")
    except OSError as e:
        console.print(f"[yellow]Warning: Failed to create symlink: {e}[/yellow]")
        console.print("[yellow]Falling back to copying browser files...[/yellow]")
        import shutil

        shutil.copytree(global_cache, local_browser_path)


def update_composition_json(
    remotion_root: Path,
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    project_name: str = "video",
    transition: dict[str, Any] | None = None,
    personas: list[dict[str, Any]] | None = None,
    background: dict[str, Any] | None = None,
    bgm: dict[str, Any] | None = None,
    section_backgrounds: dict[int, dict[str, Any]] | None = None,
    fps: int = VideoConstants.DEFAULT_FPS,
    resolution: tuple[int, int] = (VideoConstants.DEFAULT_WIDTH, VideoConstants.DEFAULT_HEIGHT),
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
        background: Optional global background configuration (type, path, fit).
        bgm: Optional BGM configuration (path, volume, fade_in_seconds, fade_out_seconds, loop).
        section_backgrounds: Optional map of section_index to background override.
        fps: Frames per second.
        resolution: Video resolution as (width, height) tuple.
    """
    # Build slide map for efficient lookup
    slide_map = _build_slide_map(slide_paths) if slide_paths else {}

    # Build persona lookup map and position assignment map
    persona_map: dict[str, dict[str, Any]] = {}
    persona_position_map: dict[str, str] = {}
    if personas:
        # Assign positions based on persona order
        positions = ["left", "right", "center"]
        for i, persona in enumerate(personas):
            persona_id = persona["id"]
            persona_map[persona_id] = persona
            # Assign position: first persona -> left, second -> right, third+ -> center
            persona_position_map[persona_id] = positions[min(i, len(positions) - 1)]

    # Create CompositionPhrase objects
    composition_phrases = []
    for phrase in phrases:
        persona_fields = _get_persona_fields(phrase, persona_map, persona_position_map)
        # Get background override for this section
        bg_override = None
        if section_backgrounds and phrase.section_index in section_backgrounds:
            bg_dict = section_backgrounds[phrase.section_index].copy()
            # Convert background path to public-relative
            bg_dict["path"] = _copy_asset_to_public(
                Path(bg_dict["path"]), remotion_root, "backgrounds"
            )
            bg_override = bg_dict

        composition_phrases.append(
            CompositionPhrase(
                text=phrase.get_subtitle_text(),
                duration=phrase.duration,
                start_time=phrase.start_time,
                audioFile=f"audio/phrase_{phrase.original_index:04d}.wav",
                slideFile=slide_map.get(phrase.section_index),
                persona_id=persona_fields.get("personaId"),
                persona_name=persona_fields.get("personaName"),
                subtitle_color=persona_fields.get("subtitleColor"),
                character_image=persona_fields.get("characterImage"),
                character_position=persona_fields.get("characterPosition"),
                mouth_open_image=persona_fields.get("mouthOpenImage"),
                eye_close_image=persona_fields.get("eyeCloseImage"),
                animation_style=persona_fields.get("animationStyle"),
                background_override=bg_override,
            )
        )

    composition_data = {
        "title": project_name,
        "fps": fps,
        "width": resolution[0],
        "height": resolution[1],
        "phrases": [p.model_dump(exclude_none=True, by_alias=True) for p in composition_phrases],
    }

    # Add transition config if provided
    if transition:
        composition_data["transition"] = transition

    # Add background config if provided (convert path to public-relative)
    if background:
        bg_config = background.copy()
        original_path = Path(background["path"])
        bg_config["path"] = _copy_asset_to_public(original_path, remotion_root, "backgrounds")

        # For video backgrounds, get the video duration for proper looping
        if background.get("type") == "video":
            loop_frames = _get_video_duration_frames(original_path)
            if loop_frames:
                bg_config["loopDurationInFrames"] = loop_frames

        composition_data["background"] = bg_config

    # Add BGM config if provided (convert path to public-relative)
    if bgm:
        bgm_config = bgm.copy()
        bgm_config["path"] = _copy_asset_to_public(Path(bgm["path"]), remotion_root, "bgm")
        composition_data["bgm"] = bgm_config

    # Add personas config if provided (for persistent character display)
    if personas:
        # Convert asset paths in personas to be relative to public/
        # Auto-assign character_position only if not configured
        converted_personas = []
        for i, persona in enumerate(personas):
            persona_copy = persona.copy()

            # CRITICAL: Always ensure character_position is set
            # Use config's character_position if set, otherwise use auto-assigned position
            if (
                "character_position" not in persona_copy
                or persona_copy["character_position"] is None
            ):
                # Auto-assign position based on persona order
                persona_id = persona["id"]
                if persona_id in persona_position_map:
                    persona_copy["character_position"] = persona_position_map[persona_id]
                else:
                    # Fallback: assign based on index
                    positions = ["left", "right", "center"]
                    persona_copy["character_position"] = positions[min(i, len(positions) - 1)]

            if "character_image" in persona_copy and persona_copy["character_image"] is not None:
                persona_copy["character_image"] = _convert_to_public_path(
                    persona_copy["character_image"]
                )
            if "mouth_open_image" in persona_copy and persona_copy["mouth_open_image"] is not None:
                persona_copy["mouth_open_image"] = _convert_to_public_path(
                    persona_copy["mouth_open_image"]
                )
            if "eye_close_image" in persona_copy and persona_copy["eye_close_image"] is not None:
                persona_copy["eye_close_image"] = _convert_to_public_path(
                    persona_copy["eye_close_image"]
                )
            converted_personas.append(persona_copy)
        composition_data["personas"] = converted_personas

    composition_path = remotion_root / "composition.json"
    with composition_path.open("w", encoding="utf-8") as f:
        json.dump(composition_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Updated composition.json with {len(phrases)} phrases[/green]")


def _get_persona_fields(
    phrase: Phrase,
    persona_map: dict[str, dict[str, Any]],
    persona_position_map: dict[str, str],
) -> dict[str, Any]:
    """Get persona-related fields for a phrase.

    Args:
        phrase: Phrase object.
        persona_map: Map of persona ID to persona config.
        persona_position_map: Map of persona ID to assigned position (left/right/center).

    Returns:
        Dictionary with personaId, personaName, subtitleColor, and character image fields.
    """
    if not phrase.persona_id or not persona_map:
        return {}

    persona = persona_map.get(phrase.persona_id)
    if not persona:
        return {
            "personaId": phrase.persona_id,
            "personaName": phrase.persona_name,
        }

    # Build character image paths relative to Remotion public/ directory
    character_fields: dict[str, Any] = {
        "personaId": phrase.persona_id,
        "personaName": persona.get("name", phrase.persona_name),
        "subtitleColor": persona.get("subtitle_color", SubtitleConstants.DEFAULT_COLOR),
    }

    # Add character images if configured
    if character_image := persona.get("character_image"):
        # Convert to path relative to public/ (e.g., "characters/zundamon/base.png")
        character_fields["characterImage"] = _convert_to_public_path(character_image)

    # Use config's character_position if set, otherwise use auto-assigned position
    if config_position := persona.get("character_position"):
        character_fields["characterPosition"] = config_position
    elif phrase.persona_id in persona_position_map:
        character_fields["characterPosition"] = persona_position_map[phrase.persona_id]

    if mouth_open_image := persona.get("mouth_open_image"):
        character_fields["mouthOpenImage"] = _convert_to_public_path(mouth_open_image)

    if eye_close_image := persona.get("eye_close_image"):
        character_fields["eyeCloseImage"] = _convert_to_public_path(eye_close_image)

    if animation_style := persona.get("animation_style"):
        character_fields["animationStyle"] = animation_style

    return character_fields


def _convert_to_public_path(asset_path: str | None) -> str | None:
    """Convert asset path to be relative to public/ directory.

    Args:
        asset_path: Path to asset file (e.g., "assets/characters/zundamon/base.png").

    Returns:
        Path relative to public/ directory (e.g., "characters/zundamon/base.png"),
        or None if input is None.
    """
    if asset_path is None:
        return None
    # If path starts with "assets/", remove it (assets are symlinked to public/)
    if asset_path.startswith("assets/"):
        return asset_path[7:]  # Remove "assets/" prefix
    return asset_path


def _has_attached_picture(file_path: Path) -> bool:
    """Check if an audio file has an attached picture (album art).

    MP3 files with embedded album art contain a video stream (usually mjpeg)
    marked as attached_pic. This can cause playback issues in Remotion.

    Args:
        file_path: Path to the audio file.

    Returns:
        True if the file has an attached picture stream.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type:stream_disposition=attached_pic",
                "-of",
                "csv=p=0",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # Look for lines indicating video stream with attached_pic=1
        for line in result.stdout.strip().split("\n"):
            if "video" in line and "1" in line:
                return True
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _strip_attached_picture(src_path: Path, dest_path: Path) -> bool:
    """Remove attached picture from audio file.

    Creates a clean copy of the audio file with only the audio stream,
    removing any embedded album art that could cause Remotion issues.

    Args:
        src_path: Source audio file path.
        dest_path: Destination path for cleaned audio.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src_path),
                "-map",
                "0:a:0",  # Select only first audio stream
                "-c:a",
                "copy",  # Copy without re-encoding
                str(dest_path),
            ],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _copy_asset_to_public(asset_path: Path, remotion_root: Path, category: str) -> str:
    """Copy asset file to Remotion public directory.

    For BGM files, automatically strips attached pictures (album art) which
    can cause playback issues in Remotion-rendered videos.

    Args:
        asset_path: Path to asset file (can be relative or absolute).
        remotion_root: Path to Remotion project root.
        category: Asset category (e.g., "backgrounds", "bgm").

    Returns:
        Path relative to public/ directory (e.g., "backgrounds/bg.png").

    Raises:
        FileNotFoundError: If asset file doesn't exist.
    """
    import shutil

    # Resolve relative paths from project root (/app/)
    # This is necessary because in Docker environment, the working directory
    # is the job directory (/app/data/jobs/{job_id}/), not the project root
    if not asset_path.is_absolute():
        project_root = Path("/app")
        resolved_path = None

        # Try /app/assets/{path} first (Docker mount: assets/ -> /app/assets/)
        assets_path = project_root / "assets" / asset_path
        if assets_path.exists():
            resolved_path = assets_path
        else:
            # Try project root directly
            root_path = project_root / asset_path
            if root_path.exists():
                resolved_path = root_path
            else:
                # Fallback to current working directory
                resolved_path = Path.cwd() / asset_path

        asset_path = resolved_path

    if not asset_path.exists():
        raise FileNotFoundError(f"Asset file not found: {asset_path}")

    # Create category directory in public/
    public_category_dir = remotion_root / "public" / category
    public_category_dir.mkdir(parents=True, exist_ok=True)

    dest_file = public_category_dir / asset_path.name

    # For BGM files, strip attached pictures (album art) to avoid playback issues
    if category == "bgm" and _has_attached_picture(asset_path):
        console.print(f"[yellow]Stripping album art from BGM: {asset_path.name}[/yellow]")
        if not _strip_attached_picture(asset_path, dest_file):
            # Fallback to simple copy if stripping fails
            console.print(
                "[yellow]Warning: Could not strip album art, using original file[/yellow]"
            )
            shutil.copy2(asset_path, dest_file)
    else:
        # Copy file to public directory
        shutil.copy2(asset_path, dest_file)

    # Return path relative to public/
    return f"{category}/{asset_path.name}"


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
    background: dict[str, Any] | None = None,
    bgm: dict[str, Any] | None = None,
    section_backgrounds: dict[int, dict[str, Any]] | None = None,
    crf: int = VideoConstants.DEFAULT_CRF,
    fps: int = VideoConstants.DEFAULT_FPS,
    resolution: tuple[int, int] = (VideoConstants.DEFAULT_WIDTH, VideoConstants.DEFAULT_HEIGHT),
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
        background: Optional global background configuration (type, path, fit).
        bgm: Optional BGM configuration (path, volume, fade_in_seconds, fade_out_seconds, loop).
        section_backgrounds: Optional map of section_index to background override.
        crf: Constant Rate Factor for video encoding (0-51, default 28).
        fps: Frames per second.
        resolution: Video resolution as (width, height) tuple.

    Raises:
        FileNotFoundError: If Remotion is not installed.
        RuntimeError: If video rendering fails.
    """
    # Create symlink to assets directory from job directory
    # This is needed for Docker environment where working directory is job dir
    # but assets are in project root (/app/assets)
    job_dir = remotion_root.parent
    assets_symlink = job_dir / "assets"
    if not assets_symlink.exists():
        import os

        project_root = Path("/app")
        assets_dir = project_root / "assets"
        if assets_dir.exists():
            os.symlink(assets_dir, assets_symlink)
            console.print(f"[green]Created symlink: {assets_symlink} -> {assets_dir}[/green]")

    # Ensure pnpm dependencies are installed
    ensure_pnpm_dependencies(remotion_root)

    # Ensure Chrome Headless Shell is downloaded
    ensure_chrome_headless_shell(remotion_root)

    # Update composition.json with current data
    update_composition_json(
        remotion_root,
        phrases,
        audio_paths,
        slide_paths,
        project_name,
        transition,
        personas,
        background,
        bgm,
        section_backgrounds,
        fps,
        resolution,
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate total duration including pauses
    # Use last phrase's end time (start_time + duration) + 1 second ending pause
    if phrases:
        total_duration = phrases[-1].start_time + phrases[-1].duration + 1.0  # +1s ending pause
    else:
        total_duration = 0.0
    total_frames = int(total_duration * fps)

    # Render video using Remotion CLI
    try:
        # Only show initial message when progress is hidden
        if not show_progress:
            console.print(
                f"[cyan]🎬 Rendering video with Remotion "
                f"({total_duration:.1f}s, {total_frames} frames)...[/cyan]"
            )

        # Run rendering (always execute, regardless of show_progress)
        subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "VideoGenerator",
                str(output_path.absolute()),
                "--overwrite",
                "--concurrency",
                "4",  # Reduced from 8 to prevent memory issues and timeouts
                "--timeout",
                "300000",  # 5 minutes timeout for delayRender calls (default is 30s)
                "--crf",
                str(crf),
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
