# data-models Specification

## Purpose
TBD - created by archiving change refactor-dataclass-to-pydantic. Update Purpose after archive.
## Requirements
### Requirement: Pydantic-based Domain Models

All domain model classes SHALL use Pydantic `BaseModel` instead of `@dataclass` for consistent type validation and serialization.

#### Scenario: Model instantiation with validation
- **WHEN** a model is instantiated with invalid data types
- **THEN** Pydantic raises a `ValidationError` with details

#### Scenario: Model serialization to dict
- **WHEN** `model_dump()` is called on a model instance
- **THEN** the model is serialized to a Python dictionary

#### Scenario: Model deserialization from dict
- **WHEN** `Model.model_validate(data)` is called with a dictionary
- **THEN** a validated model instance is created

### Requirement: Mutable Model Support

Domain models that require field updates after creation SHALL be configured as mutable.

#### Scenario: Phrase duration update
- **WHEN** audio generation completes
- **THEN** `Phrase.duration` field can be updated in-place

#### Scenario: Phrase timing calculation
- **WHEN** `calculate_phrase_timings()` is called
- **THEN** `Phrase.start_time` fields are updated for all phrases

### Requirement: Method Preservation

Model classes with business logic methods SHALL preserve those methods after Pydantic migration.

#### Scenario: Phrase subtitle text method
- **WHEN** `Phrase.get_subtitle_text()` is called
- **THEN** text with trailing punctuation removed is returned

### Requirement: JSON Serialization Compatibility

Model classes used for JSON output SHALL maintain compatibility with existing JSON structure.

#### Scenario: CompositionData JSON output
- **WHEN** `CompositionData` is serialized to JSON for Remotion
- **THEN** the JSON structure matches the existing format expected by Remotion

#### Scenario: VideoScript JSON parsing
- **WHEN** LLM response JSON is parsed into `VideoScript`
- **THEN** the model validates and converts the data correctly

### Requirement: Narration Reading Field

The `Narration` model SHALL include a `reading` field for pronunciation guidance.

#### Scenario: Narration with reading field
- **GIVEN** a narration dictionary with `text` and `reading`:
  ```python
  {
    "text": "明日は晴れです",
    "reading": "アシタワハレデス"
  }
  ```
- **WHEN** `Narration.model_validate()` is called
- **THEN** a `Narration` instance is created with both fields

#### Scenario: Backward compatibility with missing reading
- **GIVEN** a narration dictionary with only `text`:
  ```python
  {"text": "明日は晴れです"}
  ```
- **WHEN** parsed by the script generator
- **THEN** `reading` defaults to `text` value for backward compatibility

### Requirement: Narration Data Model

`Narration` クラスに音声合成用読み仮名フィールドを追加する SHALL。

#### Scenario: Narration with Reading Field
- **GIVEN** ナレーションデータが以下の形式で与えられる：
  ```python
  {
      "text": "明日は晴れです",
      "reading": "アシタワハレデス"
  }
  ```
- **WHEN** `Narration` オブジェクトが生成される
- **THEN** `narration.text` は `"明日は晴れです"` である
- **AND** `narration.reading` は `"アシタワハレデス"` である

#### Scenario: Narration with Persona and Reading
- **GIVEN** 対話形式のナレーションデータが以下の形式で与えられる：
  ```python
  {
      "persona_id": "zundamon",
      "text": "こんにちは！",
      "reading": "コンニチワ"
  }
  ```
- **WHEN** `Narration` オブジェクトが生成される
- **THEN** `narration.persona_id` は `"zundamon"` である
- **AND** `narration.text` は `"こんにちは！"` である
- **AND** `narration.reading` は `"コンニチワ"` である

### Requirement: Phrase Reading Field

`Phrase` クラスに音声合成用読み仮名フィールドを追加する SHALL。

#### Scenario: Phrase with Reading Field
- **GIVEN** `Narration` から `Phrase` が生成される
- **WHEN** `Phrase` オブジェクトが作成される
- **THEN** `phrase.text` は字幕表示用テキストである
- **AND** `phrase.reading` は音声合成用読み仮名である

#### Scenario: Phrase Subtitle Text Method
- **GIVEN** `Phrase` オブジェクトが存在する
- **WHEN** `get_subtitle_text()` が呼び出される
- **THEN** `phrase.text` から句読点を除いたテキストが返される
- **AND** `phrase.reading` は影響を受けない

### Requirement: VideoScript Model Structure

The `VideoScript` model SHALL contain:
- `title: str` - Video title
- `description: str` - Video description
- `sections: list[ScriptSection]` - Script sections
- `role_assignments: list[RoleAssignment] | None` - Persona role assignments (for dialogue mode)

**変更内容**: `pronunciations` フィールドを削除

#### Scenario: VideoScript Model Fields

**GIVEN** a VideoScript instance
**THEN** it SHALL have `title`, `description`, `sections`, and `role_assignments` fields
**AND** it SHALL NOT have a `pronunciations` field
