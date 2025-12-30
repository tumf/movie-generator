"""Logo asset download functionality for slide generation."""

from pathlib import Path

from ..assets.converter import convert_svg_to_png
from ..assets.downloader import download_logo, sanitize_filename
from ..script.generator import LogoAsset


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
                try:
                    convert_svg_to_png(temp_path, final_path)
                    # Remove original SVG after successful conversion
                    temp_path.unlink()
                except Exception as e:
                    print(f"⚠ SVG conversion failed for {name}: {e}")
                    print(f"  → Using original SVG file (may not work for slide generation)")
                    final_path = temp_path

            logo_paths[name] = final_path

        except Exception as e:
            print(f"⚠ Failed to download logo '{name}' from {url}: {e}")
            print(f"  → Continuing without this logo")
            continue

    print(f"✓ Downloaded {len(logo_paths)}/{len(logo_assets)} logo(s)\n")
    return logo_paths
