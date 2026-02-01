# Change: web APIユーティリティ整理とPydantic v2対応

## Why
APIルートで `get_client_ip` や日時パースが重複し、`web/api/models.py` のバリデーションが Pydantic v2 非推奨APIを使用している。

## What Changes
- 共有ユーティリティ（IP取得、日時パース/経過時間計算）を専用モジュールに切り出す
- Pydantic v2 の `field_validator` に移行し、挙動を維持する

## Impact
- Affected specs: `specs/refactor-codebase-structure/spec.md`
- Affected code: `web/api/routes/*.py`, `web/api/models.py`
