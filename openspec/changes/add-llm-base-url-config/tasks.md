## 1. 実装
- [ ] 1.1 `LLMConfig` と `SlidesLLMConfig` に `base_url` を追加する（完了条件: `src/movie_generator/config.py` にフィールドが存在する）
- [ ] 1.2 `config/default.yaml` と `movie-generator config init` 出力に `base_url` を追加する（完了条件: 初期化出力に反映される）
- [ ] 1.3 `script`/`slides`/`audio`/`agent` のLLM呼び出しで `base_url` を参照する（完了条件: ハードコードURLがなくなる）

## 2. 検証
- [ ] 2.1 `uv run movie-generator config validate config/default.yaml` が成功することを確認する
