# Change: 環境/パス解決ロジックの重複を解消し共通化

## Why
Docker/ローカル実行など環境に依存するパス解決・最小解像度チェックが複数箇所に分散すると、片方だけ修正して挙動がズレるリスクがあります。共通化により一貫性を保ちます。

## What Changes
- `PROJECT_ROOT` を含む環境/パス解決と関連するチェックを共通関数へ集約する
- 複数モジュールから同一の共通関数/定数を参照する

## Impact
- Affected specs: `openspec/specs/config-management/spec.md`
- Affected code: `src/movie_generator/video/remotion_renderer.py` など（重複箇所）
