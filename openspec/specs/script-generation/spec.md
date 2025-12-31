# Script Generation Specification

## Purpose

This specification defines the script generation system for the movie generator application. The system generates narration scripts using LLM prompts, supporting both single-speaker narration and multi-persona dialogue formats. The generated scripts include speaker assignments, enabling multi-character conversational videos.
## Requirements
### Requirement: Dialogue Format Prompt

The system SHALL be able to generate dialogue-style scripts with multiple personas.

#### Scenario: Generate Dialogue Script
- **GIVEN** persona configuration:
  ```yaml
  personas:
    - id: "zundamon"
      character: "元気で明るい東北の妖精"
    - id: "metan"
      character: "優しくて落ち着いた四国の妖精"
  ```
- **AND** `narration.mode: "dialogue"` is configured
- **WHEN** `generate_script()` is called
- **THEN** a dialogue format prompt is sent to the LLM
- **AND** each persona's `character` configuration is included

#### Scenario: Parse Dialogue Format Response
- **GIVEN** the LLM returns the following response:
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "dialogues": [
          {
            "persona_id": "zundamon",
            "narration": "やっほー！"
          },
          {
            "persona_id": "metan",
            "narration": "こんにちは！"
          }
        ],
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** the response is parsed
- **THEN** 2 phrases are generated
- **AND** phrase 0 has `persona_id="zundamon"`
- **AND** phrase 1 has `persona_id="metan"`

### Requirement: Single-Speaker Mode Support

The system SHALL continue to support the traditional single-speaker mode.

#### Scenario: Generate Single-Speaker Script
- **GIVEN** `narration.mode: "single"` is configured
- **AND** only one persona is defined
- **WHEN** `generate_script()` is called
- **THEN** the traditional single-speaker prompt is used
- **AND** all phrases are assigned to the same persona

#### Scenario: Parse Single-Speaker Response
- **GIVEN** the LLM returns a traditional format response:
  ```json
  {
    "sections": [
      {
        "title": "イントロ",
        "narration": "やっほー！ずんだもんなのだ。",
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **WHEN** the response is parsed
- **THEN** phrase splitting is executed
- **AND** all phrases are assigned to `personas[0].id`

### Requirement: Automatic Persona Role Assignment

The dialogue format prompt SHALL assign appropriate roles to personas.

#### Scenario: Two-Persona Roles
- **GIVEN** two personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** persona 0 is designated as the "explainer" role
- **AND** persona 1 is designated as the "questioner/responder" role

#### Scenario: Three or More Persona Roles
- **GIVEN** three or more personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** roles are assigned based on each persona's character traits
- **AND** the LLM is instructed to generate natural conversation

### Requirement: Add Speaker Information to Phrases

Generated phrases SHALL include speaker information.

#### Scenario: Add Speaker Information to Phrase Objects
- **GIVEN** a dialogue format response is parsed
- **WHEN** `Phrase` objects are created
- **THEN** the `persona_id` field is set
- **AND** the `persona_name` field is set

#### Scenario: Unknown Persona ID Error
- **GIVEN** the LLM response includes `persona_id="unknown"`
- **AND** no persona with ID `"unknown"` is defined
- **WHEN** the response is parsed
- **THEN** an error is raised
- **AND** the error message includes the unknown persona ID

### Requirement: Language-Specific Dialogue Prompts

The system SHALL provide dialogue format prompts for Japanese and English.

#### Scenario: Japanese Dialogue Prompt
- **GIVEN** `language="ja"` is configured
- **AND** `narration.mode="dialogue"` is configured
- **WHEN** a prompt is generated
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_JA` is used

#### Scenario: English Dialogue Prompt
- **GIVEN** `language="en"` is configured
- **AND** `narration.mode="dialogue"` is configured
- **WHEN** a prompt is generated
- **THEN** `SCRIPT_GENERATION_PROMPT_DIALOGUE_EN` is used

### Requirement: Reading Field Generation

