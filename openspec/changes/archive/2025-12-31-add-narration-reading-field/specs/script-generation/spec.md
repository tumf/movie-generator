# script-generation Spec Delta

## ADDED Requirements

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
