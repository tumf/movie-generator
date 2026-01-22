# Implementation Tasks

## 1. 設定モデルの追加

- [x] 1.1 `BackgroundConfig` Pydanticモデルを作成
  - `type`: "image" | "video"
  - `path`: str（ファイルパス）
  - `fit`: "cover" | "contain" | "fill" (デフォルト: "cover")
- [x] 1.2 `BgmConfig` Pydanticモデルを作成
  - `path`: str（ファイルパス）
  - `volume`: float (0.0-1.0, デフォルト: 0.3)
  - `fade_in_seconds`: float (デフォルト: 2.0)
  - `fade_out_seconds`: float (デフォルト: 2.0)
  - `loop`: bool (デフォルト: true)
- [x] 1.3 `VideoConfig` に `background` と `bgm` フィールドを追加
- [x] 1.4 設定バリデーション（ファイル存在チェック、範囲チェック）を実装

## 2. データモデルの拡張

- [x] 2.1 `Section` モデルに `background` オプショナルフィールドを追加
- [x] 2.2 スクリプトYAMLパーサーでセクション背景を読み込み

## 3. Composition JSON 拡張

- [x] 3.1 `composition.json` に `background` フィールドを追加
- [x] 3.2 `composition.json` に `bgm` フィールドを追加
- [x] 3.3 セクションごとの背景オーバーライドを `phrases` に追加
- [x] 3.4 背景/BGMアセットを `public/` にコピーまたはシンボリックリンク

## 4. Remotion テンプレート拡張

- [x] 4.1 `BackgroundLayer` コンポーネントを作成
  - 画像背景: `<Img>` コンポーネント
  - 動画背景: `<Video>` コンポーネント with loop
  - fit プロパティ対応
- [x] 4.2 `BgmAudio` コンポーネントを作成
  - `<Audio>` コンポーネント with volume
  - フェードイン/フェードアウト: `interpolate()` で実装
  - ループ対応
- [x] 4.3 `VideoGenerator.tsx` に BackgroundLayer と BgmAudio を統合
- [x] 4.4 レイヤー順序: Background → Slide → Character → Subtitle

## 5. ナレーション・BGMミキシング

- [x] 5.1 BGMとナレーションの音量バランス設定
- [x] 5.2 ナレーション再生中のBGM自動ダッキング検討（オプション、将来拡張）
  - 注: Non-Goalとして設定済み。将来的に必要であれば別途実装

## 6. テスト

- [x] 6.1 `BackgroundConfig` バリデーションテスト
- [x] 6.2 `BgmConfig` バリデーションテスト
- [x] 6.3 セクション背景オーバーライドテスト
  - 注: composition.json生成テストでカバー済み
- [x] 6.4 composition.json 生成テスト
  - 注: 統合テストでカバー済み
- [ ] 6.5 E2Eテスト（背景画像 + BGM付き動画生成）
  - 注: 実際のアセットファイルが必要なため、手動テスト推奨

## 7. ドキュメント

- [x] 7.1 設定例を `config/examples/` に追加
- [x] 7.2 スクリプト例（セクション背景オーバーライド）を追加
