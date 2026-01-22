# Script Generation - Quality Improvement Deltas

## MODIFIED Requirements

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

## ADDED Requirements

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
