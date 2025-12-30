"""Logo asset download functionality for slide generation."""

from pathlib import Path

from ..assets.downloader import download_logo, sanitize_filename
from ..script.generator import LogoAsset

# Conditional import for converter
try:
    from ..assets.converter import convert_svg_to_png

    _CONVERTER_AVAILABLE = True
except (ImportError, OSError):
    _CONVERTER_AVAILABLE = False


async def download_logo_assets(
    *,
    logo_assets: list[LogoAsset],
    logos_dir: Path,
) -> dict[str, Path]:
    """Download logo assets from URLs.

    Args:
        logo_assets: List of logo assets with name and URL.
        logos_dir: Directory to save downloaded logos.

    Returns:
        Dictionary mapping logo names to their local file paths.
    """
    if not logo_assets:
        return {}

    print(f"\n🖼️  Downloading {len(logo_assets)} logo asset(s)...")

    logo_paths: dict[str, Path] = {}

    for logo in logo_assets:
        name = logo.name
        url = logo.url
        sanitized_name = sanitize_filename(name)

        # Determine file extension from URL
        url_lower = url.lower()
        is_svg = url_lower.endswith(".svg") or "svg" in url_lower

        # Download to temporary location first
        if is_svg:
            temp_path = logos_dir / f"{sanitized_name}.svg"
            final_path = logos_dir / f"{sanitized_name}.png"
        else:
            # Assume PNG/JPG
            ext = ".png" if ".png" in url_lower else ".jpg"
            temp_path = logos_dir / f"{sanitized_name}{ext}"
            final_path = temp_path

        try:
            # Download logo
            await download_logo(url=url, output_path=temp_path)

            # Convert SVG to PNG if needed
            if is_svg and temp_path.exists():
                if _CONVERTER_AVAILABLE:
                    try:
                        convert_svg_to_png(temp_path, final_path)
                        # Remove original SVG after successful conversion
                        temp_path.unlink()
                    except Exception as e:
                        print(f"⚠ SVG conversion failed for {name}: {e}")
                        print(f"  → Using original SVG file (may not work for slide generation)")
                        final_path = temp_path
                else:
                    print(f"⚠ SVG converter not available (cairo library missing) for {name}")
                    print(f"  → Using original SVG file (may not work for slide generation)")
                    final_path = temp_path

            logo_paths[name] = final_path

        except Exception as e:
            print(f"⚠ Failed to download logo '{name}' from {url}: {e}")
            print(f"  → Continuing without this logo")
            continue

    print(f"✓ Downloaded {len(logo_paths)}/{len(logo_assets)} logo(s)\n")
    return logo_paths


def prepare_logo_images_for_multimodal(logo_paths: dict[str, Path]) -> list[str]:
    """Prepare logo images for multimodal LLM input.

    Args:
        logo_paths: Dictionary mapping logo names to their file paths.

    Returns:
        List of base64-encoded data URLs for logo images.
    """
    logo_images = []

    for name, path in logo_paths.items():
        try:
            encoded = encode_logo_to_base64(path)
            logo_images.append(encoded)
            print(f"  ✓ Encoded logo for multimodal input: {name}")
        except Exception as e:
            print(f"  ⚠ Failed to encode logo '{name}': {e}")
            continue

    return logo_images


def encode_logo_to_base64(logo_path: Path) -> str:
    """Encode logo image to base64 data URL.

    Args:
        logo_path: Path to the logo image file.

    Returns:
        Base64-encoded data URL (e.g., "data:image/png;base64,...").
    """
    import base64

    # Determine MIME type from extension
    ext = logo_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }.get(ext, "image/png")

    # Read and encode image
    image_bytes = logo_path.read_bytes()
    b64_data = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:{mime_type};base64,{b64_data}"


def create_logo_context(logo_names: list[str]) -> str:
    """Create context string about available logos for slide generation prompt.

    Args:
        logo_names: List of logo names (products/companies).

    Returns:
        Context string to append to slide generation prompt.
    """
    if not logo_names:
        return ""

    logos_list = ", ".join(logo_names)
    return (
        f"Available logos: {logos_list}. Include relevant logos appropriately in the slide design."
    )
