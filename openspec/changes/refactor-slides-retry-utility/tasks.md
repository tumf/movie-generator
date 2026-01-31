## 1. Implementation
- [x] 1.1 スライド生成で使うリトライを共通ユーティリティ化する（検証: スライド生成が共通ユーティリティを呼ぶことを確認）
- [x] 1.2 リトライ設定は `RetryConfig` のみから取得する（検証: リテラル回数/遅延が存在しないことを確認）

## 2. Tests
- [x] 2.1 リトライ回数/バックオフが `RetryConfig` に追従することをユニットテストで検証する（検証: `uv run pytest -k retry -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] Git作業ツリーをクリーンにする（変更/未追跡: `openspec/changes/refactor-slides-retry-utility/tasks.md`, `src/movie_generator/slides/generator.py`, `src/movie_generator/utils/retry.py`, `tests/test_retry.py`）。
- [x] 仕様に合わせて `RetryConfig.BASE_DELAY_SECONDS` を追加し、スライド生成のリトライがそれを参照するよう更新する（`src/movie_generator/constants.py`, `src/movie_generator/slides/generator.py`）。
