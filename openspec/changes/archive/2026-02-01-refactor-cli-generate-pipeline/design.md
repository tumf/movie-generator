## Context
`generate` は複数段階（content → script → audio → slides → video）を直列に実行する CLI 入口です。現状は単一関数に段階ごとの実装が集約されており、分岐も多く、局所的な変更が他段階へ波及しやすい状態です。

## Goals / Non-Goals
- Goals:
  - `generate()` の責務を段階別に分割し、各段階をユニットテスト可能にする
  - 既存の CLI 振る舞い（引数/出力/エラー）を維持する
- Non-Goals:
  - パイプライン順序や生成物の仕様変更
  - 既存のサブコマンド（`script create` / `audio generate` / `slides generate` / `video render`）の統合

## Decisions
- Decision: `cli.py` は Click コマンド定義に集中し、パイプライン処理は別モジュール（例: `movie_generator/cli_pipeline.py`）へ委譲する
- Decision: 段階間の受け渡しは「入力（設定/パス/範囲）」をまとめたパラメータオブジェクト（Pydantic もしくは dataclass）で行う

## Risks / Trade-offs
- 変更差分が大きくなりやすい → 段階ごとに関数抽出し、都度 `uv run pytest` で回帰を検出する
- Click のオプション値の受け渡しが散らばる → パラメータオブジェクトで集約する

## Migration Plan
1) 段階別関数を追加（最初は `generate()` から単純委譲）
2) 既存ロジックを段階関数へ移動
3) 入口 `generate()` を薄く保つ
