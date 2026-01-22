# Script Generation Specification - Delta

## ADDED Requirements

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
