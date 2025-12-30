"""Slide image generation using OpenRouter API.

Generates presentation slides using image generation models.
"""

import asyncio
import base64
from pathlib import Path

import httpx


async def generate_slide(
    *,
    prompt: str,
    output_path: Path,
    api_key: str,
    # NOTE: DO NOT change this model. gemini-3-pro-image-preview is the correct model.
    # Do NOT use gemini-2.5-flash-image-preview or any other model.
    model: str = "google/gemini-3-pro-image-preview",
    base_url: str = "https://openrouter.ai/api/v1",
    width: int = 1920,
    height: int = 1080,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    logo_context: str | None = None,
    logo_images: list[str] | None = None,
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
        logo_context: Optional context about available logos to include in prompt.
        logo_images: Optional list of base64-encoded logo images for multimodal input.

    Returns:
        Path to generated image file.

    Raises:
        httpx.HTTPError: If API request fails after all retries.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if slide already exists and is not empty
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"  ↷ Skipping existing slide: {output_path.name}")
        return output_path

    # Create prompt for slide generation
    # Simple, direct prompt to maximize image generation success
    text_prompt = f"""Generate an image: {prompt}

Style: Clean presentation slide, modern flat design, 16:9 aspect ratio."""

    # Add logo context if available
    if logo_context:
        text_prompt += f"\n\n{logo_context}"

    # Build multimodal content if logos are provided
    if logo_images:
        # Multimodal content: text + logo images
        content_parts = [{"type": "text", "text": text_prompt}]

        for logo_data_url in logo_images:
            content_parts.append({"type": "image_url", "image_url": {"url": logo_data_url}})

        message_content = content_parts
    else:
        # Text-only content
        message_content = text_prompt

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
                                "content": message_content,
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
            except:
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
            delay = retry_delay * (2**attempt)
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
    sections: list[tuple[str, str]],
    output_dir: Path,
    api_key: str,
    language: str = "ja",
    # NOTE: DO NOT change this model. gemini-3-pro-image-preview is the correct model.
    # Do NOT use gemini-2.5-flash-image-preview or any other model.
    model: str = "google/gemini-3-pro-image-preview",
    max_concurrent: int = 3,
    start_index: int = 0,
    logo_context: str | None = None,
    logo_images: list[str] | None = None,
) -> list[Path]:
    """Generate slides for multiple script sections with concurrent processing.

    Args:
        sections: List of (title, prompt) tuples.
        output_dir: Directory to save slide images.
        api_key: OpenRouter API key.
        language: Language code for organizing output (ja, en, etc.).
        model: Image model identifier.
        max_concurrent: Maximum number of concurrent API requests.
        start_index: Starting section index for file naming (useful for scene ranges).
        logo_context: Optional context about available logos to include in prompts.
        logo_images: Optional list of base64-encoded logo images for multimodal input.

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

    for i, (title, prompt) in enumerate(sections):
        # Use start_index to generate correct file names for scene ranges
        section_idx = start_index + i
        output_path = lang_output_dir / f"slide_{section_idx:04d}.png"
        slide_paths.append(output_path)

        # Check if already exists
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"⊙ Slide {section_idx:02d} already exists: {output_path.name}")
        else:
            print(f"→ Slide {section_idx:02d} queued: {title[:50]}...")
            tasks_to_run.append(
                generate_slide(
                    prompt=prompt,
                    output_path=output_path,
                    api_key=api_key,
                    model=model,
                    logo_context=logo_context,
                    logo_images=logo_images,
                )
            )
            task_indices.append(section_idx)

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

    print(f"\n📈 Slide generation complete:")
    print(f"  ✓ Successful: {successful}/{len(slide_paths)}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}/{len(slide_paths)}")
        print(f"\n💡 Tip: Delete failed (0-byte) slides and run again to retry only those.")

    return slide_paths


async def download_image_as_slide(url: str, output_path: Path) -> Path:
    """Download an image from URL and save as slide.

    Args:
        url: URL of the image to download.
        output_path: Path to save the downloaded image.

    Returns:
        Path to the saved image file.

    Raises:
        httpx.HTTPError: If download fails.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if already exists
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"  ↷ Skipping existing slide: {output_path.name}")
        return output_path

    print(f"  ↓ Downloading image: {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

        # Save the image
        output_path.write_bytes(response.content)
        print(f"  ✓ Downloaded: {output_path.name} ({len(response.content)} bytes)")

    return output_path
