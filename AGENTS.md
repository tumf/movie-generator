# AGENTS.md - AI Coding Agent Instructions

Instructions for AI coding assistants working in this repository.

## Project Overview

Movie Generator is a Python CLI tool that generates YouTube slide videos from blog URLs.
It fetches content, generates narration scripts with LLM, synthesizes audio with VOICEVOX,
creates slides, and renders videos using Remotion.

## Build/Test/Lint Commands

```bash
# Install with uv (recommended)
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/test_scene_range.py -v

# Run single test function
uv run pytest tests/test_scene_range.py::TestSceneRangeParsing::test_single_scene -v

# Run tests matching keyword
uv run pytest -k "scene" -v

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/
```

## Code Style Guidelines

### Python Version & Tools

- **Python**: 3.13+
- **Linter/Formatter**: Ruff (line-length: 100)
- **Type Checker**: mypy (strict mode)
- **Testing**: pytest

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `voicevox.py`, `remotion_renderer.py` |
| Classes | PascalCase | `VoicevoxSynthesizer`, `VideoScript` |
| Functions | snake_case | `parse_scene_range`, `create_composition` |
| Constants | SCREAMING_SNAKE_CASE | `VOICEVOX_AVAILABLE` |
| Variables | snake_case | `audio_paths`, `section_index` |

### Import Organization

```python
"""Module docstring."""

# 1. Standard library
import asyncio
from pathlib import Path

# 2. Third-party packages
import click
from pydantic import BaseModel

# 3. Local/project imports
from .config import Config
```

### Type Annotations

Always use type annotations for function signatures:

```python
def parse_scene_range(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range argument."""
    ...
```

### Documentation

Use Google-style docstrings for public functions:

```python
def split_into_phrases(text: str, max_chars: int = 50) -> list[Phrase]:
    """Split text into phrases.

    Args:
        text: Input text to split.
        max_chars: Maximum characters per phrase.

    Returns:
        List of Phrase objects.
    """
```

### Error Handling

- Raise `ValueError` for invalid inputs with descriptive messages
- Use `RuntimeError` for system/external failures
- Include context in error messages

## Critical Rules

### NEVER Use Low-Quality Fallbacks

When a primary approach fails:
- Do NOT silently degrade to a worse alternative
- Do NOT use placeholder values or dummy data
- Report the failure clearly and ask for guidance

### Pydantic Model Serialization

**ALWAYS use `model_dump()` to serialize Pydantic models.** Never manually construct dicts.

```python
narr_dict = n.model_dump(exclude_none=True)  # Good
narr_dict = {"text": n.text, "reading": n.reading}  # Bad
```

### LLM Prompt Management

The script generator has 4 prompt templates. When adding LLM output fields, update ALL:
- `SCRIPT_GENERATION_PROMPT_JA` (single-speaker, Japanese)
- `SCRIPT_GENERATION_PROMPT_EN` (single-speaker, English)
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` (multi-speaker, Japanese)
- `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` (multi-speaker, English)

### Subtitle Color Management

Use constants from `constants.py`, never hardcode colors:

```python
from ..constants import SubtitleConstants
color = SubtitleConstants.DEFAULT_COLOR  # Good
```

## Project Structure

```
src/movie_generator/
├── cli.py              # Main CLI entry point
├── config.py           # Pydantic configuration models
├── constants.py        # Shared constants
├── project.py          # Project management
├── assets/             # Logo and asset download/conversion
├── audio/              # Audio synthesis (VOICEVOX)
├── content/            # URL fetching and HTML parsing
├── script/             # Script generation and phrase splitting
├── slides/             # Slide image generation
└── video/              # Video rendering (Remotion)
```

### Key Concepts

- **Phrase**: Text segment with `section_index` and `original_index` (global ID for file naming)
- **Section**: Script section with title, narration, and slide prompt
- **Composition**: JSON data linking phrases, audio files, and slides for Remotion

## Environment Variables

```bash
export OPENROUTER_API_KEY="..."           # Required for LLM/slides
export VOICEVOX_DICT_DIR="..."            # VOICEVOX dictionary path
```

## Important Reminders

1. **Read before editing** - Always read existing files before modification
2. **Use `original_index`** - For file naming across filtered phrase lists
3. **Regenerate composition** - Always regenerate `composition.json` for scene ranges
4. **Test with scene ranges** - Verify `--scenes N`, `--scenes N-M`, `--scenes N-`
