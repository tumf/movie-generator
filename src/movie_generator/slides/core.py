"""Core slide generation functionality.

Provides library functions for slide generation that can be called
directly by worker processes or other Python code, without CLI overhead.
"""

from collections.abc import Callable
from pathlib import Path

import yaml

from ..script.generator import Narration, ScriptSection, VideoScript
from .generator import generate_slides_for_sections


async def generate_slides_for_script(
    script_path: Path,
    output_dir: Path | None = None,
    api_key: str | None = None,
    model: str = "google/gemini-3-pro-image-preview",
    base_url: str = "https://openrouter.ai/api/v1",
    language: str = "ja",
    max_concurrent: int = 2,
    scenes: tuple[int | None, int | None] | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
    resolution: tuple[int, int] | None = None,
) -> list[Path]:
    """Generate slide images from script.yaml.

    Reads the script, extracts slide prompts, and generates slide images
    using AI models or downloads from source URLs.

    Args:
        script_path: Path to script.yaml file.
        output_dir: Output directory for slides. If None, uses script.parent / "slides".
        api_key: OpenRouter API key for image generation.
        model: AI model identifier for slide generation.
        language: Language code for organizing output (ja, en, etc.).
        max_concurrent: Maximum number of concurrent slide generation requests.
        scenes: Optional scene range (start_index, end_index), 0-based inclusive.
                Either value can be None to indicate "from beginning" or "to end".
        progress_callback: Optional callback(current, total, message) called during generation.

    Returns:
        List of paths to generated/downloaded slides.

    Raises:
        FileNotFoundError: If script file doesn't exist.
        ValueError: If API key is not provided.

    Example:
        >>> import asyncio
        >>> from pathlib import Path
        >>>
        >>> async def main():
        ...     slides = await generate_slides_for_script(
        ...         script_path=Path("script.yaml"),
        ...         output_dir=Path("slides"),
        ...         api_key="your-api-key",
        ...         progress_callback=lambda c, t, m: print(f"{c}/{t}: {m}")
        ...     )
        ...     return slides
        >>>
        >>> asyncio.run(main())
    """
    if not script_path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")

    if not api_key:
        raise ValueError("API key is required for slide generation")

    # Determine output directory
    if output_dir is None:
        output_dir = script_path.parent
    slide_dir = output_dir / "slides"
    slide_dir.mkdir(parents=True, exist_ok=True)

    # Parse scene range
    scene_start: int | None = None
    scene_end: int | None = None
    if scenes is not None:
        scene_start, scene_end = scenes

    # Load and parse script
    with open(script_path, encoding="utf-8") as f:
        script_dict = yaml.safe_load(f)

    sections = []
    for section in script_dict["sections"]:
        narrations: list[Narration] = []

        if "narrations" in section and section["narrations"]:
            for n in section["narrations"]:
                if isinstance(n, str):
                    narrations.append(Narration(text=n, reading=n))
                else:
                    reading = n.get("reading", n["text"])
                    narrations.append(
                        Narration(text=n["text"], reading=reading, persona_id=n.get("persona_id"))
                    )
        elif "dialogues" in section and section["dialogues"]:
            for d in section["dialogues"]:
                reading = d.get("reading", d["narration"])
                narrations.append(
                    Narration(text=d["narration"], reading=reading, persona_id=d["persona_id"])
                )
        elif "narration" in section:
            narrations.append(Narration(text=section["narration"], reading=section["narration"]))

        sections.append(
            ScriptSection(
                title=section["title"],
                narrations=narrations,
                slide_prompt=section.get("slide_prompt"),
                source_image_url=section.get("source_image_url"),
                background=section.get("background"),
            )
        )

    video_script = VideoScript(
        title=script_dict["title"],
        description=script_dict["description"],
        sections=sections,
    )

    # Filter slide prompts based on scene range
    slide_prompts = []
    slide_indices = []
    for section_idx, section in enumerate(video_script.sections):
        if scene_start is not None and section_idx < scene_start:
            continue
        if scene_end is not None and section_idx > scene_end:
            continue
        slide_prompts.append(
            (section.title, section.slide_prompt or section.title, section.source_image_url)
        )
        slide_indices.append(section_idx)

    total_slides = len(slide_prompts)
    if progress_callback:
        progress_callback(0, total_slides, "Starting slide generation...")

    # Generate slides with modified progress reporting
    # The underlying function prints to stdout, we'll wrap it to capture progress
    if progress_callback:
        # Count existing slides
        lang_slide_dir = slide_dir / language
        existing_count = sum(
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
        if existing_count > 0:
            progress_callback(
                existing_count,
                total_slides,
                f"Found {existing_count} existing slides, generating {total_slides - existing_count}...",
            )

    slide_paths = await generate_slides_for_sections(
        sections=slide_prompts,
        output_dir=slide_dir,
        api_key=api_key,
        model=model,
        base_url=base_url,
        max_concurrent=max_concurrent,
        section_indices=slide_indices,
        language=language,
        resolution=resolution or (1280, 720),
    )

    # Count successful slides
    successful_count = sum(1 for p in slide_paths if p.exists() and p.stat().st_size > 0)
    failed_count = len(slide_paths) - successful_count

    if progress_callback:
        if failed_count > 0:
            progress_callback(
                successful_count,
                total_slides,
                f"Slide generation complete: {successful_count} succeeded, {failed_count} failed",
            )
        else:
            progress_callback(total_slides, total_slides, "Slide generation complete")

    return slide_paths
