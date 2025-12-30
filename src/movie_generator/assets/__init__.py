"""Asset management for logos and images.

This module handles downloading and converting product/company logos
for use in slide generation.
"""

from .converter import convert_svg_to_png
from .downloader import download_logo, sanitize_filename

__all__ = ["download_logo", "sanitize_filename", "convert_svg_to_png"]
