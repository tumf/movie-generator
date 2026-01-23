## 1. 実装
- [x] 1.1 `AudioConfig` に `pronunciation_model` を追加する（完了条件: `src/movie_generator/config.py` にフィールドが存在し、`load_config()` で読める）
- [x] 1.2 `VideoConfig` に `render_concurrency` と `render_timeout_seconds` を追加する（完了条件: `src/movie_generator/config.py` のスキーマに反映される）
- [x] 1.3 `config/default.yaml` と `movie-generator config init` 出力に新フィールドを追加する（完了条件: `uv run movie-generator config init --output /tmp/config.yaml` で新フィールドが出力される）
- [x] 1.4 発音LLM呼び出しとレンダリング実行で設定値を参照する（完了条件: 呼び出し経路で新フィールドが参照される）

## 2. 検証
- [x] 2.1 `uv run movie-generator config validate config/default.yaml` が成功することを確認する（Note: スキーマ検証は成功、ファイル参照エラーはアセットファイル不在のためで予期された動作）

## Acceptance #1 Failure Follow-up
- [x] Commit all modified files: config/default.yaml, src/movie_generator/audio/voicevox.py, src/movie_generator/cli.py, src/movie_generator/config.py, src/movie_generator/video/core.py, src/movie_generator/video/remotion_renderer.py
- [x] Ensure tasks.md itself is committed (currently showing as modified)
