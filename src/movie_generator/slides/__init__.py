"""Slide generation module."""

from .core import generate_slides_for_script
from .generator import generate_slide, generate_slides_for_sections

__all__ = ["generate_slide", "generate_slides_for_sections", "generate_slides_for_script"]
