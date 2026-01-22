# Change: MCP Agent 機能の追加（公式SDK使用）

## Why

現在のMCP実装は単純なFirecrawlスクレイピングのみで、本来期待されていたLLMがMCPツールを自律的に選択・使用するエージェント機能がない。また、現在の独自実装MCPClientは公式のModel Context Protocol仕様に完全準拠していない。公式 MCP Python SDK（https://github.com/modelcontextprotocol/python-sdk）に移行し、標準準拠のエージェント機能を実装することで、より高度なコンテンツ取得とエコシステムとの互換性を確保する。

## What Changes

- **依存関係の追加**: 公式 `mcp` パッケージを `pyproject.toml` に追加
- **既存MCPクライアントの置き換え**: `src/movie_generator/mcp/client.py` を公式SDK使用に移行
- 新規モジュール `movie_generator/agent/` を追加
  - `tool_converter.py`: MCP tools → OpenAI tools形式変換
  - `agent_loop.py`: 公式SDKのClientSessionを使用したエージェントループ実行
- `script/core.py` に `generate_script_from_url_with_agent()` 関数を追加
- ワーカーに環境変数ベースのMCP設定管理を追加
- MCP設定があればエージェント版を使用、なければ標準動作を維持

## Impact

- Affected specs: 新規 `mcp-agent` capability 追加
- Affected code:
  - `pyproject.toml` (依存関係追加: `mcp[cli]`)
  - `src/movie_generator/mcp/client.py` (公式SDK使用に移行・破壊的変更)
  - `src/movie_generator/agent/` (新規)
  - `src/movie_generator/script/core.py` (新規関数追加)
  - `web/worker/main.py` (環境変数対応)
  - `web/worker/pyproject.toml` (依存関係確認)
  - `web/config/` (設定ファイル追加)

## Migration Notes

既存の `MCPClient` を使用しているコードは、公式SDKの `ClientSession` APIに移行する必要がある。ただし、現在movie-generator本体で直接 `MCPClient` を使用している箇所は `cli.py` のみ（`fetch_content_with_mcp`）なので、影響範囲は限定的。
