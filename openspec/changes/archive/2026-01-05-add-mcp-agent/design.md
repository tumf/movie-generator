# Design: MCP Agent 機能

## Context

Movie Generator は現在 MCP (Model Context Protocol) を使用してFirecrawlでURLをスクレイピングしている。しかし、現在の実装はMCPの本来の機能を活用していない。MCPは複数のツール（Firecrawl, Brave Search等）を提供し、LLMがこれらを自律的に選択・使用するエージェントパターンを想定している。

### ステークホルダー

- ワーカー: バックグラウンドジョブ処理
- CLI ユーザー: コマンドラインからの動画生成
- 開発者: 拡張性と保守性

## Goals / Non-Goals

### Goals

- LLMがMCPツールを自律的に選択・実行するエージェントループの実装
- ワーカーとCLIの両方でエージェント機能を利用可能にする
- 既存の動作との互換性を維持（MCP設定がなければ標準動作）

### Non-Goals

- MCP Sampling機能の使用（OpenRouter Tool Callingを使用）
- 新しいMCPサーバーの実装
- 既存のMCPClientクラスの大幅な変更

## Decisions

### Decision 1: エージェントループの実装場所

**決定**: 新規モジュール `movie_generator/agent/` を作成

**理由**:
- 単一責任の原則: エージェントロジックはコンテンツ取得とスクリプト生成から分離
- テスト容易性: エージェントロジックを独立してテスト可能
- 再利用性: 将来的に他の用途（スライド生成等）でも使用可能

**代替案**:
- `mcp/` モジュールに追加: MCPの責務が曖昧になる
- `script/` モジュールに追加: スクリプト生成と密結合になる

### Decision 2: ツール形式変換

**決定**: MCP tools → OpenAI tools形式への変換を行う

**理由**:
- OpenRouterはOpenAI互換のTool Calling APIを提供
- MCPのツール定義（JSON Schema）をOpenAI形式に変換可能

```python
# MCP tool format
{
    "name": "firecrawl_scrape",
    "description": "Scrape a URL",
    "inputSchema": {...}
}

# OpenAI tools format
{
    "type": "function",
    "function": {
        "name": "firecrawl_scrape",
        "description": "Scrape a URL",
        "parameters": {...}
    }
}
```

### Decision 3: エージェントループの設計

**決定**: シンプルなwhile-loopベースのエージェントループ

```
1. MCPクライアントに接続
2. available_tools を OpenAI tools形式に変換
3. LLMに初期メッセージ + tools を送信
4. ループ:
   - LLM responseを取得
   - finish_reason が "tool_calls" なら MCPClient.call_tool() で実行
   - finish_reason が "stop" なら最終レスポンスを返す
5. 最大反復回数チェック（デフォルト10回）
```

**理由**:
- 単純で理解しやすい
- デバッグが容易
- MCPサーバーの特性（同期的なツール呼び出し）に適合

### Decision 4: 設定管理

**決定**: 環境変数ベースの設定

```
CONFIG_PATH       # movie-generator の config.yaml へのパス
MCP_CONFIG_PATH   # MCP設定ファイルへのパス（オプション）
```

**理由**:
- Dockerコンテナとの親和性
- 既存の環境変数パターン（OPENROUTER_API_KEY等）との一貫性
- MCP設定がなければ標準動作を維持（フォールバックではなく条件分岐）

### Decision 5: フォールバック概念の排除

**決定**: フォールバックではなく、条件分岐による動作選択

**理由**:
- AGENTS.mdの「NEVER use low-quality fallbacks」ルールに準拠
- MCP設定があればエージェント版、なければ標準動作を明示的に選択
- サイレントな品質低下を防止

## Risks / Trade-offs

### Risk 1: LLMのツール選択ミス

**リスク**: LLMが不適切なツールを選択する可能性
**軽減策**: システムプロンプトでツール使用のガイダンスを提供

### Risk 2: 無限ループ

**リスク**: ツール呼び出しが終了条件に達しない
**軽減策**: 最大反復回数（デフォルト10回）を設定

### Risk 3: MCPサーバーの可用性

**リスク**: MCPサーバーが応答しない場合
**軽減策**: タイムアウト設定と明示的なエラー報告

## Module Structure

```
src/movie_generator/
├── agent/
│   ├── __init__.py
│   ├── tool_converter.py    # MCP → OpenAI tools変換
│   └── agent_loop.py        # エージェントループ実行
├── mcp/
│   ├── client.py            # 既存（変更なし）
│   └── config.py            # 既存（変更なし）
└── script/
    └── core.py              # generate_script_from_url_with_agent() 追加
```

## Open Questions

1. ~~ワーカーでMCP設定がない場合の動作確認方法~~ → 標準動作を維持（フォールバックではない）
