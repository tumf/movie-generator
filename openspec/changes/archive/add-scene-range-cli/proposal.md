# Change: シーン範囲指定による部分動画出力

**Status**: ✅ Deployed
**Archived**: 2025-12-30

## Why

現在、動画生成コマンドは常にすべてのシーン（セクション）を含む動画を出力する。
デバッグや部分的なプレビュー、特定シーンの再生成のために、
コマンドライン引数でシーン範囲を指定して部分的な動画を出力できると便利。

## What Changes

- `movie-generator generate` コマンドに `--scenes` オプションを追加
- フォーマット例: `--scenes 1-3`（シーン1〜3）、`--scenes 2`（シーン2のみ）
- 指定された範囲のシーンに属するフレーズのみを動画に含める
- 出力ファイル名に範囲を反映（例: `output_scenes_1-3.mp4`）

## Impact

- 影響する仕様: `video-generation`
- 影響するコード:
  - `src/movie_generator/cli.py` - CLIオプション追加
  - `src/movie_generator/video/remotion_renderer.py` - フレーズフィルタリング
- 後方互換性: 維持（`--scenes` 未指定時は従来通り全シーン出力）
