# Change: LLMベースURLの設定追加

## Why
OpenRouterのベースURLがハードコードされており、プロキシやローカルエンドポイントへの切り替えができないため、設定ファイルで指定可能にする。

## What Changes
- `llm.base_url` と `slides.llm.base_url` を追加してベースURLを設定可能にする
- LLM呼び出し時に設定値を参照する
- `config/default.yaml` と `config init` 出力に反映する

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/config.py`, `config/default.yaml`, `src/movie_generator/script/generator.py`, `src/movie_generator/slides/generator.py`, `src/movie_generator/audio/furigana.py`, `src/movie_generator/agent/agent_loop.py`
