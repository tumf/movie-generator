"""Slide image generation using OpenRouter API.

Generates presentation slides using image generation models.
"""

import asyncio
import base64
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from ..constants import ProjectPaths, RetryConfig, VideoConstants
from ..utils.filesystem import is_valid_file, skip_if_exists


async def download_and_process_image(
    *,
    url: str,
    output_path: Path,
    target_width: int = VideoConstants.DEFAULT_WIDTH,
    target_height: int = VideoConstants.DEFAULT_HEIGHT,
    min_width: int = VideoConstants.MIN_WIDTH,
    min_height: int = VideoConstants.MIN_HEIGHT,
) -> Path:
    """Download and process an image from URL.

    Args:
        url: Image URL to download.
        output_path: Path to save processed image.
        target_width: Target width for resizing.
        target_height: Target height for resizing.
        min_width: Minimum acceptable width.
        min_height: Minimum acceptable height.

    Returns:
        Path to processed image file.

    Raises:
        httpx.HTTPError: If download fails.
        ValueError: If image is below minimum resolution.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if already exists
    if skip_if_exists(output_path, "image"):
        return output_path

    # Download image
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        image_data = response.content

    # Open image with PIL
    img = Image.open(BytesIO(image_data))

    # Check minimum resolution
    if img.width < min_width or img.height < min_height:
        raise ValueError(
            f"Image resolution {img.width}x{img.height} is below minimum {min_width}x{min_height}"
        )

    # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize to fit target dimensions while maintaining aspect ratio
    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    # Create canvas with target dimensions (centered)
    canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    offset_x = (target_width - img.width) // 2
    offset_y = (target_height - img.height) // 2
    canvas.paste(img, (offset_x, offset_y))

    # Save processed image
    canvas.save(output_path, "PNG", optimize=True)
    print(f"✓ Downloaded and processed: {output_path.name}")
    return output_path


async def _download_or_generate_slide(
    *,
    source_url: str,
    prompt: str,
    output_path: Path,
    api_key: str,
    model: str,
    base_url: str = "https://openrouter.ai/api/v1",
    resolution: tuple[int, int] = (VideoConstants.DEFAULT_WIDTH, VideoConstants.DEFAULT_HEIGHT),
) -> Path:
    """Try to download source image, fallback to AI generation on failure.

    Args:
        source_url: Image URL to download.
        prompt: Fallback prompt for AI generation.
        output_path: Path to save slide.
        api_key: OpenRouter API key.
        model: AI model identifier.

    Returns:
        Path to generated/downloaded slide.
    """
    try:
        return await download_and_process_image(
            url=source_url,
            output_path=output_path,
            target_width=resolution[0],
            target_height=resolution[1],
        )
    except (httpx.HTTPError, ValueError, Exception) as e:
        print(f"⚠ Failed to download image from {source_url}: {e}")
        print("  ⟳ Falling back to AI generation...")
        return await generate_slide(
            prompt=prompt,
            output_path=output_path,
            api_key=api_key,
            model=model,
            base_url=base_url,
            width=resolution[0],
            height=resolution[1],
        )


async def generate_slide(
    *,
    prompt: str,
    output_path: Path,
    api_key: str,
    # NOTE: DO NOT change this model. gemini-3-pro-image-preview is the correct model.
    # Do NOT use gemini-2.5-flash-image-preview or any other model.
    model: str = "google/gemini-3-pro-image-preview",
    base_url: str = "https://openrouter.ai/api/v1",
    width: int = VideoConstants.DEFAULT_WIDTH,
    height: int = VideoConstants.DEFAULT_HEIGHT,
    max_retries: int = RetryConfig.MAX_RETRIES,
    retry_delay: float = RetryConfig.INITIAL_DELAY,
) -> Path:
    """Generate a slide image from a prompt with retry logic.

    Args:
        prompt: Image generation prompt.
        output_path: Path to save generated image.
        api_key: OpenRouter API key.
        model: Image model identifier.
        base_url: API base URL.
        width: Image width in pixels.
        height: Image height in pixels.
        max_retries: Maximum number of retry attempts on failure.
        retry_delay: Initial delay between retries (exponential backoff).

    Returns:
        Path to generated image file.

    Raises:
        httpx.HTTPError: If API request fails after all retries.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if slide already exists and is not empty
    if skip_if_exists(output_path, "slide"):
        return output_path

    # Create prompt for slide generation
    # Simple, direct prompt to maximize image generation success
    full_prompt = f"""Generate an image: {prompt}

Style: Clean presentation slide, modern flat design, 16:9 aspect ratio."""

    last_error = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": full_prompt,
                            }
                        ],
                        "modalities": ["image", "text"],
                        "image_config": {
                            "aspect_ratio": "16:9",
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Extract image from response
                message = data["choices"][0]["message"]

                # Check for images in the response
                if "images" in message and len(message["images"]) > 0:
                    image_data = message["images"][0]
                    image_url = image_data["image_url"]["url"]

                    # Extract base64 data from data URL
                    if image_url.startswith("data:image"):
                        # Format: data:image/png;base64,<base64_data>
                        if "base64," in image_url:
                            b64_data = image_url.split("base64,")[1]
                            img_bytes = base64.b64decode(b64_data)
                            output_path.write_bytes(img_bytes)
                            print(f"✓ Generated slide: {output_path.name}")
                            return output_path

                # No image in response - treat as error
                error_msg = f"No image data in API response for '{prompt[:50]}...'"
                print(f"⚠ {error_msg}")
                # Debug: show response structure
                print(f"  Response keys: {list(data.keys())}")
                if "choices" in data and data["choices"]:
                    msg_keys = list(message.keys()) if message else []
                    print(f"  Message keys: {msg_keys}")
                    if "content" in message:
                        content = message["content"]
                        if isinstance(content, str):
                            print(f"  Content (text): {content[:200]}...")
                        elif isinstance(content, list):
                            print(f"  Content (list): {len(content)} items")
                            for idx, item in enumerate(content[:3]):
                                if isinstance(item, dict):
                                    print(
                                        f"    [{idx}] type={item.get('type')}, keys={list(item.keys())}"
                                    )
                last_error = ValueError(error_msg)

        except httpx.HTTPStatusError as e:
            last_error = e
            error_detail = ""
            try:
                error_detail = f"\n    Response: {e.response.text[:500]}"
            except (AttributeError, Exception):
                # response may not have text attribute or may fail to access
                pass
            print(f"⚠ HTTP error on attempt {attempt + 1}/{max_retries}: {e}{error_detail}")
        except httpx.HTTPError as e:
            last_error = e
            print(f"⚠ HTTP error on attempt {attempt + 1}/{max_retries}: {e}")
        except Exception as e:
            last_error = e
            print(f"⚠ Error on attempt {attempt + 1}/{max_retries}: {e}")

        # Retry with exponential backoff
        if attempt < max_retries - 1:
            delay = retry_delay * (RetryConfig.BACKOFF_FACTOR**attempt)
            print(f"  ⟳ Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)

    # All retries exhausted
    print(f"✗ Failed to generate slide after {max_retries} attempts: {output_path.name}")
    print(f"  Last error: {last_error}")
    # Create 0-byte placeholder to mark as failed
    output_path.write_bytes(b"")
    return output_path


async def generate_slides_for_sections(
    *,
    sections: Sequence[tuple[str, str] | tuple[str, str, str | None]],
    output_dir: Path,
    api_key: str,
    language: str = "ja",
    # NOTE: DO NOT change this model. gemini-3-pro-image-preview is the correct model.
    # Do NOT use gemini-2.5-flash-image-preview or any other model.
    model: str = "google/gemini-3-pro-image-preview",
    base_url: str = "https://openrouter.ai/api/v1",
    max_concurrent: int = 3,
    section_indices: list[int] | None = None,
    resolution: tuple[int, int] = (VideoConstants.DEFAULT_WIDTH, VideoConstants.DEFAULT_HEIGHT),
) -> list[Path]:
    """Generate slides for multiple script sections with concurrent processing.

    Args:
        sections: List of (title, prompt, source_image_url) tuples.
                  If source_image_url is provided, download and use that image.
                  Otherwise, generate using AI with the prompt.
        output_dir: Directory to save slide images.
        api_key: OpenRouter API key.
        language: Language code for organizing output (ja, en, etc.).
        model: Image model identifier.
        max_concurrent: Maximum number of concurrent API requests.
        section_indices: Optional list of original section indices for file naming.
                        If None, uses sequential indices 0, 1, 2, ...

    Returns:
        List of paths to generated slides.
    """
    # Create language-specific subdirectory
    lang_output_dir = output_dir / language
    lang_output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare all tasks
    slide_paths = []
    tasks_to_run = []
    task_indices = []

    print(f"\n📊 Preparing to generate {len(sections)} slides for language '{language}'...")

    for i, section_data in enumerate(sections):
        # Use custom index if provided, otherwise use sequential index
        file_index = section_indices[i] if section_indices else i

        # Support both old format (title, prompt) and new format (title, prompt, source_image_url)
        if len(section_data) == 2:
            title, prompt = section_data
            source_image_url = None
        else:
            title, prompt, source_image_url = section_data

        output_path = lang_output_dir / ProjectPaths.SLIDE_FILENAME_FORMAT.format(index=file_index)
        slide_paths.append(output_path)

        # Check if already exists
        if is_valid_file(output_path):
            print(f"⊙ Slide {i:02d}/{len(sections) - 1} already exists: {output_path.name}")
        else:
            # Decide whether to download image or generate with AI
            if source_image_url:
                print(f"→ Slide {i:02d}/{len(sections) - 1} queued (download): {title[:40]}...")
                # Create a task that tries download first, then falls back to generation if available
                if prompt:
                    # Fallback available
                    tasks_to_run.append(
                        _download_or_generate_slide(
                            source_url=source_image_url,
                            prompt=prompt,
                            output_path=output_path,
                            api_key=api_key,
                            model=model,
                            base_url=base_url,
                            resolution=resolution,
                        )
                    )
                else:
                    # No fallback, just download
                    tasks_to_run.append(
                        download_and_process_image(
                            url=source_image_url,
                            output_path=output_path,
                            target_width=resolution[0],
                            target_height=resolution[1],
                        )
                    )
            elif prompt:
                print(f"→ Slide {i:02d}/{len(sections) - 1} queued (generate): {title[:40]}...")
                tasks_to_run.append(
                    generate_slide(
                        prompt=prompt,
                        output_path=output_path,
                        api_key=api_key,
                        model=model,
                        base_url=base_url,
                        width=resolution[0],
                        height=resolution[1],
                    )
                )
            else:
                # Neither source image nor prompt available
                print(
                    f"⚠ Slide {i:02d}/{len(sections) - 1} has no image source or prompt, skipping"
                )
                continue

            task_indices.append(i)

    if not tasks_to_run:
        print("\n✓ All slides already exist, nothing to generate")
        return slide_paths

    # Execute tasks with concurrency limit
    print(
        f"\n🚀 Generating {len(tasks_to_run)} slides (max {max_concurrent} concurrent requests)...\n"
    )

    # Process in batches to limit concurrency
    results = []
    for batch_idx in range(0, len(tasks_to_run), max_concurrent):
        batch = tasks_to_run[batch_idx : batch_idx + max_concurrent]
        batch_task_indices = task_indices[batch_idx : batch_idx + max_concurrent]

        print(
            f"Processing batch {batch_idx // max_concurrent + 1}/{(len(tasks_to_run) + max_concurrent - 1) // max_concurrent}..."
        )
        batch_results = await asyncio.gather(*batch, return_exceptions=True)

        # Check for exceptions in batch
        for idx, result in zip(batch_task_indices, batch_results):
            if isinstance(result, Exception):
                print(f"✗ Error generating slide {idx:04d}: {result}")

        results.extend(batch_results)

        # Brief pause between batches to avoid rate limiting
        if batch_idx + max_concurrent < len(tasks_to_run):
            await asyncio.sleep(1.0)

    # Check results
    successful = sum(1 for path in slide_paths if path.exists() and path.stat().st_size > 0)
    failed = len(slide_paths) - successful

    print("\n📈 Slide generation complete:")
    print(f"  ✓ Successful: {successful}/{len(slide_paths)}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}/{len(slide_paths)}")
        print("\n💡 Tip: Delete failed (0-byte) slides and run again to retry only those.")

    return slide_paths
