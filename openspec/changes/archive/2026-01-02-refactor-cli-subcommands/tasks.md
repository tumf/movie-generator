# Tasks: CLIサブコマンド構造へのリファクタリング

## 1. 準備・リファクタリング

- [x] 1.1 `cli.py` の共通ロジックを内部関数として抽出
  - [x] サブコマンドとして直接実装（関数抽出は不要と判断）
- [x] 1.2 既存の `generate` コマンドは維持（後方互換性）
- [x] 1.3 既存テストが通ることを確認 (`uv run pytest tests/test_scene_range.py -v`)

## 2. サブコマンド実装

- [x] 2.1 `script` グループと `script create` コマンドを実装
  - オプション: `--output`, `--config`, `--api-key`, `--mcp-config`, `--character`, `--style`, `--model`
  - 動作: URL取得 → スクリプト生成 → script.yaml保存
- [x] 2.2 `audio` グループと `audio generate` コマンドを実装
  - オプション: `--config`, `--scenes`, `--speaker-id`, `--allow-placeholder`
  - 動作: script.yaml読み込み → フレーズ分割 → 音声合成 → audio/*.wav保存
- [x] 2.3 `slides` グループと `slides generate` コマンドを実装
  - オプション: `--config`, `--api-key`, `--scenes`, `--model`, `--language`, `--max-concurrent`
  - 動作: script.yaml読み込み → スライド生成 → slides/*.png保存
- [x] 2.4 `video` グループと `video render` コマンドを実装
  - オプション: `--config`, `--scenes`, `--output`, `--progress`, `--transition`, `--fps`
  - 動作: script.yaml + audio/ + slides/ → Remotion → output.mp4

## 3. 共通オプション追加

- [x] 3.1 `--force` オプションを全コマンドに追加
  - 既存ファイルを強制上書き
- [x] 3.2 `--quiet` オプションを全コマンドに追加
  - 成功時は最終出力パスのみ出力
  - 進捗表示なし
- [x] 3.3 `--verbose` オプションを全コマンドに追加
  - 詳細ログ出力（パス、サイズ、処理時間等）
  - エラー時はスタックトレース表示
- [x] 3.4 `--dry-run` オプションを全コマンドに追加
  - ファイル書き込み、API呼び出しをスキップ
  - 「何が実行されるか」を出力
- [x] 3.5 `--quiet` と `--verbose` の相互排他チェックを実装

## 4. テスト

- [x] 4.1 `script create` コマンドのテスト追加
- [x] 4.2 `audio generate` コマンドのテスト追加
- [x] 4.3 `slides generate` コマンドのテスト追加
- [x] 4.4 `video render` コマンドのテスト追加
- [x] 4.5 共通オプション (`--force`, `--quiet`, `--verbose`, `--dry-run`) のテスト追加
- [x] 4.6 既存の `generate` コマンドが引き続き動作することを確認

## 5. ドキュメント更新

- [x] 5.1 `README.md` の Usage セクションを更新
- [x] 5.2 `AGENTS.md` の Quick Reference を更新
- [x] 5.3 `--help` メッセージの確認・改善

## Dependencies

- タスク2はタスク1完了後に開始
- タスク3はタスク2と並行可能
- タスク4はタスク2, 3完了後に開始
- タスク5はタスク4完了後に開始

## 完了

すべてのタスクが完了しました。
