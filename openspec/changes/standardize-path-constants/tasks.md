## 1. 実装
- [x] 1.1 `ProjectPaths` と `VideoConstants` の定数を追加/拡張する（完了条件: `constants.py` に定義される）
- [x] 1.2 生成アセットのファイル名フォーマット参照を定数化する（完了条件: `audio/voicevox.py` と `video/remotion_renderer.py` が定数参照になる）
- [x] 1.3 画像の最小解像度チェックで定数を参照する（完了条件: `slides/generator.py` が `VideoConstants` を参照する）
- [x] 1.4 Docker環境のプロジェクトルート参照を環境変数化する（完了条件: `remotion_renderer.py` が `PROJECT_ROOT` を参照する）

## 2. 検証
- [x] 2.1 `uv run pytest -k "slide" -v` が成功することを確認する

## Acceptance #1 Failure Follow-up
- [x] Commit all modified files: openspec/changes/standardize-path-constants/tasks.md, src/movie_generator/audio/voicevox.py, src/movie_generator/constants.py, src/movie_generator/slides/generator.py, src/movie_generator/video/core.py, src/movie_generator/video/remotion_renderer.py, web/worker/main.py
