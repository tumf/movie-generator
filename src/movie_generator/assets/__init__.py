"""Asset management for logos and images.

This module handles downloading and converting product/company logos
for use in slide generation.
"""

from .downloader import download_logo, sanitize_filename

__all__ = ["download_logo", "sanitize_filename"]

# Conditional import for converter (requires cairo system library)
try:
    from .converter import convert_svg_to_png

    __all__.append("convert_svg_to_png")
except (ImportError, OSError):
    # cairo library not installed, converter will not be available
    pass
