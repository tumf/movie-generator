# 実装タスク

## 1. データモデルの拡張

- [x] 1.1 `Persona`データモデルの作成（`src/movie_generator/config.py`）
  - `PersonaConfig`クラス追加（id, name, character, synthesizer, subtitle_color, avatar_image）
  - `SynthesizerConfig`基底クラス追加
  - `VoicevoxSynthesizerConfig`派生クラス追加

- [x] 1.2 `Phrase`データクラスの拡張（`src/movie_generator/script/phrases.py`）
  - `persona_id: str`フィールド追加
  - `persona_name: str`フィールド追加
  - デフォルト値の設定（後方互換性）

- [x] 1.3 `Config`モデルの拡張（`src/movie_generator/config.py`）
  - `personas: list[PersonaConfig]`フィールド追加
  - `NarrationConfig`に`mode`フィールド追加（"single" | "dialogue"）
  - バリデーションロジック追加（ペルソナID重複チェック）

- [x] 1.4 設定ファイルのサンプル更新
  - `config/multi-speaker-example.yaml`: 対話形式設定例の作成
  - コメントによる説明追加

## 2. スクリプト生成の拡張

- [x] 2.1 `Dialogue`データモデルの作成（`src/movie_generator/script/generator.py`）
  - `Dialogue`クラス追加（persona_id, narration）
  - `ScriptSection`に`dialogues`フィールド追加

- [x] 2.2 対話形式プロンプトテンプレートの追加
  - `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA`追加
  - `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN`追加
  - ペルソナキャラクター情報の埋め込み

- [x] 2.3 `generate_script()`関数の拡張
  - `personas`パラメータ追加
  - `mode`パラメータ追加
  - モードに応じたプロンプト選択ロジック

- [x] 2.4 対話形式レスポンスのパース処理
  - `dialogues`配列のパース
  - ペルソナID検証
  - フレーズへの話者情報追加

## 3. 音声合成の抽象化

- [x] 3.1 `AudioSynthesizer`抽象基底クラスの作成（新ファイル: `src/movie_generator/audio/synthesizer.py`）
  - `initialize()`抽象メソッド
  - `synthesize_phrase()`抽象メソッド
  - `synthesize_phrases()`抽象メソッド

- [x] 3.2 `VoicevoxSynthesizer`のリファクタリング
  - `AudioSynthesizer`を継承
  - 既存のロジックを維持
  - テストの更新

- [ ] 3.3 `SynthesizerFactory`の実装（`src/movie_generator/audio/synthesizer.py`）
  - **スキップ**: 現在はVOICEVOXのみサポートのため不要
  - 将来的に複数エンジンをサポートする際に実装予定

- [x] 3.4 ペルソナごとの音声合成ロジック（CLIまたはプロジェクト管理層）
  - フレーズの`persona_id`に応じたSynthesizer選択（`cli.py`に実装）
  - 複数Synthesizerインスタンスの管理
  - 音声ファイル名の維持（`original_index`使用）

## 4. 動画レンダリングの拡張

- [x] 4.1 `_get_persona_fields()`ヘルパー関数の追加（`src/movie_generator/video/remotion_renderer.py`）
  - ペルソナ情報の検索ロジック
  - `personaId`, `personaName`, `subtitleColor`フィールドの取得
  - composition.json生成時にペルソナ情報を含める

- [x] 4.2 Remotion TypeScript型定義の更新（`src/movie_generator/video/templates.py`）
  - `PhraseData`インターフェースに話者フィールド追加（`personaId`, `personaName`, `subtitleColor`）
  - オプショナル型の適切な設定

- [x] 4.3 `AudioSubtitleLayer`コンポーネントの拡張
  - `personaName`, `subtitleColor`プロパティ追加
  - デフォルト色の設定（#FFFFFF）
  - `WebkitTextStroke`への色適用
  - 複数話者時のペルソナ名表示機能

- [ ] 4.4 composition.jsonスキーマのドキュメント更新
  - **保留**: 将来的にドキュメント整備時に実施

## 5. CLI統合

- [x] 5.1 `movie-generator generate`コマンドの更新
  - ペルソナ設定の読み込み
  - モード検出ロジック（`config.personas`の存在確認）
  - 単一話者と対話形式の分岐処理

- [ ] 5.2 エラーメッセージの改善
  - **保留**: 基本機能が動作した後に改善予定
  - 不明なペルソナIDのエラー
  - ペルソナ設定の検証エラー

## 6. テスト

- [x] 6.1 単体テストの追加
  - `tests/test_multi_speaker.py`: ペルソナ設定のバリデーション
  - `test_persona_config.py`機能含む
  - Phraseモデル拡張のテスト含む

- [ ] 6.2 統合テストの追加
  - **保留**: E2E機能動作確認後に追加
  - 単一話者動画の生成（新形式設定）
  - 2話者対話動画の生成
  - 3話者以上の対話動画の生成

- [x] 6.3 既存テストの更新
  - テンプレート生成テストを更新（`tests/test_template_generation.py`）
  - 既存テストとの互換性確認

## 7. ドキュメント

- [ ] 7.1 README.mdの更新
  - ペルソナ設定の説明
  - 対話形式動画の生成方法
  - サンプル設定の追加

- [ ] 7.2 設定ガイドの作成（`docs/PERSONA_CONFIGURATION.md`）
  - ペルソナの定義方法
  - VOICEVOX speaker_idの一覧
  - 字幕色の選び方
  - サンプル設定集

- [ ] 7.3 移行ガイドの作成（`docs/MIGRATION_TO_PERSONA.md`）
  - 旧設定形式から新形式への書き換え方法
  - Breaking Changesの説明
  - トラブルシューティング

## 8. サンプルとデモ

- [x] 8.1 サンプル設定ファイルの作成
  - `config/multi-speaker-example.yaml`: 2話者対話設定完成

- [ ] 8.2 デモ動画の生成
  - **保留**: 実装完了後に動作確認として実施
  - 単一話者デモ
  - 2話者対話デモ（ずんだもん × 四国めたん）

## 実装順序のノート

1. **Phase 1 (1.1-1.4)**: データモデルを先に整備し、型安全性を確保
2. **Phase 2 (2.1-2.4, 3.1-3.4)**: スクリプト生成と音声合成を並行実装可能
3. **Phase 3 (4.1-4.4)**: ビデオレンダリングは音声合成完了後
4. **Phase 4 (5.1-8.2)**: CLI統合とテスト、ドキュメント整備

各タスクは小さく分割されており、1つずつ完了していくことで段階的に機能を追加できます。
