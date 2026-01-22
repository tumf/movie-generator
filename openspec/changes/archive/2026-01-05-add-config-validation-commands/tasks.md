## 1. config validate コマンドの実装

- [x] 1.1 `validate_config()` 関数を `config.py` に追加
  - YAML 構文チェック
  - Pydantic バリデーション
  - 参照ファイル存在チェック
  - エラー詳細メッセージの生成
- [x] 1.2 `config validate` サブコマンドを `cli.py` に追加
  - `--config` オプションでファイル指定
  - 成功時: 緑色のチェックマーク + 「Valid」メッセージ
  - 失敗時: エラー詳細を表示して非ゼロ終了
- [x] 1.3 ユニットテスト作成 (`tests/test_config_validate.py`)
  - 有効な設定ファイルのテスト
  - 無効な YAML 構文のテスト
  - スキーマエラーのテスト
  - 参照ファイル不在のテスト

## 2. script validate コマンドの実装

- [x] 2.1 `validate_script()` 関数を `script/generator.py` または新規モジュールに追加
  - YAML 構文チェック
  - 必須フィールド検証
  - narrations 形式検証
  - persona_id 参照チェック
- [x] 2.2 `script validate` サブコマンドを `cli.py` に追加
  - `--config` オプションで設定ファイル指定（persona_id 検証用、オプション）
  - 成功時: 緑色のチェックマーク + 統計情報表示
  - 失敗時: エラー詳細を表示して非ゼロ終了
- [x] 2.3 ユニットテスト作成 (`tests/test_script_validate.py`)
  - 有効なスクリプトのテスト
  - 必須フィールド不足のテスト
  - 不正な narrations 形式のテスト
  - 存在しない persona_id 参照のテスト

## 3. ドキュメント・CI

- [x] 3.1 AGENTS.md の CLI Quick Reference を更新
- [x] 3.2 既存テストが通ることを確認
