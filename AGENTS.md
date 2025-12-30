# AGENTS.md - AI Coding Agent Instructions

Instructions for AI coding assistants working in this repository.

## Project Overview

Movie Generator is a Python CLI tool that generates YouTube slide videos from blog URLs.
It fetches content, generates narration scripts with LLM, synthesizes audio with VOICEVOX,
creates slides, and renders videos using Remotion.

## Quick Reference

### Build/Test/Lint Commands

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

# Run CLI
uv run movie-generator generate <script.yaml> --scenes 1-3
```

### Environment Variables

```bash
export OPENROUTER_API_KEY="..."           # Required for LLM/slides
export VOICEVOX_DICT_DIR="..."            # VOICEVOX dictionary path
export VOICEVOX_MODEL_PATH="..."          # VOICEVOX model path
export VOICEVOX_ONNXRUNTIME_PATH="..."    # VOICEVOX ONNX runtime path
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
import yaml
from pydantic import BaseModel
from rich.console import Console

# 3. Local/project imports
from .audio.voicevox import create_synthesizer_from_config
from .config import Config, load_config
```

### Type Annotations

Always use type annotations for function signatures:

```python
def parse_scene_range(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range argument."""
    ...

def create_composition(
    title: str,
    phrases: list[Phrase],
    slide_paths: list[Path],
    fps: int = 30,
) -> CompositionData:
    ...
```

### Data Classes

Use `@dataclass` for simple data containers:

```python
@dataclass
class Phrase:
    """A single phrase with timing information."""
    text: str
    duration: float = 0.0
    section_index: int = 0
    original_index: int = 0  # Global index for file naming
```

### Error Handling

- Raise `ValueError` for invalid inputs with descriptive messages
- Use `RuntimeError` for system/external failures
- Include context in error messages

```python
if start > end:
    raise ValueError(
        f"Invalid scene range: start ({start}) > end ({end})"
    )
```

### Documentation

- Module docstring at top of each file
- Google-style docstrings for public functions
- Type hints serve as primary documentation

```python
def split_into_phrases(text: str, max_chars: int = 50) -> list[Phrase]:
    """Split text into phrases based on punctuation and length.

    Args:
        text: Input text to split.
        max_chars: Maximum characters per phrase.

    Returns:
        List of Phrase objects.
    """
```

## Project Structure

```
src/movie_generator/
├── cli.py              # Main CLI entry point
├── config.py           # Pydantic configuration models
├── project.py          # Project management
├── audio/              # Audio synthesis (VOICEVOX)
├── content/            # URL fetching and HTML parsing
├── script/             # Script generation and phrase splitting
├── slides/             # Slide image generation
└── video/              # Video rendering (Remotion)
```

### Key Concepts

- **Phrase**: Text segment with `section_index` (which section) and `original_index` (global ID)
- **Section**: A script section with title, narration, and slide prompt
- **Composition**: JSON data linking phrases, audio files, and slides for Remotion

## Testing

### Test Structure

```python
class TestSceneRangeParsing:
    """Test scene range parsing function."""

    def test_single_scene(self) -> None:
        """Test parsing single scene number."""
        start, end = parse_scene_range("2")
        assert start == 1  # 0-based
        assert end == 1
```

### Test Naming

- Files: `test_<module>.py`
- Classes: `Test<Feature>`
- Functions: `test_<behavior>` or `test_<input>_<expected>`

## Git Workflow

### Commit Messages (Conventional Commits)

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat(cli): add --scenes option for scene range filtering`
- `fix(video): always regenerate composition for scene range accuracy`

<!-- OPENSPEC:START -->
# OpenSpec Instructions

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts

<!-- OPENSPEC:END -->

## Important Reminders

1. **Read before editing** - Always read existing files before modification
2. **Use `original_index`** - For file naming across filtered phrase lists
3. **Use `section_index`** - For mapping phrases to slides
4. **Regenerate composition** - Always regenerate `composition.json` for scene ranges
5. **Test with scene ranges** - Verify `--scenes N`, `--scenes N-M`, `--scenes N-`
