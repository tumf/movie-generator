## 1. 実装
- [ ] 1.1 Firecrawl summary取得のクライアント処理を追加する（検証: 取得関数/クラスが`web/api`配下に存在する）
- [ ] 1.2 `/api/jobs`の作成フローに品質チェックを組み込み、失敗時はジョブ作成を拒否する（検証: `web/api/routes/api_routes.py`で品質チェックが呼び出される）
- [ ] 1.3 WebUIフォームからの作成も同じ品質チェックを通す（検証: `web/api/routes/web_routes.py`が`create_job`のエラーを表示する）
- [ ] 1.4 APIテストにsummary合格/不合格/取得失敗のケースを追加する（検証: `uv run pytest web/tests/test_api.py -v`）
