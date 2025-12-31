"""Tests for script generator."""

from movie_generator.script.generator import Narration, ScriptSection


def test_script_section_with_source_image_url():
    """Test ScriptSection with source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narrations=[Narration(text="This is a test narration.")],
        slide_prompt=None,
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert len(section.narrations) == 1
    assert section.narrations[0].text == "This is a test narration."
    assert section.slide_prompt is None
    assert section.source_image_url == "https://example.com/image.jpg"


def test_script_section_with_slide_prompt():
    """Test ScriptSection with slide_prompt."""
    section = ScriptSection(
        title="Test Section",
        narrations=[Narration(text="This is a test narration.")],
        slide_prompt="A beautiful landscape",
        source_image_url=None,
    )
    assert section.title == "Test Section"
    assert section.narrations[0].text == "This is a test narration."
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url is None


def test_script_section_with_both():
    """Test ScriptSection with both slide_prompt and source_image_url."""
    section = ScriptSection(
        title="Test Section",
        narrations=[Narration(text="This is a test narration.")],
        slide_prompt="A beautiful landscape",
        source_image_url="https://example.com/image.jpg",
    )
    assert section.title == "Test Section"
    assert section.slide_prompt == "A beautiful landscape"
    assert section.source_image_url == "https://example.com/image.jpg"


def test_script_section_with_multi_speaker():
    """Test ScriptSection with multiple narrations (multi-speaker)."""
    section = ScriptSection(
        title="Test Section",
        narrations=[
            Narration(text="Hello!", persona_id="alice"),
            Narration(text="Hi there!", persona_id="bob"),
            Narration(text="How are you?", persona_id="alice"),
        ],
        slide_prompt="A conversation between two people",
    )
    assert section.title == "Test Section"
    assert len(section.narrations) == 3
    assert section.narrations[0].persona_id == "alice"
    assert section.narrations[1].persona_id == "bob"
    assert section.narrations[2].persona_id == "alice"


def test_narration_without_persona():
    """Test Narration without persona_id (single speaker)."""
    narration = Narration(text="This is a single speaker narration.")
    assert narration.text == "This is a single speaker narration."
    assert narration.persona_id is None
