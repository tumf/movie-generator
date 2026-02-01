## Context
WebUIのジョブ作成はURL形式チェックのみで進むため、内容が薄いページでも処理が走る。
Firecrawlのsummaryを使えば短時間で要約を取得でき、事前品質判定が可能。

## Goals / Non-Goals
- Goals: summaryを利用してジョブ作成前に品質チェックを行い、無意味なジョブを拒否する
- Goals: WebUIフォームとAPIの両方で同じ判定を適用する
- Non-Goals: コンテンツ全体の再解析、翻訳品質の評価、LLMでの追加要約

## Decisions
- Firecrawlの`/v2/scrape`で`formats=["summary"]`を使い、summaryのみ取得する
- summaryは前後の空白を除去し、200文字以上を合格とする
- 取得失敗（APIキー未設定/タイムアウト/4xx/5xx）は明示的にエラーにする
- 品質チェックは`/api/jobs`の作成フローに組み込み、WebUIフォーム経由も同一処理を通す

## Alternatives Considered
- MCP経由でFirecrawlを呼ぶ: WebAPI側にMCPサーバー起動が必要になり、運用負担が増える
- 既存httpx取得 + 自前判定: 要約を作る別処理が必要で、判定精度が不安定

## Risks / Trade-offs
- ジョブ作成前に追加の外部API呼び出しが入るため、待ち時間が増える
- Firecrawl障害時にジョブ作成が止まる（意図的に拒否）

## Migration Plan
- 既存ジョブには影響なし
- 新規ジョブ作成から品質チェックを適用

## Open Questions
- なし
