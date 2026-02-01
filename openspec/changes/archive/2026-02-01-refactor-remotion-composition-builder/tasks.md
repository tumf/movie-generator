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

## Acceptance #2 Failure Follow-up
- [x] src/movie_generator/project.py:572-654 Project.update_composition_json remains unused by the CLI render flow (cli.py:1489 -> remotion_renderer.render_video_with_remotion -> remotion_renderer.update_composition_json). Integrate Project.update_composition_json into the CLI flow or remove/replace it to eliminate dead code.
- [x] src/movie_generator/project.py:627-631 collects phrase_dict["audio_file"] into audio_paths, but src/movie_generator/video/remotion_renderer.py:321 hardcodes audioFile using ProjectPaths.PHRASE_FILENAME_FORMAT, dropping provided audio_file values. Use audio_paths in build_composition_data or align update_composition_json input contract.

## Acceptance #3 Failure Follow-up
- [x] 3.3.1 Remove Project.update_composition_json from src/movie_generator/project.py:572
- [x] 3.3.2 Update tests/test_transition_integration.py to use remotion_renderer.update_composition_json directly
