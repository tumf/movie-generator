"""Convert SVG logos to PNG format."""

import shutil
import subprocess
from pathlib import Path


def convert_svg_to_png(svg_path: Path, png_path: Path, width: int = 512) -> Path:
    """Convert SVG file to PNG format.

    Tries multiple conversion methods in order of preference:
    1. cairosvg (if available)
    2. ImageMagick (magick or convert)
    3. Fallback to original SVG

    Args:
        svg_path: Path to the source SVG file.
        png_path: Path to save the converted PNG file.
        width: Target width in pixels (height is auto-scaled to maintain aspect ratio).

    Returns:
        Path to the converted PNG file.

    Raises:
        Exception: If conversion fails.
    """
    png_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  ⟳ Converting SVG to PNG: {svg_path.name}")

    # Method 1: Try cairosvg first (if available)
    try:
        import cairosvg

        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
        )
        print(f"  ✓ Converted with cairosvg: {png_path.name}")
        return png_path
    except (ImportError, OSError) as e:
        print(f"  ⚠ cairosvg not available: {e}")

    # Method 2: Try ImageMagick
    magick_cmd = shutil.which("magick") or shutil.which("convert")
    if magick_cmd:
        try:
            cmd = [
                magick_cmd,
                str(svg_path),
                "-resize",
                f"{width}x{width}",
                str(png_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if png_path.exists() and png_path.stat().st_size > 0:
                print(f"  ✓ Converted with ImageMagick: {png_path.name}")
                return png_path
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ ImageMagick conversion failed: {e.stderr}")

    # All methods failed
    error_msg = "SVG conversion failed: No converter available (cairosvg or ImageMagick)"
    print(f"✗ {error_msg}")
    print(f"  → Keeping original SVG file: {svg_path}")
    print(f"  💡 Tip: Install ImageMagick (brew install imagemagick) or use a PNG logo URL")
    raise RuntimeError(error_msg)
