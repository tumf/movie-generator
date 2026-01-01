#!/usr/bin/env python3
"""Generate character animation assets from Zundamon PSD file."""

import sys
from pathlib import Path

from PIL import Image
from psd_tools import PSDImage


def set_layer_visibility(psd, layer_path, visible):
    """Set visibility of a layer by path.

    Args:
        psd: PSDImage object
        layer_path: List of layer names from root to target (e.g., ['!口', '*ほあー'])
        visible: Boolean visibility state
    """
    current = psd
    for name in layer_path:
        found = False
        for layer in current:
            if layer.name == name:
                current = layer
                found = True
                break
        if not found:
            print(f"Warning: Layer '{name}' not found in path {layer_path}")
            return False

    current.visible = visible
    return True


def hide_all_in_group(group):
    """Hide all layers in a group."""
    for layer in group:
        layer.visible = False
        if layer.is_group():
            hide_all_in_group(layer)


def find_group(psd, group_name):
    """Find a group by name."""
    for layer in psd:
        if layer.is_group() and layer.name == group_name:
            return layer
    return None


def generate_base_image(psd, output_path):
    """Generate base.png - neutral expression with closed mouth and open eyes.

    Visibility:
    - 口: ほあー (closed mouth)
    - 目: 普通目 (normal open eyes)
    - 眉: 普通眉 (normal eyebrows)
    """
    print("Generating base.png...")

    # Hide all mouth variants, show 'ほあー'
    mouth_group = find_group(psd, "!口")
    if mouth_group:
        hide_all_in_group(mouth_group)
        for layer in mouth_group:
            if layer.name == "*ほあー":
                layer.visible = True

    # Configure eyes - show normal eyes
    eye_group = find_group(psd, "!目")
    if eye_group:
        eye_group.visible = True  # Ensure parent group is visible
        hide_all_in_group(eye_group)
        eye_set = find_group(eye_group, "*目セット")
        if eye_set:
            eye_set.visible = True
            # Show white part of eyes
            for layer in eye_set:
                if layer.name == "*普通白目":
                    layer.visible = True
            # Show normal black pupil
            pupil_group = find_group(eye_set, "!黒目")
            if pupil_group:
                pupil_group.visible = True  # CRITICAL: Make pupil group visible!
                # Hide all pupil variants first
                for layer in pupil_group:
                    layer.visible = False
                # Show only normal pupil
                for layer in pupil_group:
                    if layer.name == "*普通目":
                        layer.visible = True

    # Configure eyebrows - show normal
    eyebrow_group = find_group(psd, "!眉")
    if eyebrow_group:
        hide_all_in_group(eyebrow_group)
        for layer in eyebrow_group:
            if layer.name == "*普通眉":
                layer.visible = True

    # Render and save with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    # Crop and resize to square
    image = crop_and_resize(image, 1024)
    image.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def generate_mouth_open_image(psd, output_path):
    """Generate mouth_open.png - speaking expression with open mouth.

    Visibility:
    - 口: お (open mouth for speech)
    - 目: 普通目 (same as base)
    - 眉: 普通眉 (same as base)
    """
    print("Generating mouth_open.png...")

    # Hide all mouth variants, show 'お' (open mouth)
    mouth_group = find_group(psd, "!口")
    if mouth_group:
        hide_all_in_group(mouth_group)
        for layer in mouth_group:
            if layer.name == "*お":
                layer.visible = True

    # Eyes and eyebrows same as base (already configured)

    # Render and save with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    image = crop_and_resize(image, 1024)
    image.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def generate_eye_close_image(psd, output_path):
    """Generate eye_close.png - blinking expression with closed eyes.

    Visibility:
    - 口: ほあー (same as base)
    - 目: にっこり (closed eyes)
    - 眉: 普通眉 (same as base)
    """
    print("Generating eye_close.png...")

    # Mouth same as base (already configured with ほあー)

    # Hide all eye variants, show 'にっこり' (closed/smiling eyes)
    eye_group = find_group(psd, "!目")
    if eye_group:
        hide_all_in_group(eye_group)
        for layer in eye_group:
            if layer.name == "*にっこり":
                layer.visible = True

    # Eyebrows same as base (already configured)

    # Render and save with transparency
    # Use force=True to get proper RGBA with transparency
    image = psd.composite(force=True)
    image = crop_and_resize(image, 1024)
    image.save(output_path, "PNG")
    print(f"  Saved: {output_path}")


def crop_and_resize(image, target_size):
    """Crop image to square and resize to target size.

    Args:
        image: PIL Image (should already be RGBA from composite(force=True))
        target_size: Target width/height in pixels

    Returns:
        Resized square PIL Image with transparency
    """
    # Ensure RGBA mode
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    width, height = image.size

    # Calculate crop box for center square
    if width > height:
        # Landscape - crop width
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        # Portrait - crop height from bottom to keep head
        left = 0
        top = 0
        right = width
        bottom = width

    # Crop to square
    image = image.crop((left, top, right, bottom))

    # Resize to target size with high-quality resampling
    image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

    return image


def main():
    psd_path = Path("assets/ずんだもん立ち絵素材2.3.psd")
    output_dir = Path("assets/characters/zundamon")

    if not psd_path.exists():
        print(f"Error: PSD file not found: {psd_path}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading PSD: {psd_path}")
    psd = PSDImage.open(psd_path)

    print(f"PSD size: {psd.width}x{psd.height}")
    print(f"Output directory: {output_dir}")
    print()

    # Generate three asset variants
    generate_base_image(psd, output_dir / "base.png")
    generate_mouth_open_image(psd, output_dir / "mouth_open.png")
    generate_eye_close_image(psd, output_dir / "eye_close.png")

    print()
    print("✅ Asset generation complete!")
    print(f"   Output: {output_dir}")
    print()
    print("Next steps:")
    print("1. Verify assets look correct")
    print("2. Configure in config YAML:")
    print("   personas:")
    print("     - id: zundamon")
    print("       character_image: assets/characters/zundamon/base.png")
    print("       mouth_open_image: assets/characters/zundamon/mouth_open.png")
    print("       eye_close_image: assets/characters/zundamon/eye_close.png")


if __name__ == "__main__":
    main()
