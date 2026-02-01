## 1. Implementation
- [ ] 1.1 scene range のパース/検証を共通ユーティリティへ移動する（検証: `audio/slides/video/generate` の各コマンドから同一関数が呼ばれることを確認）
- [ ] 1.2 不正入力（例: `--scenes a-b`, `--scenes 0`, `--scenes 3-2`）のエラー文言を統一する（検証: 追加テストで確認）

## 2. Tests
- [ ] 2.1 scene range パーサーのユニットテストを追加する（検証: `uv run pytest -k scene -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
