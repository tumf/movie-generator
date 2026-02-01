# Change: generate と audio generate のスクリプト読み込み/フレーズ化処理を共通化

## Why
`generate` と `audio generate` が同様の「スクリプト読み込み→フレーズ化→出力パス決定」を別実装で持つと、シーン範囲や命名規約の変更時に差異が生まれやすくなります。共通化により回帰リスクを下げます。

## What Changes
- スクリプト読み込みとフレーズ準備（シーン範囲適用含む）を共通化する
- 既存のスキップポリシー（既存音声を残す等）を維持する

## Impact
- Affected specs: `openspec/specs/cli-interface/spec.md`
- Affected code: `src/movie_generator/cli.py`
