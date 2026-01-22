# Change: 複数話者による掛け合い動画生成機能の追加

**Status**: ✅ 実装完了（2025-12-31）

## Why

現在の動画生成システムは単一話者（例：ずんだもん）のナレーションのみをサポートしているが、複数のキャラクターが掛け合いで会話する形式の動画を生成したいという要望がある。例えば「ずんだもん」と「四国めたん」が交互に話しながら解説する動画などがニーズとして存在する。

これにより、以下のメリットが得られる：
- より親しみやすく、エンゲージメントの高い動画コンテンツ
- 複雑な内容を対話形式で分かりやすく説明
- 視聴者の飽きを防ぐバリエーション豊かな表現

## What Changes

- **話者（ペルソナ）の設定機能**: 複数の話者を設定ファイルで定義可能にする（名前、キャラクター性、音声合成パラメータ、字幕色など）
- **フレーズ単位での話者切り替え**: 各フレーズに話者を割り当て、フレーズごとに異なる話者で音声合成
- **LLMによる対話形式スクリプト生成**: 複数話者の掛け合いを自動生成するプロンプト対応
- **話者別字幕スタイル**: 話者ごとに異なる字幕色で表示
- **音声合成エンジンの抽象化**: VOICEVOX以外の音声合成エンジンにも対応できる設計
- **単一話者との互換性**: 話者が1人の場合も新形式で動作（旧設定形式は非サポート）

**注意**: アバター画像表示は今回のスコープ外。ただし、将来的な実装の可能性を残す設計とする。

## Impact

### 影響を受ける仕様
- `config-management`: 話者設定の追加、設定形式の変更
- `audio-synthesis`: 新規仕様 - 話者ごとの音声合成抽象化
- `script-generation`: 新規仕様 - 対話形式スクリプト生成
- `video-rendering`: 新規仕様 - 話者別字幕スタイル

### 影響を受けるコード
- `src/movie_generator/config.py`: 設定モデルの拡張
- `src/movie_generator/script/phrases.py`: `Phrase`データクラスに話者情報追加
- `src/movie_generator/script/generator.py`: 対話形式プロンプト追加
- `src/movie_generator/audio/voicevox.py`: 話者ごとの音声合成
- `output/*/remotion/src/VideoGenerator.tsx`: 話者別字幕レンダリング
- `src/movie_generator/video/remotion_renderer.py`: composition.jsonに話者情報追加

### Breaking Changes
- **設定形式の変更**: 既存の設定ファイルは新形式に書き換えが必要（ただし、単一話者の場合は1要素の配列として定義すれば動作）
- **composition.json形式の変更**: 話者情報を含む新しいフィールドを追加

## Dependencies

なし（既存の依存関係のみ使用）

## Migration Path

既存ユーザーは設定ファイルを以下のように書き換える：

**旧形式（非サポート）:**
```yaml
audio:
  speaker_id: 3
  speed_scale: 1.0
```

**新形式:**
```yaml
personas:
  - id: "zundamon"
    name: "ずんだもん"
    character: "ずんだもん"
    synthesizer:
      engine: "voicevox"
      speaker_id: 3
      speed_scale: 1.0
    subtitle_color: "#8FCF4F"
```
