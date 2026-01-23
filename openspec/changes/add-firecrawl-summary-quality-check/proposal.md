# Change: Firecrawl summaryを使った事前コンテンツ品質チェック

## Why
WebUIのURL入力は形式チェックのみのため、内容がほぼ無いページやログイン画面でもジョブが作成されます。
Firecrawlのsummaryを使って事前に品質を判定し、無意味なジョブ生成を抑止します。

## What Changes
- ジョブ作成前にFirecrawlでsummaryを取得し、200文字未満ならエラーで拒否する
- Firecrawl取得失敗（APIキー未設定/タイムアウト等）の場合はジョブ作成を拒否する
- WebUIフォーム経由とAPI経由の両方で同じ品質チェックを適用する

## Impact
- Affected specs: web-interface
- Affected code: web/api/routes/api_routes.py, web/api/routes/web_routes.py, web/api/config.py, web/tests/test_api.py
