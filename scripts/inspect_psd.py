#!/usr/bin/env python3
"""Inspect PSD file structure to understand layer organization."""

from psd_tools import PSDImage


def print_layer_tree(layer, indent=0):
    """Print layer tree structure."""
    prefix = "  " * indent
    layer_type = "Group" if layer.is_group() else "Layer"
    visible = "👁️ " if layer.visible else "🔒"
    print(f"{prefix}{visible}{layer_type}: {layer.name}")

    if layer.is_group():
        for child in layer:
            print_layer_tree(child, indent + 1)


def main():
    psd_path = "assets/ずんだもん立ち絵素材2.3.psd"

    print(f"Loading PSD: {psd_path}")
    psd = PSDImage.open(psd_path)

    print("\nPSD Info:")
    print(f"  Size: {psd.width}x{psd.height}")
    print(f"  Channels: {psd.channels}")
    print(f"  Depth: {psd.depth}")
    print("\nLayer Structure:")

    for layer in psd:
        print_layer_tree(layer)


if __name__ == "__main__":
    main()
