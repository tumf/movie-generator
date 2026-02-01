## 1. Implementation
- [ ] 1.1 Remotion レンダリング呼び出しの引数を設定オブジェクトに集約する（検証: 呼び出し側の引数列が短くなることを確認）
- [ ] 1.2 環境チェック（例: headless shell / Docker 関連）を共通関数化する（検証: 複数箇所の重複チェックが解消されることを確認）

## 2. Tests
- [ ] 2.1 環境チェックのユニットテスト（環境変数/パスをモック）を追加する（検証: `uv run pytest -k chrome -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
