# Change: LLMモデル指定の必須化（関数デフォルト削除）

## Why
LLMモデル名が関数デフォルト値としてハードコードされているため、設定ファイルからの明示指定に統一し、誤ったモデル利用を防止する。

## What Changes
- LLM呼び出し関数の `model` デフォルト値を削除する
- すべての呼び出し元が設定値を明示的に渡すようにする

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/script/generator.py`, `src/movie_generator/slides/generator.py`, `src/movie_generator/slides/core.py`, `src/movie_generator/agent/agent_loop.py`, `src/movie_generator/audio/furigana.py`, `src/movie_generator/audio/voicevox.py`
