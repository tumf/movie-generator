# Change: --scenes の範囲パースを共通化しガード句で単純化

## Why
`--scenes` のパースは複数コマンドで共有される重要な入力ですが、エッジケースが多く、分岐が深くなりがちです。入力エラーの一貫性とテスト容易性を高めるため、共通ユーティリティ化とガード句による単純化を提案します。

## What Changes
- `--scenes` のパース/検証を共通関数へ集約する
- 不正入力時のエラーメッセージと終了コードをコマンド間で統一する
- パース実装をガード句中心に整理し、ネストを浅くする（振る舞いは変えない）

## Impact
- Affected specs: `openspec/specs/cli-interface/spec.md`
- Affected code: `src/movie_generator/cli.py`（scene range パース周辺）、共通ユーティリティ
