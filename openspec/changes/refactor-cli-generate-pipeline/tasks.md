## 1. Implementation
- [x] 1.1 `generate()` の段階を関数として抽出する（検証: `src/movie_generator/cli.py` の `generate()` が段階関数に委譲していることを確認）
- [x] 1.2 段階間の引数をパラメータオブジェクトに集約する（検証: 段階関数の引数が 5 個以下相当になることを確認）
- [x] 1.3 例外メッセージに段階名/入力（URL か script パスか等）の文脈を付与する（検証: エラー系のユニットテストでメッセージを確認）

## 2. Tests
- [x] 2.1 `generate` の段階呼び出し順とスキップ条件（例: 既存 `script.yaml`）をモックで検証するテストを追加する（検証: `uv run pytest -k generate -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）
- [x] 3.2 形式チェックが通る（検証: `uv run ruff check .` と `uv run ruff format .`）

## Acceptance #2 Failure Follow-up
- [x] Update spec.md to match actual function names: change `_create_script()`, `_generate_audio()`, `_generate_slides()`, `_render_video()` to `stage_script_resolution()`, `stage_audio_generation()`, `stage_slides_generation()`, `stage_video_rendering()` OR rename implementation functions to match spec
- [x] Add @common_options decorator to the `generate` command in src/movie_generator/cli.py (line 276) to support --force, --quiet, --verbose, --dry-run options as specified in spec.md lines 14-18
- [x] Add tests for pipeline stage functions to verify call order and skip conditions (e.g., test that stage_script_resolution skips generation when script.yaml exists)

## Acceptance #3 Failure Follow-up
- [x] Commit auto-formatting changes from ruff in 22 files: scripts/inspect_psd.py, tests/test_character_animation.py, tests/test_cli_subcommands.py, tests/test_config_validate.py, tests/test_furigana.py, tests/test_mcp_client.py, tests/test_mcp_config.py, tests/test_mcp_integration.py, tests/test_multi_speaker.py, tests/test_script_validate.py, tests/test_script_with_mcp.py, tests/test_subtitle_color.py, tests/test_video_e2e.py, tests/test_voicevox.py, tests/test_worker_config.py, web/api/firecrawl_client.py, web/api/main.py, web/api/routes/api_routes.py, web/demo_progress.py, web/tests/conftest.py, web/tests/test_worker.py, web/worker/main.py (import organization and blank line removal)
