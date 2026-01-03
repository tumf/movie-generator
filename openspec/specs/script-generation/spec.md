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

### Requirement: Storytelling Structure in Prompts

The LLM prompts SHALL guide the LLM to generate scripts with a clear storytelling structure that engages viewers and maintains logical flow.

**変更内容**: プロンプトにストーリーテリングの構造化指示を追加。従来は「最低6セクション」「最後にまとめ」程度の指示だったが、Hook・起承転結・セクション間接続を明示的に指示する。

#### Scenario: Hook Section in Opening
- **GIVEN** 日本語または英語の台本生成プロンプトが構築される
- **WHEN** プロンプトが生成される
- **THEN** 冒頭セクション（Hook）で以下を含むよう指示される：
  - 視聴者の興味を引く問題提起・驚きの事実
  - 「なぜこのトピックが重要か」の動機付け
  - 15-30秒以内での簡潔な提示
- **AND** 具体的なHook例がプロンプトに含まれる

#### Scenario: 起承転結の明示的指示
- **WHEN** 台本生成プロンプトが構築される
- **THEN** 以下の構造を生成するよう指示される：
  - **起（導入）**: 背景・問題提起・視聴者の関心を引く
  - **承（展開）**: 核心内容の説明・詳細な情報提供
  - **転（転換）**: 応用例・別視点・驚きの発見
  - **結（結論）**: 要点の再確認・視聴者への行動喚起
- **AND** 各段階のセクション数の目安が示される

#### Scenario: セクション間の論理的接続
- **WHEN** 台本生成プロンプトが構築される
- **THEN** セクション間の接続を明示するよう指示される：
  - 前セクションの内容を受けた導入
  - 次セクションへの自然な橋渡し
  - 「なぜこの順序か」の論理的根拠
- **AND** 接続詞の使用例が提示される（「それでは次に」「この背景として」「具体的には」）

### Requirement: Enhanced Multi-Speaker Role Design

The dialogue prompts SHALL provide detailed role patterns and conversation dynamics to generate natural, engaging multi-speaker interactions.

**変更内容**: 従来の「解説役・質問役」程度の抽象的指示から、具体的な会話パターン・リズム・個性引き出しの詳細指示に拡張。

#### Scenario: 具体的な役割パターンの提供
- **GIVEN** 複数話者モードのプロンプトが生成される
- **WHEN** プロンプト内の役割指示セクションを確認する
- **THEN** 以下の具体的なパターンが含まれる：
  - **理解確認パターン**: 「つまり〜ということ?」「〜という理解で合ってる?」
  - **疑問提起パターン**: 「でも〜はどうなるの?」「初心者が疑問に思うのは〜」
  - **具体例要求パターン**: 「具体的には?」「実際の例を教えて」
  - **リアクションパターン**: 「すごい!」「なるほど!」「それは知らなかった!」
- **AND** 各パターンの使用タイミングが説明される

#### Scenario: 話者交代のリズム指示
- **WHEN** 対話プロンプトが生成される
- **THEN** 以下の話者交代リズムが指示される：
  - 一方的な長い説明を避ける（1ターン最大3文まで）
  - 理解度確認を適宜挟む
  - 重要ポイントの前後で反応を入れる
  - 単純な交互発言パターンを避け、自然な会話流れにする
- **AND** 良い例・悪い例が提示される

#### Scenario: キャラクター個性の活用
- **GIVEN** 各ペルソナの `character` 設定がある
- **WHEN** 対話プロンプトが生成される
- **THEN** キャラクター設定を活かすよう指示される：
  - 「元気で明るい」→リアクションを大きく、テンポよく
  - 「優しくて落ち着いた」→丁寧な確認、わかりやすい言い換え
  - 「専門家気質」→正確な用語、詳しい説明
- **AND** キャラクター設定ごとの発言例が含まれる

### Requirement: Deep Content Understanding Instructions

The prompts SHALL instruct the LLM to deeply understand content and present it from the viewer's perspective with concrete examples and analogies.

**変更内容**: 表面的な要約を避け、視聴者視点の疑問予測・具体例・段階的説明を生成するよう指示を追加。

#### Scenario: 視聴者疑問の予測と対応
- **WHEN** 台本生成プロンプトが構築される
- **THEN** 以下の指示が含まれる：
  - 「初めてこのトピックを聞く視聴者が疑問に思うこと」を予測する
  - 専門用語を使う場合は必ず「〜とは」で定義する
  - 抽象的な概念には必ず具体例を添える
  - 「なぜ重要か」「どう使うのか」を説明する
- **AND** 疑問予測の例が提示される（「なぜ今必要?」「従来との違いは?」「実際に使える?」）

#### Scenario: 具体例・比喩の必須化
- **WHEN** LLMに台本生成を依頼する
- **THEN** 各メインポイントに対して以下が指示される：
  - 最低1つの具体例を含める
  - 可能な限り日常的な比喩を使う
  - 「例えば〜」「〜のようなもの」などの導入フレーズを使う
