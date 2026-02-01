## 1. Implementation
- [ ] 1.1 `WorkerSettings` を `web/worker/settings.py` に切り出し、既存の環境変数名を維持する
  - **Verify**: `web/worker/main.py` が `WorkerSettings()` を生成し、既存の env 名が使われていることを確認
- [ ] 1.2 `PocketBaseClient` を `web/worker/pocketbase_client.py` に移動する
  - **Verify**: `web/worker/worker.py` が新モジュールを import していることを確認
- [ ] 1.3 `create_default_movie_config()` を `web/worker/movie_config_factory.py` に移動する
  - **Verify**: `web/worker/generator.py` が新モジュールを参照していることを確認
- [ ] 1.4 `MovieGeneratorWrapper` を `web/worker/generator.py` に移動する
  - **Verify**: `web/worker/worker.py` から `MovieGeneratorWrapper` を import していることを確認
- [ ] 1.5 `Worker` 本体を `web/worker/worker.py` に移動し、`main.py` はエントリポイントのみ残す
  - **Verify**: `web/worker/main.py` が `Worker` を呼び出すだけになっていることを確認

## 2. Validation
- [ ] 2.1 `cd web/worker && uv run pytest` を実行し、既存テストが壊れていないことを確認する
  - **Verify**: テストが成功すること
