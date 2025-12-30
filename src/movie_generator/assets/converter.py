"""Convert SVG logos to PNG format."""

from pathlib import Path

import cairosvg


def convert_svg_to_png(svg_path: Path, png_path: Path, width: int = 512) -> Path:
    """Convert SVG file to PNG format.

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

    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
        )
        print(f"  ✓ Converted: {png_path.name}")
        return png_path

    except Exception as e:
        print(f"✗ SVG conversion failed: {e}")
        print(f"  → Keeping original SVG file: {svg_path}")
        print(f"  💡 Tip: Use a PNG logo URL instead, or convert manually.")
        raise
