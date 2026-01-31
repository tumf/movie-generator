## 1. Implementation
- [x] 1.1 `generate_script()` を段階別の小関数に分割する（検証: 各段階が個別関数として切り出されていることを確認）
- [x] 1.2 レスポンス検証/パースを純粋関数化し、I/O から分離する（検証: ユニットテストで LLM 呼び出しなしにパースを検証できる）

## 2. Tests
- [x] 2.1 単一話者モードのパースをフィクスチャ JSON で検証するテストを追加する（検証: `uv run pytest -k single_speaker -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）
