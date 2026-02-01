## 1. Implementation
- [ ] 1.1 画像抽出の責務（属性抽出/URL 解決/aria-describedby 解決/フィルタ）を関数分割する（検証: 関数が小さく純粋処理になっていることを確認）

## 2. Tests
- [ ] 2.1 aria-describedby が欠落/不正な場合の挙動をフィクスチャ HTML でテストする（検証: `uv run pytest -k image_extraction -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
