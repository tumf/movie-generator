## MODIFIED Requirements

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
