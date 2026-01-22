# Change: 台本生成時のMCPサーバー連携

## Why

現在の台本生成は静的なコンテンツのみを使用していますが、MCPサーバー（Firecrawlなど）を経由して動的にウェブ情報を取得できれば、より豊富で最新の情報を含む台本を生成できます。

## What Changes

- CLIコマンド実行時に `--mcp-config` オプションでMCP設定ファイルパスを指定可能にする
- MCP設定ファイル（`.cursor/mcp.json`, `opencode.jsonc`, `claude_desktop_config.json`）を読み込む機能を追加
- 台本生成時にMCPサーバー（Firecrawl等）を使ってウェブコンテンツを取得する機能を追加
- `generate_script()` 関数にMCPツール利用のためのパラメータを追加

## Impact

- 影響を受けるspec: `video-generation`
- 影響を受けるコード:
  - `src/movie_generator/cli.py` - CLI引数追加
  - `src/movie_generator/config.py` - MCP設定読み込み
  - `src/movie_generator/script/generator.py` - MCP連携機能追加
  - 新規ファイル: `src/movie_generator/mcp/` - MCPクライアント実装
