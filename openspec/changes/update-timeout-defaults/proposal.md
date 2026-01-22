# Change: タイムアウト値の定数化と参照統一

## Why
複数のモジュールでタイムアウト値がハードコードされており、調整や検証が難しいため、共通の定数に集約する。

## What Changes
- `TimeoutConstants` を追加してタイムアウト既定値を集約する
- HTTP取得/LLM呼び出し/画像生成/レンダリング等のタイムアウト参照を統一する

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/constants.py`, `src/movie_generator/content/fetcher.py`, `src/movie_generator/script/generator.py`, `src/movie_generator/slides/generator.py`, `src/movie_generator/audio/furigana.py`, `src/movie_generator/assets/downloader.py`, `src/movie_generator/video/remotion_renderer.py`, `src/movie_generator/mcp/client.py`
