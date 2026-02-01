# Change: webワーカー構成のモジュール分割

## Why
`web/worker/main.py` が大きく、設定・PocketBaseクライアント・生成ロジック・ワーカーループが密結合のため、保守性とテスト容易性が低い。

## What Changes
- Worker設定、PocketBaseクライアント、生成ラッパー、ワーカーループを専用モジュールに分割する
- `main.py` はエントリポイントとして最小化し、既存の起動方法を維持する

## Impact
- Affected specs: `specs/refactor-codebase-structure/spec.md`
- Affected code: `web/worker/main.py` と新規モジュール群（`web/worker/` 配下）
