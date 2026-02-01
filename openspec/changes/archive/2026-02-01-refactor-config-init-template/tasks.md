## 1. Implementation
- [x] 1.1 デフォルト YAML をテンプレートとして切り出す（検証: `config init` がテンプレートを参照して出力することを確認）
- [x] 1.2 テンプレートの更新が差分として追いやすい配置にする（検証: テンプレートが単一ファイルで管理されることを確認）

## 2. Tests
- [x] 2.1 `config init` 出力が `load_config()` で検証できることをテストする（検証: `uv run pytest -k config_init -v`）

## 3. Verification
- [x] 3.1 全テストが通る（検証: `uv run pytest`）

## Acceptance #1 Failure Follow-up
- [x] src/movie_generator/config.py: write_config_to_file() creates missing parent directories; update to error when output directory does not exist to satisfy openspec/changes/refactor-config-init-template/specs/config-management/spec.md Scenario "Invalid output path".

## Acceptance #2 Failure Follow-up
- [x] openspec/changes/refactor-config-init-template/specs/config-management/spec.md の「Generated config is valid」要件に対し、`src/movie_generator/templates/default_config.yaml` の `video.background` / `video.bgm` がデフォルト値と一致せず `load_config()` で差分が出るため、テンプレートをデフォルトと一致させる（例: コメント化/削除/None 相当）。
- [x] `src/movie_generator/templates/default_config.yaml` が `assets/backgrounds/default-background.mp4` と `assets/bgm/default-bgm.mp3` を参照しているが実体が存在せず、`src/movie_generator/config.py` の `validate_config()` が生成設定で失敗するため、テンプレート/検証/同梱資産の整合を取る。
