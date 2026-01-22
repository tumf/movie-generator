# Change: 動画に背景（画像/動画）とBGM機能を追加

## Why

現在のmovie-generatorは、スライド画像と音声ナレーションのみで動画を生成している。
ユーザーからの要望として、以下の機能が求められている：

1. **背景**: 動画全体に背景画像または動画を設定し、スライドの後ろに表示
2. **BGM**: バックグラウンドミュージックを追加し、ナレーション音声とミックス

これらの機能により、より視覚的・聴覚的に魅力的な動画を生成可能になる。

## What Changes

### 背景機能
- グローバル設定 (`video.background`) で動画全体の背景を指定
- セクション単位でのオーバーライド (`section.background`) をサポート
- 背景タイプ: 画像（png/jpg）、動画（mp4/webm）
- 背景がない場合のデフォルト動作: 黒背景（現状維持）

### BGM機能
- グローバル設定 (`video.bgm`) でBGMを指定
- 音量調整（volume: 0.0-1.0）
- フェードイン/フェードアウト（duration_seconds）
- ループ再生（デフォルト: true）
- ナレーション音声との適切なミキシング

### アセット管理
- 背景/BGMファイルが見つからない場合のフォールバック動作
- 相対パス/絶対パスの両方をサポート

## Impact

- **影響するスペック**:
  - `config-management`: 背景・BGM設定フィールド追加
  - `video-rendering`: 背景レンダリング、BGMミキシング
  - `data-models`: Section.backgroundフィールド追加

- **影響するコード**:
  - `src/movie_generator/config.py`: BackgroundConfig, BgmConfig追加
  - `src/movie_generator/video/remotion_renderer.py`: composition.jsonに背景・BGM情報追加
  - `src/movie_generator/video/templates.py`: Remotionテンプレートに背景・BGMサポート追加
  - Remotion側TypeScript: BackgroundLayer, BgmAudio コンポーネント追加

- **後方互換性**:
  - 背景・BGM設定がない場合は現状通り動作（黒背景、BGMなし）
  - 既存の設定ファイルは変更不要
