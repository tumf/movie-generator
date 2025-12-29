"""Slide image generation using OpenRouter API.

Generates presentation slides using image generation models.
"""

import asyncio
import base64
from pathlib import Path

import httpx


async def generate_slide(
    prompt: str,
    output_path: Path,
    api_key: str,
    model: str = "google/gemini-3-pro-image-preview",
    base_url: str = "https://openrouter.ai/api/v1",
    width: int = 1920,
    height: int = 1080,
    max_retries: int = 3,
    retry_delay: float = 2.0,
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
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"  ↷ Skipping existing slide: {output_path.name}")
        return output_path

    # Create prompt for slide generation
    full_prompt = f"""Create a professional presentation slide image for YouTube video.

Topic: {prompt}

Style requirements:
- Clean, modern design
- Readable text with good contrast
- Professional aesthetic suitable for educational content
- Visual elements that support the topic
- 16:9 aspect ratio
- High quality, polished look"""

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
                            "image_size": "2K",
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
    sections: list[tuple[str, str]],
    output_dir: Path,
    api_key: str,
    model: str = "google/gemini-3-pro-image-preview",
    max_concurrent: int = 3,
) -> list[Path]:
    """Generate slides for multiple script sections with concurrent processing.

    Args:
        sections: List of (title, prompt) tuples.
        output_dir: Directory to save slide images.
        api_key: OpenRouter API key.
        model: Image model identifier.
        max_concurrent: Maximum number of concurrent API requests.

    Returns:
        List of paths to generated slides.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare all tasks
    tasks = []
    slide_paths = []

    print(f"\n📊 Preparing to generate {len(sections)} slides...")

    for i, (title, prompt) in enumerate(sections):
        output_path = output_dir / f"slide_{i:04d}.png"
        slide_paths.append(output_path)

        # Check if already exists
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"⊙ Slide {i:02d}/{len(sections) - 1} already exists: {output_path.name}")

            # Create a dummy coroutine that returns the path
            async def skip_existing(path=output_path):
                return path

            tasks.append(skip_existing())
        else:
            print(f"→ Slide {i:02d}/{len(sections) - 1} queued: {title[:50]}...")
            tasks.append(generate_slide(prompt, output_path, api_key, model))

    # Execute tasks with concurrency limit
    print(f"\n🚀 Generating slides (max {max_concurrent} concurrent requests)...\n")

    # Process in batches to limit concurrency
    results = []
    for i in range(0, len(tasks), max_concurrent):
        batch = tasks[i : i + max_concurrent]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        results.extend(batch_results)

        # Brief pause between batches to avoid rate limiting
        if i + max_concurrent < len(tasks):
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
