# Implementation Tasks

## 1. MCP設定ファイル読み込み機能

- [x] 1.1 `src/movie_generator/mcp/__init__.py` を作成
- [x] 1.2 `src/movie_generator/mcp/config.py` でMCP設定ファイル読み込み関数を実装
  - [x] `opencode.jsonc` (JSONC形式) の読み込み対応
  - [x] `.cursor/mcp.json` (JSON形式) の読み込み対応
  - [x] `claude_desktop_config.json` (JSON形式) の読み込み対応
  - [x] `{env:VAR_NAME}` 形式の環境変数参照を実際の値に置換する関数を実装
  - [x] 再帰的に全てのstring値を走査して環境変数を置換
  - [x] 未定義環境変数のエラーハンドリング
- [x] 1.3 MCPサーバー設定のPydanticモデルを定義

## 2. MCPクライアント実装

- [x] 2.1 `src/movie_generator/mcp/client.py` を作成
- [x] 2.2 MCPサーバーとの通信クライアントを実装
  - [x] Firecrawlツール呼び出し機能
  - [x] その他MCPツールの汎用呼び出し機能
- [x] 2.3 エラーハンドリング（タイムアウト、接続失敗など）

## 3. CLI引数追加

- [x] 3.1 `src/movie_generator/cli.py` に `--mcp-config` オプションを追加
- [x] 3.2 設定ファイルパスのバリデーション

## 4. 台本生成機能の拡張

- [x] 4.1 `generate_script()` に `mcp_config_path` パラメータを追加（CLI経由で統合）
- [x] 4.2 MCPツールを使ったコンテンツ取得ロジックを実装
- [x] 4.3 取得したコンテンツを既存のプロンプトに統合

## 5. テスト

- [x] 5.1 `tests/test_mcp_config.py` - MCP設定読み込みのテスト
  - [x] 環境変数置換の正常系テスト
  - [x] 未定義環境変数のエラーテスト
  - [x] ネストされたオブジェクト内の環境変数置換テスト
  - [x] 複数の環境変数参照の同時置換テスト
- [x] 5.2 `tests/test_mcp_client.py` - MCPクライアントのモックテスト
- [x] 5.3 `tests/test_script_with_mcp.py` - E2Eテスト（モック使用）

## 6. ドキュメント

- [x] 6.1 README に MCP連携機能の使用方法を追加
- [x] 6.2 サンプルMCP設定ファイルを提供
