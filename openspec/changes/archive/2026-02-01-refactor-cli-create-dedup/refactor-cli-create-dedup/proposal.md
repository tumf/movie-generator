# Change: script create と generate の共通処理を抽出して重複を削減

## Why
`script create` と `generate` で URL 取得/スクリプト生成周りの重複があると、修正時に片方だけ直して不整合が起きやすくなります。共通処理を抽出し、入口は薄く保つ方針を提案します。

## What Changes
- URL 取得/スクリプト生成の共通処理を関数として抽出し、`script create` と `generate` から呼ぶ
- 既存の CLI 引数/出力/スキップ条件の挙動は維持する

## Impact
- Affected specs: `openspec/specs/cli-interface/spec.md`
- Affected code: `src/movie_generator/cli.py`
