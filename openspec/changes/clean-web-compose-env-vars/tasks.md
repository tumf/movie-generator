## 1. Implementation
- [ ] 1.1 `web/docker-compose.yml` の PocketBase 環境変数から重複行を削除する
  - **Verify**: `POCKETBASE_ADMIN_EMAIL` の定義が1回だけになることを確認

## 2. Validation
- [ ] 2.1 `cd web && docker-compose config` で環境変数の解決結果を確認する
  - **Verify**: PocketBase の環境変数が重複していないこと
