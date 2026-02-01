## 1. Implementation
- [ ] 1.1 `get_client_ip` を `web/api/routes/request_utils.py` に切り出し、`api_routes.py` と `web_routes.py` から参照する
  - **Verify**: 両ルートで同一ユーティリティを import していることを確認
- [ ] 1.2 `parse_datetime` と `calculate_elapsed_time` を `web/api/routes/job_time.py` に切り出す
  - **Verify**: `web_routes.py` が新モジュール経由で計算していることを確認
- [ ] 1.3 `web/api/models.py` の `@validator` を `@field_validator(mode="before")` に置換する
  - **Verify**: `JobResponse` の空文字→`None`変換が維持されていることを確認

## 2. Validation
- [ ] 2.1 `cd web/api && uv run pytest` を実行し、APIテストが通ることを確認する
  - **Verify**: テストが成功すること
