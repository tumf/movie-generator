## MODIFIED Requirements

### Requirement: Backward Compatibility

既存の辞書処理との互換性を維持する SHALL。

#### Scenario: Fallback to Dictionary Processing
- **GIVEN** `Phrase` オブジェクトに `reading` フィールドがない（None または空文字列）
- **WHEN** 音声合成処理が実行される
- **THEN** 既存の形態素解析による辞書登録処理が実行される
- **AND** `config.pronunciation.custom` の手動辞書が使用される

#### Scenario: Reading Field Takes Priority
- **GIVEN** `Phrase` オブジェクトに `reading` フィールドが設定されている
- **WHEN** 音声合成処理が実行される
- **THEN** `reading` の値が直接 VOICEVOX に渡される
- **AND** 辞書登録処理はスキップされる

**Note**: `pronunciations` フィールドは削除されました。`reading` フィールドまたは `config.pronunciation.custom` による手動辞書設定のみがサポートされます。
