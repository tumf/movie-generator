# Project Context

## Purpose

Movie Generator - A Python CLI tool that generates YouTube slide videos from blog URLs.

Key features:
- Automatic YouTube script generation from blog articles
- Narration via VOICEVOX audio synthesis
- Phrase-based accurate subtitle synchronization
- Unified styling via YAML configuration

## Tech Stack

- **Language**: Python 3.13
- **Package Manager**: uv
- **Audio**: VOICEVOX Core
- **Video**: ffmpeg / Remotion
- **LLM**: OpenRouter (Gemini, etc.)
- **CLI**: typer + rich

## Project Conventions

### Code Style

- Black + Ruff for formatting/linting
- Type hints required (mypy strict)
- Docstrings in Google style

### Architecture Patterns

- Modular pipeline design
- Pydantic for configuration validation
- Dependency injection for testability

### Testing Strategy

- pytest for unit/integration tests
- Mocks for external APIs (VOICEVOX, LLM)
- E2E tests with sample content

### Git Workflow

- Conventional commits (feat, fix, docs, etc.)
- Feature branches: `feature/<change-id>`

## Domain Context

### Video Generation Pipeline

```
URL → Content → Script → Phrases → Audio → Slides → Video
```

### Key Concepts

- **Phrase**: Narration segment of 3-6 seconds
- **Pronunciation Dictionary**: Dictionary for proper noun readings
- **Scene**: Combination of slide + audio + subtitles

## Important Constraints

- VOICEVOX environment dependent (Open JTalk dictionary, voice models)
- macOS/Linux prioritized (Windows support is best effort)
- Japanese content only

## External Dependencies

- VOICEVOX Core: https://voicevox.hiroshiba.jp/
- OpenRouter API: https://openrouter.ai/
- ffmpeg: System installation required
