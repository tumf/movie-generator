# Change: Python Script for Batch Slide Video Generation from Blog URLs

## Why

We want to automate the workflow for generating slide videos for YouTube from blog post URLs.
The current experimental setup at `/Users/tumf/work/study/daihon` performs phrase segmentation, audio generation, and Remotion video composition manually.
This change integrates these processes into a unified Python script to create a reusable tool.

## What Changes

- **New**: Python 3.13 + uv project structure
- **New**: YAML-based configuration management (unified style, audio settings, output settings)
- **New**: URL content extraction → script generation pipeline
- **New**: VOICEVOX speech synthesis integration
- **New**: Phrase-based subtitle and audio synchronization system
- **New**: Video rendering with Remotion/ffmpeg

## Impact

- Affected specs: `video-generation`, `config-management` (new capabilities)
- Affected code: Entire project (new construction)
- Dependencies:
  - Python 3.13 (managed by uv)
  - VOICEVOX Core
  - Remotion or ffmpeg (video composition)
  - OpenRouter/LLM API (content generation)

## References

Experimental environment: Outputs from `/Users/tumf/work/study/daihon/`
- `scripts/phrase_based_script.py`: Phrase data management
- `voicevox/generate_phrases.py`: Audio generation
- `tui-video/src/VideoPhrases.tsx`: Remotion component
- `docs/PROJECT_SUMMARY.md`: Overall production workflow
