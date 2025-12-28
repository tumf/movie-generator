# Project Context

## Purpose

Movie Generator - ブログURLからYouTube向けスライド動画を一括生成するPythonツール。

主な機能:
- ブログ記事からYouTube台本を自動生成
- VOICEVOX音声合成によるナレーション
- フレーズベースの正確な字幕同期
- YAML設定によるスタイル統一

## Tech Stack

- **Language**: Python 3.13
- **Package Manager**: uv
- **Audio**: VOICEVOX Core
- **Video**: ffmpeg / Remotion
- **LLM**: OpenRouter (Gemini等)
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

- **Phrase**: 3-6秒単位のナレーションセグメント
- **Pronunciation Dictionary**: 固有名詞の読み方辞書
- **Scene**: スライド+音声+字幕の組み合わせ

## Important Constraints

- VOICEVOX環境依存（Open JTalk辞書、音声モデル）
- macOS/Linux優先（Windows対応はベストエフォート）
- 日本語コンテンツのみ対応

## External Dependencies

- VOICEVOX Core: https://voicevox.hiroshiba.jp/
- OpenRouter API: https://openrouter.ai/
- ffmpeg: システムインストール必須
