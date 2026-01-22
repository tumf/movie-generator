## 1. 実装
- [ ] 1.1 `AudioConfig` に `pronunciation_model` を追加する（完了条件: `src/movie_generator/config.py` にフィールドが存在し、`load_config()` で読める）
- [ ] 1.2 `VideoConfig` に `render_concurrency` と `render_timeout_seconds` を追加する（完了条件: `src/movie_generator/config.py` のスキーマに反映される）
- [ ] 1.3 `config/default.yaml` と `movie-generator config init` 出力に新フィールドを追加する（完了条件: `uv run movie-generator config init --output /tmp/config.yaml` で新フィールドが出力される）
- [ ] 1.4 発音LLM呼び出しとレンダリング実行で設定値を参照する（完了条件: 呼び出し経路で新フィールドが参照される）

## 2. 検証
- [ ] 2.1 `uv run movie-generator config validate config/default.yaml` が成功することを確認する
