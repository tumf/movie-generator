"""Tests for script generator."""

import pytest

from movie_generator.script.generator import ScriptSection


def test_script_section_with_source_image_url():
    """Test ScriptSection with source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narration="This is a test narration.",
        slide_prompt=None,
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert section.narration == "This is a test narration."
    assert section.slide_prompt is None
    assert section.source_image_url == "https://example.com/image.jpg"


def test_script_section_with_slide_prompt():
    """Test ScriptSection with slide_prompt."""
    section = ScriptSection(
        title="Test Section",
        narration="This is a test narration.",
        slide_prompt="A beautiful landscape",
        source_image_url=None,
    )
    assert section.title == "Test Section"
    assert section.narration == "This is a test narration."
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url is None


def test_script_section_with_both():
    """Test ScriptSection with both slide_prompt and source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narration="This is a test narration.",
        slide_prompt="A beautiful landscape",
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url == "https://example.com/image.jpg"
