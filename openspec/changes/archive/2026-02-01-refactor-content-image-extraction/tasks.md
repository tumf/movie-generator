## 1. Implementation
- [x] 1.1 画像抽出の責務（属性抽出/URL 解決/aria-describedby 解決/フィルタ）を関数分割する（検証: 関数が小さく純粋処理になっていることを確認）

## 2. Tests
- [x] 2.1 aria-describedby が欠落/不正な場合の挙動をフィクスチャ HTML でテストする（検証: `uv run pytest -k image_extraction -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] src/movie_generator/content/parser.py:_extract_images (lines 206-231) only appends images with meaningful description, so not all `<img>` elements are extracted; collect all images and separate candidates to satisfy spec Scenario "Successful Image Extraction".
- [x] src/movie_generator/content/parser.py: ParsedContent (lines 35-41) has no field to track excluded/non-candidate images; add tracking to satisfy spec Scenario "Filtering Images by Alt Text Quality" (excluded images still tracked).
- [x] tests/test_parser.py:test_extract_images_no_meaningful_description (lines 119-134) asserts only one image is returned; update tests to reflect tracking of excluded images per spec.

## Acceptance #2 Failure Follow-up
- [x] src/movie_generator/content/parser.py:_extract_images で is_candidate を付与しているが、src/movie_generator/cli.py:_fetch_and_generate_script / src/movie_generator/cli_pipeline.py:stage_script_resolution / src/movie_generator/script/core.py:generate_script_from_url で parsed.images 全件を images_metadata に渡しており、候補のみを使う仕様 (openspec/changes/refactor-content-image-extraction/specs/video-generation/spec.md) を満たしていない。候補のみを渡すか下流で絞り込む。
- [x] src/movie_generator/content/parser.py:ImageInfo.is_candidate が参照されずデッドコード化しているため、候補判定を利用する処理を追加するか不要なら仕様と整合する形で整理する。
