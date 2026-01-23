# Change: 設定フィールドの追加（発音LLM/レンダリング実行設定）

## Why
発音用LLMモデルやレンダリング実行設定がハードコードされており、運用環境に合わせた調整ができないため、設定ファイルで管理可能にする。

## What Changes
- `audio.pronunciation_model` を追加して発音LLMモデルを設定可能にする
- `video.render_concurrency` と `video.render_timeout_seconds` を追加してレンダリング実行設定を設定可能にする
- `config/default.yaml` と `config init` 出力に新フィールドを反映する

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/config.py`, `config/default.yaml`, `src/movie_generator/cli.py`
