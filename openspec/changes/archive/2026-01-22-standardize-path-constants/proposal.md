# Change: 生成パス規約と最小解像度の定数化

## Why
生成ファイル名フォーマット、最小解像度、Docker環境のプロジェクトルートがハードコードされており、保守性が低いため定数・環境変数に集約する。

## What Changes
- 生成アセットのファイル名フォーマットを定数化する
- 最小解像度の基準値を定数化し、参照を統一する
- Docker環境のプロジェクトルートを環境変数で上書き可能にする

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/constants.py`, `src/movie_generator/slides/generator.py`, `src/movie_generator/audio/voicevox.py`, `src/movie_generator/video/remotion_renderer.py`
