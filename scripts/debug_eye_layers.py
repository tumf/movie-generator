#!/usr/bin/env python3
"""Debug eye layer visibility in Zundamon PSD."""

from psd_tools import PSDImage


def print_eye_layers(psd):
    """Print eye layer visibility."""
    for layer in psd:
        if layer.name == "!目":
            print("=== Eye Group (!目) ===")
            print_layer_tree(layer, 0)
            return


def print_layer_tree(layer, indent=0):
    """Print layer tree with visibility."""
    prefix = "  " * indent
    visible = "👁️ " if layer.visible else "🔒"
    layer_type = "Group" if layer.is_group() else "Layer"
    print(f"{prefix}{visible}{layer_type}: {layer.name}")

    if layer.is_group():
        for child in layer:
            print_layer_tree(child, indent + 1)


def main():
    psd = PSDImage.open("assets/ずんだもん立ち絵素材2.3.psd")
    print("Current eye layer visibility:")
    print_eye_layers(psd)


if __name__ == "__main__":
    main()
