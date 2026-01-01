#!/usr/bin/env python3
"""Generate Shikoku Metan character assets for Movie Generator.

This script generates three PNG images from the Shikoku Metan PSD file:
- base.png: Eyes open, mouth closed (default state)
- mouth_open.png: Eyes open, mouth open (for lip sync)
- eye_close.png: Eyes closed, mouth closed (for blinking)

Output directory: assets/characters/shikoku-metan/
"""

from pathlib import Path

from psd_tools import PSDImage


def set_layer_visibility(psd, layer_path, visible):
    """Set visibility of a layer by path.

    Args:
        psd: PSDImage object.
        layer_path: List of layer names from root to target.
        visible: Boolean visibility state.
    """
    current = psd
    for i, name in enumerate(layer_path):
        # Find layer by name
        found = False
        for layer in current:
            if layer.name == name:
                # If this is the target layer, set visibility
                if i == len(layer_path) - 1:
                    layer.visible = visible
                    return
                # Otherwise, traverse into group
                if layer.is_group():
                    current = layer
                    found = True
                    break
        if not found and i < len(layer_path) - 1:
            raise ValueError(f"Layer path not found: {layer_path[: i + 1]}")


def generate_base(psd_path: Path, output_path: Path):
    """Generate base.png with eyes open, mouth closed.

    Default visible layers:
    - !目 > *目セット > !黒目 > *カメラ目線
    - !口 > *ほほえみ (closed mouth)
    """
    psd = PSDImage.open(psd_path)

    # Ensure target mouth is visible (closed mouth)
    # Default visible mouth is *わあー (open), so switch to *ほほえみ
    set_layer_visibility(psd, ["!口", "*わあー"], False)
    set_layer_visibility(psd, ["!口", "*ほほえみ"], True)

    # Ensure eyes are open (default state is already open)
    # !目 > *目セット > !黒目 > *カメラ目線 is already visible

    # Export merged image with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    image.save(output_path, "PNG")
    print(f"✅ Generated: {output_path}")


def generate_mouth_open(psd_path: Path, output_path: Path):
    """Generate mouth_open.png with eyes open, mouth open.

    Visible layers:
    - !目 > *目セット > !黒目 > *カメラ目線 (same as base)
    - !口 > *わあー (open mouth)
    """
    psd = PSDImage.open(psd_path)

    # Set mouth to open state
    set_layer_visibility(psd, ["!口", "*ほほえみ"], False)
    set_layer_visibility(psd, ["!口", "*わあー"], True)

    # Eyes remain open (default)

    # Export merged image with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    image.save(output_path, "PNG")
    print(f"✅ Generated: {output_path}")


def generate_eye_close(psd_path: Path, output_path: Path):
    """Generate eye_close.png with eyes closed, mouth closed.

    Visible layers:
    - !目 > *目閉じ (closed eyes)
    - !口 > *ほほえみ (closed mouth, same as base)
    """
    psd = PSDImage.open(psd_path)

    # Set mouth to closed state
    set_layer_visibility(psd, ["!口", "*わあー"], False)
    set_layer_visibility(psd, ["!口", "*ほほえみ"], True)

    # Set eyes to closed state
    # First, hide the default eye set
    set_layer_visibility(psd, ["!目", "*目セット"], False)
    # Then show the closed eyes layer
    set_layer_visibility(psd, ["!目", "*目閉じ"], True)

    # Export merged image with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    image.save(output_path, "PNG")
    print(f"✅ Generated: {output_path}")


def main():
    # Input PSD file
    psd_path = Path("assets/四国めたん立ち絵素材2.1.psd")

    if not psd_path.exists():
        print(f"❌ Error: PSD file not found: {psd_path}")
        print(f"   Please ensure the file exists at: {psd_path.absolute()}")
        return

    # Output directory
    output_dir = Path("assets/characters/shikoku-metan")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🎨 Generating Shikoku Metan character assets...")
    print(f"📁 Input:  {psd_path}")
    print(f"📁 Output: {output_dir}/")
    print()

    # Generate all variants
    generate_base(psd_path, output_dir / "base.png")
    generate_mouth_open(psd_path, output_dir / "mouth_open.png")
    generate_eye_close(psd_path, output_dir / "eye_close.png")

    print()
    print("🎉 All assets generated successfully!")
    print()
    print("📋 Generated files:")
    for filename in ["base.png", "mouth_open.png", "eye_close.png"]:
        filepath = output_dir / filename
        size_kb = filepath.stat().st_size / 1024
        print(f"   {filename:20s} ({size_kb:6.1f} KB)")


if __name__ == "__main__":
    main()
