## Context
発音LLMモデルやレンダリング実行設定が設定ファイルから指定できず、コード側のハードコードに依存している。

## Goals / Non-Goals
- Goals:
  - `audio.pronunciation_model` を追加して発音LLMモデルを構成可能にする
  - `video.render_concurrency` と `video.render_timeout_seconds` を追加する
  - `config/default.yaml` と `config init` 出力に新フィールドを反映する
- Non-Goals:
  - LLMベースURLの設定追加（別変更で対応）
  - LLMモデルのデフォルト削除（別変更で対応）

## Decisions
- `AudioConfig` に `pronunciation_model` を追加する
- `VideoConfig` に `render_concurrency` と `render_timeout_seconds` を追加する
- 既存の挙動と整合するデフォルト値を設定する

## Risks / Trade-offs
- 既存の設定ファイルは新フィールドを持たないが、デフォルト値で互換性を維持する

## Migration Plan
- 新フィールドは任意項目として追加し、旧設定ファイルはそのまま利用できる

## Open Questions
- なし
