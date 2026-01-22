# data-models Spec Delta

## ADDED Requirements

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
