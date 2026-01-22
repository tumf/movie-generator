# Tasks: MCP Agent 機能の追加

## 1. エージェントモジュールの実装

- [x] 1.1 `src/movie_generator/agent/__init__.py` を作成
- [x] 1.2 `src/movie_generator/agent/tool_converter.py` を実装
  - MCP tool定義をOpenAI tools形式に変換する `convert_mcp_tools_to_openai()` 関数
  - inputSchemaをparametersにマッピング
- [x] 1.3 `src/movie_generator/agent/agent_loop.py` を実装
  - `AgentLoop` クラス: LLMとMCPツールの対話ループ
  - 最大反復回数制限（デフォルト10回）
  - ツール実行結果のメッセージ履歴管理
- [x] 1.4 エージェントモジュールのユニットテスト作成
  - `tests/test_tool_converter.py`
  - `tests/test_agent_loop.py`

## 2. スクリプト生成の拡張

- [x] 2.1 `script/core.py` に `generate_script_from_url_with_agent()` を追加
  - MCPクライアント接続
  - エージェントループでコンテンツ取得
  - 取得したコンテンツでスクリプト生成
- [x] 2.2 同期版 `generate_script_from_url_with_agent_sync()` を追加
- [x] 2.3 エージェント版スクリプト生成の統合テスト作成
  - `tests/test_script_with_agent.py`

## 3. ワーカーの設定管理

- [x] 3.1 ワーカーに環境変数対応を追加
  - `CONFIG_PATH`: movie-generator の config.yaml パス
  - `MCP_CONFIG_PATH`: MCP設定ファイルパス（オプション）
- [x] 3.2 ワーカーの `generate_video()` を更新
  - MCP設定がある場合: `generate_script_from_url_with_agent()` を使用
  - MCP設定がない場合: 既存の `generate_script_from_url()` を使用
- [x] 3.3 ワーカーの設定テスト作成

## 4. 設定ファイルの追加

- [x] 4.1 `web/config/config.yaml` サンプルを作成
- [x] 4.2 `web/config/mcp.jsonc` サンプルを作成
  - Firecrawl設定（必須）
  - Brave Search設定（オプション）
- [x] 4.3 設定ファイルのドキュメント追加

## 5. ドキュメントと検証

- [x] 5.1 `docs/MCP_AGENT.md` を作成
  - エージェント機能の説明
  - 設定方法
  - トラブルシューティング
- [x] 5.2 統合テストの実行と確認
- [x] 5.3 ワーカーでの動作確認（実装完了、実機確認は別途）

## Dependencies

- Task 1.2, 1.3 は並行実行可能
- Task 2.1 は Task 1.* に依存
- Task 3.2 は Task 2.1 に依存
- Task 4.* は Task 1-3 と並行実行可能
