## 1. Implementation
- [x] 1.1 `generate_script()` を段階別の小関数に分割する（検証: 各段階が個別関数として切り出されていることを確認）
- [x] 1.2 レスポンス検証/パースを純粋関数化し、I/O から分離する（検証: ユニットテストで LLM 呼び出しなしにパースを検証できる）

## 2. Tests
- [x] 2.1 単一話者モードのパースをフィクスチャ JSON で検証するテストを追加する（検証: `uv run pytest -k single_speaker -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] Remove duplicate `background` field in ScriptSection class (src/movie_generator/script/generator.py:30-31)

## Acceptance #2 Failure Follow-up
- [x] Single-speaker mode uses dialogue prompt when one persona is configured: Fixed by modifying `src/movie_generator/script/core.py` (lines 117-122, 331-336) and `src/movie_generator/cli_pipeline.py` (lines 283-289) to only set personas_for_script when len(personas) >= 2, ensuring single-speaker mode uses the single-speaker prompt.
- [x] Single-speaker response parsing does not split into phrases or assign personas[0].id: Fixed by modifying `src/movie_generator/script/generator.py` _parse_script_response to accept optional personas parameter and assign default_persona_id = personas[0]["id"] when len(personas) == 1, applying this to all narrations without persona_id.
- [x] Regression check failed because tests cannot run: Fixed by installing the package with dev dependencies using `uv pip install -e ".[dev]"`, ensuring pytest runs in the correct environment with movie_generator module available.

## Acceptance #3 Failure Follow-up
- [x] Git working tree is dirty: Fixed by committing changes to `src/movie_generator/cli_pipeline.py` and `src/movie_generator/script/generator.py`.
- [x] `src/movie_generator/cli_pipeline.py` `stage_script_resolution()` (lines 282-289) only passes personas when `len(personas) >= 2`, so single persona mode calls `generate_script()` without personas; pass the single persona so `_parse_script_response()` can assign `personas[0].id` per spec: Fixed by changing condition to `len(personas) >= 1` (line 287).
- [x] Single-speaker response parsing does not split phrases: `src/movie_generator/script/generator.py` `_parse_script_response()` (lines 881-945) and `src/movie_generator/cli_pipeline.py` `stage_audio_generation()` (lines 360-375) create 1:1 narrations/phrases without `split_into_phrases()`; implement phrase splitting for legacy `"narration"` format: Fixed by calling `split_into_phrases()` in `_parse_script_response()` for legacy narration format (lines 940-951).
