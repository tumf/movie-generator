## 1. Implementation
- [ ] 1.1 Remotion セットアップを「初期化」「TS 生成」「workspace 更新」「リンク作成」に分割する（検証: 各段階が個別関数になっていることを確認）
- [ ] 1.2 失敗時に段階名を含むエラーメッセージを返す（検証: 例外メッセージのユニットテスト）

## 2. Tests
- [ ] 2.1 外部コマンド実行をモックしてセットアップの制御フローを検証する（検証: `uv run pytest -k remotion -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
