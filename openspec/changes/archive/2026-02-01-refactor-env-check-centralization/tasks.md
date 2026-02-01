## 1. Implementation
- [x] 1.1 `PROJECT_ROOT` や最小解像度などの共通値/解決ロジックを 1 箇所に集約する（検証: 重複実装が削除されることを確認）

## 2. Tests
- [x] 2.1 `PROJECT_ROOT` の有無でパス解決が変わるケースをユニットテストで検証する（検証: `uv run pytest -k project_root -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] src/movie_generator/project.py:222-231 uses Path.cwd() as the default project root in copy_character_assets(); src/movie_generator/cli.py:1460 and src/movie_generator/cli_pipeline.py:797 call copy_character_assets() without ProjectPaths.get_project_root(), so DOCKER_ENV/PROJECT_ROOT centralization is bypassed
