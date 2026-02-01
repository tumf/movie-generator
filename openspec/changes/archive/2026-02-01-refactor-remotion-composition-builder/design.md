## Context
composition.json は Remotion 側の入力であり、後方互換性（フィールド欠落時の既定動作）が重要です。生成・デフォルト付与が分散すると、仕様と実装のズレが発生しやすくなります。

## Goals / Non-Goals
- Goals:
  - 生成入力を 1 つのオブジェクトにまとめ、デフォルト付与と互換ロジックを集約する
  - composition.json のスキーマ互換性を維持する
- Non-Goals:
  - composition.json のスキーマ変更

## Decisions
- Decision: 生成関数は「入力オブジェクト → composition data」を返す形にし、ファイル書き込みは別責務にする
