# Change: スライド生成のリトライ設定統一

## Why
スライド生成のリトライ回数や遅延がハードコードされており、既存の `RetryConfig` と不整合があるため、共通定数に統一する。

## What Changes
- スライド生成のリトライ設定を `RetryConfig` に合わせる
- バックオフ計算も定数参照に統一する

## Impact
- Affected specs: `specs/config-management/spec.md`
- Affected code: `src/movie_generator/slides/generator.py`, `src/movie_generator/constants.py`
