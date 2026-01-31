# Change: スライド生成のリトライ処理を共通ユーティリティ化

## Why
リトライ処理が個別関数内に散在すると、回数/遅延/バックオフの参照ミスやログの不統一が起きます。`RetryConfig` を単一の真実として扱い、共通ユーティリティで再利用する形に整理します。

## What Changes
- スライド生成のリトライ処理を共通ユーティリティ（例: デコレータ/ヘルパー）へ抽出する
- `RetryConfig` の参照を強制し、パラメータの重複定義を排除する

## Impact
- Affected specs: `openspec/specs/config-management/spec.md`
- Affected code: `src/movie_generator/slides/generator.py`, `src/movie_generator/utils/retry.py`
