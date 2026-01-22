# audio-synthesis Spec Delta

## ADDED Requirements

### Requirement: Use Reading Field for Synthesis

音声合成時に `reading` フィールドを使用して正確な発音を実現する SHALL。

#### Scenario: Synthesize with Reading Field
- **GIVEN** `Phrase` オブジェクトに `reading` フィールドが設定されている
- **WHEN** `synthesize_from_texts_async()` が呼び出される
- **THEN** `reading` の値が VOICEVOX に渡される
- **AND** `text` は字幕表示用として保持される

#### Scenario: Skip Dictionary Processing with Reading
- **GIVEN** `Phrase` オブジェクトに `reading` フィールドが設定されている
- **WHEN** 音声合成処理が実行される
- **THEN** 既存の辞書登録処理（形態素解析・LLM読み取得）はスキップされる
- **AND** `reading` が直接 VOICEVOX に渡される

#### Scenario: Katakana Reading Format
- **GIVEN** `reading` フィールドがカタカナ形式で設定されている
- **WHEN** VOICEVOX で合成される
- **THEN** 正確な発音で音声が生成される
- **AND** 助詞「ワ」「エ」「オ」は正しく発音される

### Requirement: Backward Compatibility

既存の辞書処理との互換性を維持する SHALL。

#### Scenario: Fallback to Dictionary Processing
- **GIVEN** `Phrase` オブジェクトに `reading` フィールドがない（None）
- **WHEN** 音声合成処理が実行される
- **THEN** 既存の辞書登録処理が実行される
- **AND** `pronunciations` 辞書が使用される

**Note**: 新しいスクリプトでは `reading` は必須だが、古いスクリプトとの互換性のためフォールバック処理を残す。
