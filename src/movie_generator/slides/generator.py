"""Slide image generation using OpenRouter API.

Generates presentation slides using image generation models.
"""

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
) -> Path:
    """Generate a slide image from a prompt.

    Args:
        prompt: Image generation prompt.
        output_path: Path to save generated image.
        api_key: OpenRouter API key.
        model: Image model identifier.
        base_url: API base URL.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        Path to generated image file.

    Raises:
        httpx.HTTPError: If API request fails.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

            # Fallback: create placeholder if no image in response
            print(f"Warning: No image data in response for '{prompt[:50]}...'")
            output_path.write_bytes(b"")
            return output_path

    except Exception as e:
        print(f"Error generating slide for '{prompt[:50]}...': {e}")
        # Create placeholder on error
        output_path.write_bytes(b"")
        return output_path


async def generate_slides_for_sections(
    sections: list[tuple[str, str]],
    output_dir: Path,
    api_key: str,
    model: str = "nonobananapro",
) -> list[Path]:
    """Generate slides for multiple script sections.

    Args:
        sections: List of (title, prompt) tuples.
        output_dir: Directory to save slide images.
        api_key: OpenRouter API key.
        model: Image model identifier.

    Returns:
        List of paths to generated slides.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    slide_paths: list[Path] = []

    for i, (title, prompt) in enumerate(sections):
        output_path = output_dir / f"slide_{i:04d}.png"

        # Skip if slide already exists
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"⊙ Slide already exists, skipping: {output_path.name}")
        else:
            await generate_slide(prompt, output_path, api_key, model)

        slide_paths.append(output_path)

    return slide_paths
