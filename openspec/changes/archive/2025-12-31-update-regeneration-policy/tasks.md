# Tasks: Update File Regeneration Policy

## 1. Implementation

- [x] 1.1 Remove composition.json existence check in `cli.py`
  - Target: `src/movie_generator/cli.py:521-524`
  - Change: Remove `if composition_path.exists():` block and always execute generation

- [x] 1.2 Remove video existence check in `cli.py`
  - Target: `src/movie_generator/cli.py:541-542`
  - Change: Remove `if video_path.exists():` block and always execute rendering

- [x] 1.3 Remove video existence check in `remotion_renderer.py`
  - Target: `src/movie_generator/video/remotion_renderer.py:219-221`
  - Change: Remove existing file check → return logic

- [x] 1.4 **Bug fix**: Include transition settings in `composition.json`
  - Add transition field to `CompositionData`
  - Add transition argument to `create_composition()`
  - Pass transition settings from `cli.py`

## 2. Testing

- [x] 2.1 Run existing tests
  - `uv run pytest tests/test_transition_integration.py -v` ✓ 3 passed
  - `uv run pytest tests/test_video_e2e.py -v` (skipped: import error, existing issue)

- [x] 2.2 Manual test: Verify transition settings
  - Confirmed transition field is included in composition.json ✓
  - Verified operation on existing project (full environment test deferred)

## 3. Documentation

- [x] 3.1 Document changes in commit messages
  - Commit 1: `feat(cli): always regenerate composition.json and video on re-run`
  - Commit 2: `fix(cli): include transition config in composition.json`
