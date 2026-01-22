# Change: 設定ファイル検証コマンドの追加

## Why

現在、設定ファイル（config.yaml）やスクリプトファイル（script.yaml）が正しいかどうかを確認する手段がない。
ユーザーは `generate` コマンドを実行して初めてエラーに気づく状態である。
事前に検証できるコマンドがあれば、設定ミスを早期に発見でき、ワークフローが効率化される。

## What Changes

- `config validate` サブコマンドの追加
  - 設定ファイル（YAML）の構文チェック
  - Pydantic バリデーションによるスキーマ検証
  - 参照されているファイル（背景画像、BGM など）の存在チェック
  - ペルソナ ID の重複チェック

- `script validate` サブコマンドの追加
  - スクリプトファイル（YAML）の構文チェック
  - 必須フィールド（title, sections）の存在確認
  - セクション内の narrations の形式検証
  - persona_id の参照妥当性チェック（config と併用時）

## Impact

- Affected specs: `cli-interface`
- Affected code: `src/movie_generator/cli.py`, `src/movie_generator/config.py`
- New functionality: 破壊的変更なし（新規コマンド追加のみ）
