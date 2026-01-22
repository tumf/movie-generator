# Implementation Tasks

## 1. コード修正

- [x] 1.1 `src/movie_generator/video/templates.py` の字幕スタイルを修正
  - [x] 180行目: `maxWidth: '80%'` を `width: '80%'` に変更

## 2. 仕様の更新

- [x] 2.1 `openspec/changes/update-subtitle-max-width/specs/video-generation/spec.md` を更新
  - [x] 技術実装の詳細を追記（width vs maxWidth の違い）

## 3. 検証

- [x] 3.1 `openspec validate update-subtitle-max-width --strict` を実行
- [x] 3.2 既存テストが正常にパスすることを確認
- [x] 3.3 実装完了（実際の動画生成での視覚的確認は運用時に実施）
