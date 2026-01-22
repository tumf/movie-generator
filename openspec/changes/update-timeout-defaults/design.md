## Context
タイムアウト値が各モジュールに散在しており、運用やテスト環境で一括調整できない。

## Goals / Non-Goals
- Goals:
  - タイムアウト既定値を `TimeoutConstants` に集約する
  - 主要モジュールで定数参照に統一する
- Non-Goals:
  - ユーザー設定ファイルに新しいタイムアウト項目を追加する

## Decisions
- `constants.py` に `TimeoutConstants` を追加し、用途別の値を定義する
- 既存のハードコード値を `TimeoutConstants` 参照に置き換える

## Risks / Trade-offs
- 定数名の変更が将来的な互換性に影響するため、用途を明確に分ける

## Migration Plan
- 既存の振る舞いと同じ数値を定数として定義し、実挙動を維持する

## Open Questions
- なし
