# Change: ブログ画像抽出ロジックの関数分割（フィルタ/解決/正規化）

## Why
画像抽出は「候補収集」「属性抽出」「相対 URL 解決」「aria-describedby 解決」「フィルタリング」など複数責務があり、単一関数だとネストが深くなりやすいです。純粋関数化と責務分割で可読性とテスト容易性を高めます。

## What Changes
- 画像抽出処理を責務別関数へ分割する（振る舞いは維持）
- フィルタリング基準を独立させ、テストで固定する

## Impact
- Affected specs: `openspec/specs/video-generation/spec.md`
- Affected code: `src/movie_generator/content/parser.py`