- **AND** 良い具体例の特徴が説明される（身近・イメージしやすい・関連性が明確）

#### Scenario: 段階的説明の構造化
- **WHEN** 台本生成プロンプトが構築される
- **THEN** 複雑なトピックは以下の3段階で説明するよう指示される：
  1. **概要（What）**: 一言で何か、全体像
  2. **詳細（How）**: 仕組み、使い方、特徴
  3. **応用（Why/When）**: なぜ使うのか、いつ使うのか、メリット
- **AND** 各段階の説明時間の目安が示される

### Requirement: Self-Evaluation Checklist in Prompts

The prompts SHALL include a self-evaluation checklist that guides the LLM to assess the quality of the generated script before finalizing it.

**変更内容**: 新規追加。LLMに台本生成後の自己評価を促し、品質向上を図る。

#### Scenario: 自己評価チェックリストの提示
- **WHEN** 台本生成プロンプトが構築される
- **THEN** プロンプトの最後に以下のチェックリストが含まれる：
  - [ ] 冒頭15秒で視聴者の興味を引けるか?
  - [ ] 各セクションの目的が明確か?
  - [ ] セクション間のつながりが論理的か?
  - [ ] 専門用語はすべて説明されているか?
  - [ ] 具体例が各メインポイントに含まれているか?
  - [ ] 視聴者の疑問に先回りして答えているか?
  - [ ] （対話モード）会話が自然で単調でないか?
  - [ ] （対話モード）役割分担が明確か?
  - [ ] 最終セクションで要点がまとめられているか?
  - [ ] 視聴者に次のアクションが提示されているか?

#### Scenario: チェックリスト適用の指示
- **WHEN** 台本生成プロンプトが構築される
- **THEN** チェックリスト後に以下の指示が含まれる：
  - 「上記チェックリストを確認し、改善できる点があれば台本を調整してください」
  - 「すべての項目が満たされていることを確認してから出力してください」

### Requirement: Prompt Examples for Quality Patterns

The prompts SHALL include concrete examples of high-quality script patterns to guide the LLM.

#### Scenario: 良いフックの例示
- **WHEN** 台本生成プロンプトが構築される
- **THEN** 以下のような良いフックの例が含まれる：
  - 問題提起型: 「あなたは〜で困っていませんか?」
  - 驚きの事実型: 「実は、〜の97%が〜だったのです」
  - 変化の提示型: 「2023年、〜の世界が大きく変わりました」
  - 対比型: 「従来は〜でしたが、今は〜が可能になりました」

#### Scenario: 悪いパターンの警告
- **WHEN** 台本生成プロンプトが構築される
- **THEN** 避けるべきパターンの例が含まれる：
  - ❌ 唐突な本題開始: 「〜について説明します」
  - ❌ 抽象的な列挙: 「ポイントは3つあります」（理由・背景なし）
  - ❌ 単調な交互発言: A→B→A→B...（対話モード）
  - ❌ 専門用語の説明なし使用
  - ❌ 具体例のない抽象的説明

### Requirement: Language-Specific Quality Instructions

Quality instructions SHALL be appropriately adapted for Japanese and English prompts.

#### Scenario: 日本語プロンプトの品質指示
- **WHEN** 日本語プロンプト（`_JA`）が生成される
- **THEN** 日本語特有の表現が指示される：
  - 「〜のだ」「〜なのだ」などキャラクター口調の適切な使用
  - 「つまり」「要するに」「例えば」などの接続表現
  - 視聴者への問いかけ（「〜ですよね?」「〜したことありますか?」）

#### Scenario: 英語プロンプトの品質指示
- **WHEN** 英語プロンプト（`_EN`）が生成される
- **THEN** 英語特有の表現が指示される：
  - Conversational tone with contractions (e.g., "let's", "it's")
  - Transition phrases ("Now", "So", "For example")
  - Viewer engagement ("Have you ever...?", "You might be wondering...")

---

**Note**: This specification was enhanced by archiving the change `improve-script-quality`.
Original Japanese version archived in `openspec/changes/archive/2025-01-03-improve-script-quality/`.

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

### Requirement: Reading Field Quality

The system SHALL generate high-quality katakana readings in the `reading` field for each narration.

**変更内容**: LLMプロンプトに以下のルールを追加して品質を向上：
- アルファベット略語の音引きルール（ESP→イーエスピー）
- 促音の表記ルール（って→ッテ）

#### Scenario: Generate Accurate Acronym Readings

**GIVEN** narration text contains "ESPが次の章"
**WHEN** LLM generates the reading field
**THEN** reading is "イーエスピーガツギノショウ"
**AND NOT** "イーエスピージガツギノショウ" (incorrect)

#### Scenario: Generate Accurate Sokuon Readings

**GIVEN** narration text contains "聞いたって"
**WHEN** LLM generates the reading field
**THEN** reading is "キイタッテ" (with small ッ)
**AND NOT** "キイタテ" (without ッ)
