## 1. Implementation
- [x] 1.1 composition.json 生成処理の入力を設定オブジェクトにまとめる（検証: 生成関数の引数が整理されていることを確認）
- [x] 1.2 speaker 情報欠落時のデフォルト付与を生成側で統一する（検証: フィクスチャ composition を用いたユニットテストで確認）

## 2. Tests
- [x] 2.1 speaker 情報なし composition.json の互換動作をユニットテストで固定する（検証: `uv run pytest -k composition -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] src/movie_generator/project.py:572-624 Project.update_composition_json builds composition.json via its own mapping instead of the centralized composition builder; refactor to use build_composition_data or remove per spec.
- [x] src/movie_generator/project.py:572-624 Project.update_composition_json is not invoked by CLI flow (render path uses src/movie_generator/video/remotion_renderer.py:739-753); either integrate into flow or remove/update tests (e.g., tests/test_transition_integration.py:69) to avoid dead code.
