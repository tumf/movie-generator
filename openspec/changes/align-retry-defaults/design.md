## Context
スライド生成のリトライ処理が既存の `RetryConfig` を使用しておらず、設定の一貫性が崩れている。

## Goals / Non-Goals
- Goals:
  - `slides` モジュールのリトライ設定を `RetryConfig` に統一する
  - バックオフ係数も定数参照にする
- Non-Goals:
  - リトライ回数や遅延の値を変更する

## Decisions
- `RetryConfig` に定義済みの `MAX_RETRIES`/`INITIAL_DELAY`/`BACKOFF_FACTOR` を参照する

## Risks / Trade-offs
- 将来的に `RetryConfig` を変更した場合、スライド生成にも影響する

## Migration Plan
- 既存と同じ値を維持し、挙動変更を避ける

## Open Questions
- なし
