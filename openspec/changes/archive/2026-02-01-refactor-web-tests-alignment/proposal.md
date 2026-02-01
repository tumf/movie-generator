# Change: webテストの実装整合とモック化

## Why
`web/tests/test_worker_progress.py` が現行のワーカー実装と不整合で、`subprocess` 前提のテストになっているため、実装変更後に信頼できる回帰テストになっていない。

## What Changes
- ワーカー進捗テストを、現行の直接API呼び出し方式に合わせて更新する
- 外部依存（LLM/VOICEVOX/Remotion）をモック化し、ローカルで再現可能なテストにする

## Impact
- Affected specs: `specs/refactor-codebase-structure/spec.md`
- Affected code: `web/tests/test_worker_progress.py`（必要に応じて `web/tests/conftest.py`）
