## 1. Implementation
- [ ] 1.1 スクリプト読み込み/フレーズ準備を共通関数へ抽出する（検証: `generate` と `audio generate` の両方が利用することを確認）

## 2. Tests
- [ ] 2.1 シーン範囲指定時のフレーズ選択とファイル命名（`original_index`）をユニットテストで固定する（検証: `uv run pytest -k scene_range -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