The LLM SHALL generate a `reading` field in katakana for each narration to guide pronunciation.

#### Scenario: Generate reading field in Japanese
- **GIVEN** the narration text is "明日は晴れです"
- **WHEN** the LLM generates the script
- **THEN** the `reading` field is "アシタワハレデス"
- **AND** particle pronunciations follow Japanese rules: は→ワ, へ→エ, を→オ

#### Scenario: Generate reading field in English
- **GIVEN** the narration text is "Hello world"
- **WHEN** the LLM generates the script
- **THEN** the `reading` field is "ハローワールド"
- **AND** katakana represents English pronunciation

#### Scenario: Prompt includes reading field instruction
- **GIVEN** any language is configured
- **WHEN** the script generation prompt is constructed
- **THEN** the prompt MUST include instructions to generate the `reading` field
- **AND** the prompt MUST specify katakana format and particle pronunciation rules

---

**Note**: This specification was created by archiving the change `add-multi-speaker-dialogue`.
Original Japanese version archived in `openspec/changes/archive/2025-12-31-add-multi-speaker-dialogue/specs/script-generation/spec.md`.

### Requirement: Narration Reading Field Generation

LLMがスクリプト生成時に、字幕表示用テキスト（`text`）と音声合成用読み仮名（`reading`）の両方を生成する SHALL。

#### Scenario: Generate Japanese Narration with Reading
- **GIVEN** 日本語コンテンツが入力される
- **AND** `language="ja"` が設定されている
- **WHEN** `generate_script()` が呼び出される
- **THEN** 各 narration に `text` と `reading` が含まれる
- **AND** `reading` はカタカナ形式である
- **AND** 助詞「は」は「ワ」として出力される
- **AND** 助詞「へ」は「エ」として出力される
- **AND** 助詞「を」は「オ」として出力される

#### Scenario: Generate English Narration with Reading
- **GIVEN** 英語コンテンツが入力される
- **AND** `language="en"` が設定されている
- **WHEN** `generate_script()` が呼び出される
- **THEN** 各 narration に `text` と `reading` が含まれる
- **AND** `reading` は音声合成用のテキストである

#### Scenario: Dialogue Mode with Reading
- **GIVEN** `narration.mode="dialogue"` が設定されている
- **AND** 複数のペルソナが定義されている
- **WHEN** `generate_script()` が呼び出される
- **THEN** 各 narration に `persona_id`, `text`, `reading` が含まれる

### Requirement: Reading Field Validation

`reading` フィールドは必須であり SHALL、空の場合はエラーとする MUST。

#### Scenario: Missing Reading Field Error
- **GIVEN** LLMレスポンスに `reading` フィールドがない
- **WHEN** レスポンスがパースされる
- **THEN** エラーが発生する
- **AND** エラーメッセージに「reading field is required」が含まれる

#### Scenario: Empty Reading Field Error
- **GIVEN** LLMレスポンスの `reading` が空文字列
- **WHEN** レスポンスがパースされる
- **THEN** エラーが発生する
- **AND** エラーメッセージに「reading cannot be empty」が含まれる

### Requirement: LLM Prompt Format Update

LLMプロンプトに `reading` フィールドの生成指示を追加する SHALL。

#### Scenario: Japanese Prompt Includes Reading Instructions
- **GIVEN** `language="ja"` が設定されている
- **WHEN** LLMプロンプトが生成される
- **THEN** プロンプトに以下が含まれる：
  - `reading` フィールドの説明
  - カタカナ形式の指示
  - 助詞の発音ルール（は→ワ、へ→エ、を→オ）
  - 出力JSONフォーマットに `reading` が含まれる

#### Scenario: Prompt Output Format Example
- **GIVEN** LLMプロンプトが生成される
- **WHEN** 出力形式セクションを確認する
- **THEN** 以下の形式が含まれる：
  ```json
  {
    "narrations": [
      {
        "text": "明日は晴れです",
        "reading": "アシタワハレデス"
      }
    ]
  }
  ```
