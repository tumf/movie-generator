## 1. Implementation
- [x] 1.1 composition.json 生成処理の入力を設定オブジェクトにまとめる（検証: 生成関数の引数が整理されていることを確認）
- [x] 1.2 speaker 情報欠落時のデフォルト付与を生成側で統一する（検証: フィクスチャ composition を用いたユニットテストで確認）

## 2. Tests
- [x] 2.1 speaker 情報なし composition.json の互換動作をユニットテストで固定する（検証: `uv run pytest -k composition -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`)
