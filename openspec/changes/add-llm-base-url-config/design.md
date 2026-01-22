## Context
LLM呼び出しのベースURLがコードに埋め込まれており、環境ごとの切り替えが難しい。

## Goals / Non-Goals
- Goals:
  - `LLMConfig` と `SlidesLLMConfig` に `base_url` を追加する
  - すべてのLLM呼び出しが設定値を参照する
- Non-Goals:
  - LLMモデル指定の必須化（別変更で対応）

## Decisions
- デフォルト値は既存の `https://openrouter.ai/api/v1` を維持する
- `config/default.yaml` と `config init` 出力に反映する

## Risks / Trade-offs
- ベースURLの変更で障害が発生した場合、原因特定が必要

## Migration Plan
- 既存設定ファイルは新フィールドを持たないため、デフォルト値で互換性を維持する

## Open Questions
- なし
