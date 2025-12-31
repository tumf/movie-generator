# Audio Synthesis Specification

## Purpose

This specification defines the audio synthesis system for the movie generator application. The system provides an abstraction layer for multiple speech synthesis engines, supports per-persona voice synthesis, and manages pronunciation dictionaries. This enables multi-speaker dialogue videos with different voice characteristics for each persona.
## Requirements
### Requirement: Speech Synthesis Engine Abstraction

The system SHALL provide an abstraction interface that supports multiple speech synthesis engines.

#### Scenario: VOICEVOX Speech Synthesis
- **GIVEN** a persona's `synthesizer.engine` is set to `"voicevox"`
- **WHEN** phrase audio synthesis is requested
- **THEN** audio is generated using the VOICEVOX engine
- **AND** the `speaker_id` and `speed_scale` parameters are applied

#### Scenario: Unsupported Engine
- **GIVEN** a persona's `synthesizer.engine` is set to an unsupported engine (e.g., `"coefont"`)
- **WHEN** audio synthesis is initialized
- **THEN** an error is raised
- **AND** the error message indicates "unsupported engine"

#### Scenario: Engine-Specific Parameters
- **GIVEN** a persona's `synthesizer` contains arbitrary parameters
- **WHEN** the corresponding engine is implemented
- **THEN** those parameters are applied to the audio synthesis

### Requirement: Per-Persona Audio Synthesis

The system SHALL synthesize audio according to the persona assigned to each phrase.

#### Scenario: Multi-Persona Audio Synthesis
- **GIVEN** a phrase list:
  ```
  Phrase(text="やっほー！", persona_id="zundamon")
  Phrase(text="こんにちは", persona_id="metan")
  ```
- **AND** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      synthesizer: {engine: "voicevox", speaker_id: 3}
    - id: "metan"
      synthesizer: {engine: "voicevox", speaker_id: 2}
  ```
- **WHEN** `synthesize_phrases()` is called
- **THEN** phrase 0 is synthesized with speaker_id=3
- **AND** phrase 1 is synthesized with speaker_id=2

#### Scenario: Unknown Persona ID Error
- **GIVEN** a phrase has `persona_id="unknown"`
- **AND** no persona with ID `"unknown"` is defined
- **WHEN** audio synthesis is executed
- **THEN** an error is raised
- **AND** the error message includes the unknown persona ID

### Requirement: Per-Persona Pronunciation Dictionary

Each persona SHALL support having an independent pronunciation dictionary (optional in current version).

#### Scenario: Shared Pronunciation Dictionary
- **GIVEN** the global pronunciation dictionary has `"ENGINE" -> "エンジン"`
- **WHEN** audio synthesis is executed for any persona
- **THEN** all personas use this dictionary

#### Scenario: Persona-Specific Pronunciation Dictionary (Future Extension)
- **GIVEN** persona A has `"東京" -> "トーキョー"`
- **AND** persona B has `"東京" -> "とうきょう"`
- **WHEN** audio synthesis is executed for each persona
- **THEN** different pronunciations are applied per persona

### Requirement: Audio File Naming Convention

Generated audio files SHALL be named using the phrase's `original_index`.

#### Scenario: Audio File Name
- **GIVEN** a phrase's `original_index` is 5
- **WHEN** audio synthesis is executed
- **THEN** the filename is `phrase_0005.wav`
- **AND** the persona ID is not included (original_index ensures uniqueness)

### Requirement: Audio Synthesis Caching

When an existing audio file is present, re-synthesis SHALL be skipped.

#### Scenario: Skip Existing Audio
- **GIVEN** `phrase_0000.wav` already exists
- **AND** the file size is greater than 0 bytes
- **WHEN** `synthesize_phrases()` is called
- **THEN** audio synthesis for that phrase is skipped
- **AND** a "Skipping existing audio" message is displayed

#### Scenario: Regenerate Corrupted Files
- **GIVEN** `phrase_0000.wav` exists but has 0 byte size
- **WHEN** `synthesize_phrases()` is called
- **THEN** the audio is regenerated

### Requirement: Reading Field for Synthesis

The audio synthesis system SHALL use the `reading` field when available for accurate pronunciation.

#### Scenario: Synthesize with reading field
- **GIVEN** a phrase with:
  ```python
  Phrase(text="明日は晴れです", reading="アシタワハレデス")
  ```
- **WHEN** audio synthesis is executed
- **THEN** the `reading` field is passed to the synthesis engine
- **AND** the synthesized audio reflects the specified pronunciation

#### Scenario: Fallback to text field
- **GIVEN** a phrase with no `reading` field:
  ```python
  Phrase(text="明日は晴れです", reading="")
  ```
- **WHEN** audio synthesis is executed
- **THEN** the `text` field is used as fallback
- **AND** a warning is logged about missing `reading`

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/audio-synthesis/spec.md`.

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
