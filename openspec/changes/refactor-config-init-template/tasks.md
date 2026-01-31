## 1. Implementation
- [ ] 1.1 デフォルト YAML をテンプレートとして切り出す（検証: `config init` がテンプレートを参照して出力することを確認）
- [ ] 1.2 テンプレートの更新が差分として追いやすい配置にする（検証: テンプレートが単一ファイルで管理されることを確認）

## 2. Tests
- [ ] 2.1 `config init` 出力が `load_config()` で検証できることをテストする（検証: `uv run pytest -k config_init -v`）

## 3. Verification
- [ ] 3.1 全テストが通る（検証: `uv run pytest`）
