## 1. 実装
- [x] 1.1 `LLMConfig` と `SlidesLLMConfig` に `base_url` を追加する（完了条件: `src/movie_generator/config.py` にフィールドが存在する）
- [x] 1.2 `config/default.yaml` と `movie-generator config init` 出力に `base_url` を追加する（完了条件: 初期化出力に反映される）
- [x] 1.3 `script`/`slides`/`audio`/`agent` のLLM呼び出しで `base_url` を参照する（完了条件: ハードコードURLがなくなる）

## 2. 検証
- [x] 2.1 `uv run movie-generator config validate config/default.yaml` が成功することを確認する

## Acceptance #1 Failure Follow-up
- [x] Commit all implementation changes: config/default.yaml, src/movie_generator/agent/agent_loop.py, src/movie_generator/audio/voicevox.py, src/movie_generator/cli.py, src/movie_generator/config.py, src/movie_generator/script/core.py, src/movie_generator/slides/core.py, src/movie_generator/slides/generator.py
- [x] Ensure git working tree is clean (`git status --porcelain` produces no output)
