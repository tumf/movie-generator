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

The dialogue format prompt SHALL assign appropriate roles to personas, and the generated script SHALL include role assignment information.

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

#### Scenario: LLM Generates Role Assignments
- **GIVEN** multiple personas are defined
- **WHEN** `generate_script()` is called with personas
- **THEN** the LLM is instructed to assign roles freely
- **AND** the LLM response includes `role_assignments` with persona_id, role, and description
- **AND** the generated `VideoScript` contains `role_assignments` field

#### Scenario: Role Assignments in Script Output
- **GIVEN** a `VideoScript` with `role_assignments` is generated
- **WHEN** the script is serialized to YAML
- **THEN** the output includes a `role_assignments` section
- **AND** each entry contains `persona_id`, `role`, and `description`

#### Scenario: Backward Compatibility Without Role Assignments
- **GIVEN** an LLM response without `role_assignments` field
- **WHEN** the response is parsed
- **THEN** the `VideoScript.role_assignments` is set to `None`
- **AND** no error is raised

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

LLMプロンプトに `reading` フィールドの生成指示を含める SHALL。

#### Scenario: Japanese Prompt Format
- **GIVEN** `language="ja"` が設定されている
- **WHEN** LLMプロンプトが生成される
- **THEN** プロンプトに以下が含まれる：
  - `reading` フィールドの説明
  - カタカナ形式の指示
  - 助詞の発音ルール（は→ワ、へ→エ、を→オ）
- **AND** `pronunciations` セクションは含まれない

#### Scenario: English Prompt Format
- **GIVEN** `language="en"` が設定されている
- **WHEN** LLMプロンプトが生成される
- **THEN** `reading` フィールドの生成指示が含まれる
- **AND** `pronunciations` セクションは含まれない

#### Scenario: Prompt Output Format Example
- **GIVEN** LLMプロンプトが生成される
- **WHEN** 出力形式セクションを確認する
- **THEN** 以下の形式が含まれる：
  ```json
  {
    "title": "動画タイトル",
    "description": "動画の説明",
    "sections": [
      {
        "title": "セクションタイトル",
        "narrations": [
          {
            "text": "明日は晴れです",
            "reading": "アシタワハレデス"
          }
        ],
        "slide_prompt": "..."
      }
    ]
  }
  ```
- **AND** `pronunciations` フィールドは含まれない

**Note**: `pronunciations` の生成指示は削除されました。各ナレーションの `reading` フィールドのみを生成します。

### Requirement: RoleAssignment Data Model

The system SHALL provide a `RoleAssignment` data structure for storing persona role information.

#### Scenario: Create RoleAssignment
- **GIVEN** persona role information:
  - persona_id: "zundamon"
  - role: "解説役"
  - description: "専門知識を持ち、内容を詳しく説明する"
- **WHEN** a `RoleAssignment` is created
- **THEN** all fields are stored correctly
- **AND** the data can be serialized to dict/YAML

#### Scenario: RoleAssignment in VideoScript
- **GIVEN** a `VideoScript` with role assignments:
  ```python
  role_assignments = [
      RoleAssignment(persona_id="zundamon", role="解説役", description="..."),
      RoleAssignment(persona_id="metan", role="質問役", description="..."),
  ]
  ```
- **WHEN** the `VideoScript` is created with these assignments
- **THEN** `script.role_assignments` contains 2 entries
- **AND** each entry has the correct persona_id, role, and description

### Requirement: LLM-Based Image Suitability Assessment

The system SHALL instruct the LLM to evaluate blog images holistically using their metadata (alt, title/caption, aria-describedby), and only set `source_image_url` when the image is deemed suitable for the current section's slide content.

#### Scenario: 画像が現在のセクション内容に適合する場合
- **GIVEN** 元記事に画像リストが提供されている
- **AND** 画像のalt, title, aria-describedbyの情報がある
- **WHEN** LLMがセクションのスライド生成を決定する
- **AND** 画像の説明テキスト（alt, title, aria-describedbyを総合的に判断）が現在のセクションの説明内容と**直接的に関連**している
- **THEN** `source_image_url` に該当画像のURLを設定する
- **AND** `slide_prompt` は省略またはフォールバック用に設定される

#### Scenario: 画像が現在のセクション内容に適合しない場合
- **GIVEN** 元記事に画像リストが提供されている
- **WHEN** LLMがセクションのスライド生成を決定する
- **AND** 画像の説明テキストが現在のセクションの内容と**関連が薄い**または**曖昧**である
- **THEN** `source_image_url` は設定しない
- **AND** `slide_prompt` でAI生成用プロンプトを指定する

#### Scenario: 装飾的・汎用的な画像の除外
- **GIVEN** 画像のaltが「banner」「icon」「logo」などの汎用的なテキストである
- **OR** 画像の説明がセクション内容と無関係である
- **WHEN** LLMが画像採用を判断する
- **THEN** 当該画像は採用せず、AI生成を優先する

#### Scenario: 図解・スクリーンショットの優先採用
- **GIVEN** 画像のaltまたはtitleに「diagram」「architecture」「flow」「screenshot」などの説明的なキーワードが含まれる
- **AND** 画像の説明がセクション内容と明確に関連している
- **WHEN** LLMが画像採用を判断する
- **THEN** 当該画像を優先的に採用する

### Requirement: Image Selection Criteria in LLM Prompt

The LLM prompt SHALL explicitly include image selection criteria that guide the LLM to make appropriate adoption decisions.

#### Scenario: 日本語プロンプトに画像選択基準を含める
- **WHEN** 日本語のスクリプト生成プロンプトが構築される
- **THEN** プロンプトに以下の指示が含まれる：
  - 画像のalt, title/caption, aria-describedbyを総合的に判断する
  - セクションの説明内容に**適切な場合のみ**採用する
  - 曖昧または関連が薄い画像はAI生成を優先する

#### Scenario: 英語プロンプトに画像選択基準を含める
- **WHEN** 英語のスクリプト生成プロンプトが構築される
- **THEN** プロンプトに以下の指示が含まれる：
  - Evaluate alt, title/caption, and aria-describedby holistically
  - Only adopt images when they are **directly relevant** to the section content
  - Prefer AI generation for ambiguous or loosely related images
