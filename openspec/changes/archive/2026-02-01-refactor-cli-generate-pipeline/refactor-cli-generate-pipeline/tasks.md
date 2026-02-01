## 1. Implementation
- [ ] 1.1 `generate()` の段階を関数として抽出する（検証: `src/movie_generator/cli.py` の `generate()` が段階関数に委譲していることを確認）
- [ ] 1.2 段階間の引数をパラメータオブジェクトに集約する（検証: 段階関数の引数が 5 個以下相当になることを確認）
- [ ] 1.3 例外メッセージに段階名/入力（URL か script パスか等）の文脈を付与する（検証: エラー系のユニットテストでメッセージを確認）

## 2. Tests
- [ ] 2.1 `generate` の段階呼び出し順とスキップ条件（例: 既存 `script.yaml`）をモックで検証するテストを追加する（検証: `uv run pytest -k generate -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
- [ ] 3.2 形式チェックが通る（検証: `uv run ruff check .` と `uv run ruff format .`）
