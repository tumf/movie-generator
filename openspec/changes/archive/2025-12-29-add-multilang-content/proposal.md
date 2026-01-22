# Change: 複数言語対応コンテンツ生成機能の追加

## Why

現在のシステムは日本語コンテンツのみをサポートしており、グローバル展開や多言語視聴者への対応ができない。ユーザーが単一のソースコンテンツから複数言語（日本語・英語など）の動画を一括生成できるようにすることで、コンテンツの国際展開を効率化する。

## What Changes

- 設定ファイルに `content.languages` フィールドを追加し、複数言語の指定を可能にする
- スクリプト生成時に言語別のプロンプトテンプレートを使用する
- 言語ごとに個別のスクリプトファイル（`script_ja.yaml`, `script_en.yaml`）を生成する
- スライド画像を言語別サブディレクトリ（`slides/ja/`, `slides/en/`）に出力する
- 既存の単一言語設定との後方互換性を維持する

## Impact

- 影響を受ける仕様:
  - `config-management` - 設定スキーマに `languages` フィールド追加
  - `video-generation` - スクリプト・スライド生成のマルチランゲージ対応
- 影響を受けるコード:
  - `src/movie_generator/config.py` - ContentConfig に languages フィールド追加
  - `src/movie_generator/script/generator.py` - 言語別プロンプトと language パラメータ追加
  - `src/movie_generator/slides/generator.py` - 言語別ディレクトリ対応
  - `src/movie_generator/multilang.py` - 新規：複数言語統合処理
  - `scripts/generate_slides.py` - 言語別スクリプトファイル検出
  - `tests/test_config.py` - 複数言語設定テスト追加
- 破壊的変更: なし（後方互換性あり）
