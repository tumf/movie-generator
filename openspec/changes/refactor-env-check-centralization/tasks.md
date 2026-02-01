## 1. Implementation
- [ ] 1.1 `PROJECT_ROOT` や最小解像度などの共通値/解決ロジックを 1 箇所に集約する（検証: 重複実装が削除されることを確認）

## 2. Tests
- [ ] 2.1 `PROJECT_ROOT` の有無でパス解決が変わるケースをユニットテストで検証する（検証: `uv run pytest -k project_root -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
