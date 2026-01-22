## ADDED Requirements

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
