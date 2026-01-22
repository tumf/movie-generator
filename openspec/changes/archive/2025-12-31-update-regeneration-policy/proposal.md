# Change: Update File Regeneration Policy

## Why

Currently, the `movie-generator generate` command applies a "skip if file exists" policy to all files. However, `composition.json` and video files must be regenerated every time to reflect configuration changes (especially transition settings). On the other hand, scripts, audio, and slides should skip regeneration when existing files are present due to high API call costs.

## What Changes

- composition.json generation: Remove existing file check and **always regenerate**
- Video rendering: Remove existing file check and **always re-render**
- Scripts, audio, slides: Skip if existing files are present (**maintain current behavior**)

Specific changes:
1. `cli.py`: Remove composition.json existence check → skip logic
2. `cli.py`: Remove video existence check → skip logic
3. `remotion_renderer.py`: Remove existence check → return logic in `render_video_with_remotion()`

## Impact

- Affected specification: `specs/video-generation/spec.md`
- Affected code:
  - `src/movie_generator/cli.py:521-542`
  - `src/movie_generator/video/remotion_renderer.py:219-221`
- User impact:
  - When re-running video generation command, video is always regenerated with latest configuration
  - Rendering time occurs every time (approximately 2-3 minutes)
  - Configuration changes (transitions, etc.) are reliably reflected
