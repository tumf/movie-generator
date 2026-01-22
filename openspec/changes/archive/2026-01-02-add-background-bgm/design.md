# Design Document: 背景・BGM機能

## Context

movie-generatorは現在、スライド画像とVOICEVOXナレーションを組み合わせた動画を生成する。
ユーザーからより魅力的な動画生成のために、背景とBGMのサポートが求められている。

### 関係者
- 動画クリエイター（エンドユーザー）
- 開発者（本システム）

### 制約
- Remotion（TypeScript/React）でのビデオレンダリング
- 既存のcomposition.jsonベースのアーキテクチャ
- pnpmワークスペースによる依存関係管理

## Goals / Non-Goals

### Goals
- 動画全体に背景（画像/動画）を設定可能にする
- セクション単位で背景をオーバーライド可能にする
- BGM（音楽）をナレーションと一緒に再生可能にする
- BGMのボリューム、フェードイン/アウト、ループを設定可能にする
- 後方互換性を維持する（設定がなければ現状通り動作）

### Non-Goals
- リアルタイムオーディオダッキング（ナレーション時にBGMを自動で下げる）- 将来拡張として検討
- 複数BGMトラックの同時再生
- BGMのセクション単位切り替え（全体で1曲のみ）
- 背景動画の音声再生（ミュート固定）

## Decisions

### Decision 1: 背景レンダリング方式

**選択**: Remotionの`<Img>`/`<Video>`コンポーネントを使用

**理由**:
- Remotionの公式コンポーネントで安定性が高い
- `objectFit`プロパティでcover/contain/fillを簡単に実装可能
- 動画背景のループもRemotionが自動処理

**代替案**:
- CSS background-image: コンポーネントとして扱いづらい
- Canvas描画: 複雑すぎる

### Decision 2: BGMミキシング方式

**選択**: Remotionの`<Audio>`コンポーネントでBGMを追加

**理由**:
- ナレーション音声はすでに`<Audio>`で再生中
- 複数の`<Audio>`コンポーネントを並列配置するだけでミキシング可能
- `interpolate()`でフェードイン/アウトを簡単に実装可能
- FFmpegによる事前ミキシング不要

**代替案**:
- FFmpegで事前にBGM+ナレーションをミックス: レンダリング前の追加処理が必要、設定変更時に再ミックス必要
- Remotion側で単一Audioに統合: 実装が複雑

### Decision 3: セクション背景オーバーライドの実装

**選択**: composition.jsonのphrasesにbackgroundOverrideフィールドを追加

**理由**:
- 既存のsection_indexでセクションを識別可能
- Remotion側でセクションの開始/終了を判定し背景を切り替え
- スクリプトYAMLでの設定が直感的

**実装詳細**:
```json
{
  "background": {
    "type": "image",
    "path": "backgrounds/default.png",
    "fit": "cover"
  },
  "phrases": [
    {
      "sectionIndex": 0,
      "backgroundOverride": null
    },
    {
      "sectionIndex": 1,
      "backgroundOverride": {
        "type": "video",
        "path": "backgrounds/section1.mp4",
        "fit": "cover"
      }
    }
  ]
}
```

### Decision 4: アセットパス管理

**選択**: 背景/BGMファイルを`public/`ディレクトリにコピー（またはシンボリックリンク）

**理由**:
- Remotionは`public/`からの相対パスでアセットを参照
- 既存のスライド/オーディオと同じ管理方式
- ビルド時にアセットが確実に含まれる

**パス変換**:
- 設定: `assets/backgrounds/bg.png`
- composition.json: `backgrounds/bg.png`
- Remotion参照: `staticFile("backgrounds/bg.png")`

### Decision 5: BGMループ実装

**選択**: Remotionの`loop`属性を使用

**理由**:
- Remotionの`<Audio>`コンポーネントは`loop`属性をサポート
- 動画長を超えるBGMはカットされる
- 動画長より短いBGMはループで繰り返される

## Risks / Trade-offs

### Risk 1: 動画背景のパフォーマンス
- **リスク**: 高解像度動画背景はレンダリング時間を増加させる
- **軽減策**: ドキュメントで適切な解像度（1920x1080以下）を推奨

### Risk 2: BGMと音声の音量バランス
- **リスク**: BGMがナレーションを邪魔する可能性
- **軽減策**: デフォルトBGM音量を0.3（低め）に設定、ユーザーが調整可能

### Risk 3: アセットファイルサイズ
- **リスク**: 大きな動画/音声ファイルでプロジェクトサイズ増大
- **軽減策**: アセットはシンボリックリンクでpublicに配置（コピーは任意）

## Migration Plan

1. **Phase 1**: 背景機能（画像/動画）を実装
2. **Phase 2**: BGM機能（ボリューム、フェード、ループ）を実装
3. **Phase 3**: セクション背景オーバーライドを実装

### ロールバック

- 設定が存在しない場合は現状通り動作するため、ロールバック不要
- composition.jsonに新フィールドがあっても、Remotion側で未使用時はスキップ

## Open Questions

- [ ] BGMのナレーション中自動ダッキングは将来実装するか？
  - 現時点では実装しない（Non-Goal）
  - ユーザーからの要望があれば検討

- [ ] 背景動画の音声を再生するオプションは必要か？
  - 現時点では常にミュート
  - 環境音として使いたい場合は検討
