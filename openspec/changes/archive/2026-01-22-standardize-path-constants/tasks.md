## 1. 実装
- [x] 1.1 `ProjectPaths` と `VideoConstants` の定数を追加/拡張する（完了条件: `constants.py` に定義される）
- [x] 1.2 生成アセットのファイル名フォーマット参照を定数化する（完了条件: `audio/voicevox.py` と `video/remotion_renderer.py` が定数参照になる）
- [x] 1.3 画像の最小解像度チェックで定数を参照する（完了条件: `slides/generator.py` が `VideoConstants` を参照する）
- [x] 1.4 Docker環境のプロジェクトルート参照を環境変数化する（完了条件: `remotion_renderer.py` が `PROJECT_ROOT` を参照する）

## 2. 検証
- [x] 2.1 `uv run pytest -k "slide" -v` が成功することを確認する

## Acceptance #1 Failure Follow-up
- [x] Commit all modified files: openspec/changes/standardize-path-constants/tasks.md, src/movie_generator/audio/voicevox.py, src/movie_generator/constants.py, src/movie_generator/slides/generator.py, src/movie_generator/video/core.py, src/movie_generator/video/remotion_renderer.py, web/worker/main.py

## Acceptance #2 Failure Follow-up
- [x] src/movie_generator/cli.py lines 550, 643-644, 686-687, 690-691, 1346, 1433-1434, 1621-1622, 1625-1626, 1872, 1908-1909: Replace hardcoded filename formats `f"phrase_{...}:04d}.wav"` and `f"slide_{...}:04d}.png"` with `ProjectPaths.PHRASE_FILENAME_FORMAT` and `ProjectPaths.SLIDE_FILENAME_FORMAT`
- [x] src/movie_generator/audio/core.py lines 257, 338-339: Replace hardcoded filename format `f"phrase_{phrase.original_index:04d}.wav"` with `ProjectPaths.PHRASE_FILENAME_FORMAT`
- [x] src/movie_generator/audio/synthesizer.py line 71: Replace hardcoded filename format `f"phrase_{phrase.original_index:04d}.wav"` with `ProjectPaths.PHRASE_FILENAME_FORMAT`
- [x] src/movie_generator/slides/core.py lines 151-152, 155-156: Replace hardcoded filename format `f"slide_{idx:04d}.png"` with `ProjectPaths.SLIDE_FILENAME_FORMAT`
- [x] src/movie_generator/slides/generator.py line 319: Replace hardcoded filename format `f"slide_{file_index:04d}.png"` with `ProjectPaths.SLIDE_FILENAME_FORMAT`
- [x] src/movie_generator/video/renderer.py line 95: Replace hardcoded filename format `f"audio/phrase_{p.original_index:04d}.wav"` with `ProjectPaths.PHRASE_FILENAME_FORMAT`
- [x] src/movie_generator/video/core.py lines 195, 232-233: Replace hardcoded filename formats with `ProjectPaths.PHRASE_FILENAME_FORMAT` and `ProjectPaths.SLIDE_FILENAME_FORMAT`
- [x] src/movie_generator/video/remotion_renderer.py line 341: Replace hardcoded filename format `f"audio/phrase_{phrase.original_index:04d}.wav"` with `ProjectPaths.PHRASE_FILENAME_FORMAT`

## Acceptance #3 Failure Follow-up
- [x] Commit all modified files: openspec/changes/archive/2026-01-22-standardize-path-constants/tasks.md, src/movie_generator/audio/core.py, src/movie_generator/audio/synthesizer.py, src/movie_generator/cli.py, src/movie_generator/slides/core.py, src/movie_generator/slides/generator.py, src/movie_generator/video/core.py, src/movie_generator/video/remotion_renderer.py, src/movie_generator/video/renderer.py
