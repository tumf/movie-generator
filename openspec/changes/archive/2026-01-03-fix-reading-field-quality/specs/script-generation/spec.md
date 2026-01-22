# Script Generation - Reading Field Quality Fix Deltas

## MODIFIED Requirements

### Requirement: Reading Field Quality

The system SHALL generate high-quality katakana readings in the `reading` field for each narration, with correct sokuon (促音), appropriate spacing, and clear emphasis in prompts.

**変更内容**:
1. 促音ルール（「って」→「ッテ」）の強調を強化
2. スペースルールを新規追加
3. プロンプト内でCRITICALマーカーを使用して優先度を明示

既存の要件（アルファベット略語、促音の表記）はそのまま維持し、品質向上のためのプロンプト改善を行う。

#### Scenario: Generate Accurate Sokuon with Emphasis

**GIVEN** プロンプトにCRITICALマーカー付きの促音ルールがある
**AND** narration text contains "Web3って難しい"
**WHEN** LLM generates the reading field
**THEN** reading is "ウェブスリー ッテ ムズカシイ"
**AND NOT** "ウェブスリーツッテムズカシイ" (スペースなし×)
**AND NOT** "ウェブスリー ツッテ ムズカシイ" (促音が「ツッテ」×)

#### Scenario: Sokuon Examples Expanded

**GIVEN** 日本語プロンプト（単話者または対話）が生成される
**WHEN** 促音ルールセクションを確認する
**THEN** 以下の例が含まれる（最低9例）：
  - 「って」→「ッテ」
    - 「聞いたって」→「キイタッテ」
    - 「APIって何？」→「エーピーアイッテナニ？」
    - 「Web3って難しい」→「ウェブスリー ッテ ムズカシイ」
  - 「った」→「ッタ」
    - 「言った」→「イッタ」
    - 「使った」→「ツカッタ」
  - 「っぱ」→「ッパ」
    - 「やっぱり」→「ヤッパリ」
  - 「っと」→「ット」
    - 「ちょっと」→「チョット」
  - 「っか」→「ッカ」
    - 「せっかく」→「セッカク」
  - 「っこ」→「ッコ」
    - 「びっくり」→「ビックリ」

#### Scenario: Incorrect Sokuon Examples

**GIVEN** 日本語プロンプトが生成される
**WHEN** 促音ルールセクションを確認する
**THEN** 誤った例が明示される：
  - ❌ 「って」→「ツッテ」（「ツ」が大きい）
  - ❌ 「って」→「テ」（促音なし）
  - ✅ 「って」→「ッテ」（小さい「ッ」）

## ADDED Requirements

### Requirement: Spacing in Reading Field

The reading field SHALL include appropriate spaces to improve readability.

**新規追加**: カタカナ読み仮名に適切なスペースを入れるルールを追加。従来はスペースなしで長い文字列が生成されていたため、読みにくかった。

#### Scenario: Word Boundary Spacing

**GIVEN** narration text is "Web3って難しいのに操作できるの！？"
**WHEN** LLM generates the reading field
**THEN** reading includes spaces at word boundaries:
  - "ウェブスリー ッテ ムズカシイノニ ソウサデキルノ！？"
**AND NOT** "ウェブスリーッテムズカシイノニソウサデキルノ！？" (スペースなし)

#### Scenario: Particle Spacing

**GIVEN** 助詞（は、が、を、に、で、と）を含むナレーション
**WHEN** LLM generates the reading field
**THEN** 助詞の前にスペースが挿入される：
  - 「これは便利だね」→「コレワ ベンリダネ」
  - 「本を読む」→「ホンオ ヨム」
  - 「東京に行く」→「トウキョウニ イク」

#### Scenario: Spacing Rules in Prompt

**WHEN** 日本語プロンプトが生成される
**THEN** スペースルールセクションが含まれる：
  - 単語の区切りにスペースを入れる
  - 助詞の前にスペースを入れる（ただし短い場合は省略可）
  - 長い文（20文字以上）では必ずスペースを入れる
  - 句読点（。！？）の後はスペース不要

#### Scenario: Good and Bad Spacing Examples

**WHEN** 日本語プロンプトが生成される
**THEN** 良い例・悪い例が含まれる：
  - ✅ 良い例:
    - 「ウェブスリー ッテ ムズカシイノニ」
    - 「コレワ ベンリダネ」
    - 「トウキョウニ イク」
  - ❌ 悪い例:
    - 「ウェブスリーッテムズカシイノニ」（スペースなし）
    - 「コレ ワ ベン リ ダ ネ」（スペース多すぎ）

### Requirement: Critical Requirement Section in Prompts

Prompts SHALL include a CRITICAL REQUIREMENT section at the beginning to emphasize the importance of reading field quality.

**新規追加**: プロンプトの冒頭にCRITICAL REQUIREMENTセクションを追加し、reading品質の重要性を強調。

#### Scenario: Critical Requirement Section Content

**WHEN** 日本語または英語プロンプトが生成される
**THEN** プロンプトの冒頭（出力形式の前）に以下が含まれる：
```
【CRITICAL REQUIREMENT - 最重要】
reading フィールドの品質はシステムの成否を左右します。以下を必ず守ってください：
1. 促音（小さい「ッ」）を正確に使用
2. 適切なスペースを挿入
3. 助詞の発音ルールを適用（は→ワ、へ→エ、を→オ）
4. アルファベット略語の音引きルール適用

これらのルールを破ると、音声合成が失敗します。
```

#### Scenario: Self-Check Item for Reading Quality

**GIVEN** プロンプトに自己評価チェックリストがある
**WHEN** チェックリスト項目を確認する
**THEN** 以下の項目が含まれる：
  - [ ] すべてのreadingフィールドで促音が正しく使われているか？（「ツッテ」×、「ッテ」○）
  - [ ] 長い文にスペースが適切に挿入されているか？
  - [ ] 助詞の発音ルールが適用されているか？
