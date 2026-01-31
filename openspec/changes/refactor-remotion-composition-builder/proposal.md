# Change: composition.json 生成の引数整理（ビルダー/設定オブジェクト化）

## Why
composition.json の生成処理が長い関数・多数引数に依存すると、デフォルト値や後方互換の扱いが分散しやすく、変更時に漏れが起きます。生成の責務を集約し、後方互換の判断を一箇所に寄せるためのリファクタリングを提案します。

## What Changes
- composition.json 生成の入力を設定オブジェクト（builder/param object）に集約する
- 後方互換のデフォルト付与（speaker 情報欠落時など）を生成側に集約する

## Impact
- Affected specs: `openspec/specs/video-rendering/spec.md`
- Affected code: `src/movie_generator/video/remotion_renderer.py`
