# Tasks: 形態素解析による自動ふりがな生成

## 実装タスク

### フェーズ1: 依存関係とコアモジュール

- [x] **T1.1**: `pyproject.toml` に `fugashi>=1.3.0`, `unidic>=1.1.0` を追加
- [x] **T1.2**: `src/movie_generator/audio/furigana.py` を新規作成
  - `MorphemeReading` データクラス
  - `FuriganaGenerator` クラス
  - `analyze()`, `get_readings_dict()`, `analyze_texts()` メソッド

### フェーズ2: 既存モジュールの拡張

- [x] **T2.1**: `PronunciationDictionary.add_from_morphemes()` メソッド追加
  - 形態素解析結果を辞書に登録
  - 既存エントリとの優先順位管理（priority=5）
- [x] **T2.2**: `VoicevoxSynthesizer` に furigana 統合
  - `enable_furigana` パラメータ追加
  - `prepare_phrases()` メソッド追加
  - `_get_furigana_generator()` ヘルパー追加

### フェーズ3: 設定

- [x] **T3.1**: `AudioConfig.enable_furigana` 設定追加
- [x] **T3.2**: `create_synthesizer_from_config()` で設定を反映
- [x] **T3.3**: デフォルト設定YAMLにコメント追加

### フェーズ4: エクスポートとテスト

- [x] **T4.1**: `audio/__init__.py` に `FuriganaGenerator`, `MorphemeReading` をエクスポート
- [x] **T4.2**: `tests/test_furigana.py` を作成
  - 基本的な形態素解析テスト
  - ユーザー報告のケース（表計算、人月、Button）
  - 辞書統合テスト
  - 優先順位テスト

## 検証

- [x] 全14テストケースがパス
- [x] 既存テスト（40件）に影響なし
- [x] 実際の読み間違いケースで改善を確認

## 完了条件

- [x] コードがマージ可能な状態
- [x] テストが全てパス
- [ ] 仕様書が完成
