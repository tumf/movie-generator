# Audio Furigana - Morpheme Pronunciation Fallback

This delta adds CLI integration for automatic pronunciation fallback using morphological analysis to supplement LLM-generated pronunciations.

## ADDED Requirements

### Requirement: CLI Integration for Morphological Fallback

The CLI SHALL automatically supplement LLM-generated pronunciations with morphological analysis results.

#### Scenario: LLM pronunciation takes precedence
- **Given** a script.yaml with LLM-generated pronunciation for "Turso" -> "ターソ" (priority 10)
- **And** the narration text contains "Turso"
- **When** audio generation is executed
- **Then** the LLM pronunciation "ターソ" is used

#### Scenario: Morphological analysis fills gaps
- **Given** a script.yaml without pronunciation for "BETA"
- **And** the narration contains "今はBETAで"
- **When** audio generation is executed
- **Then** morphological analysis adds "BETA" -> "ベータ" (priority 5) to the dictionary

#### Scenario: Error handling for missing MeCab
- **Given** MeCab/UniDic is not installed or configured
- **When** morphological analysis is attempted
- **Then** a warning is logged and audio generation continues without morphological fallback

### Requirement: Text-based Preparation Method

The VoicevoxSynthesizer SHALL provide a method to prepare pronunciations from raw text strings.

#### Scenario: Prepare from narration texts
- **Given** a list of narration texts from script sections
- **When** prepare_texts() is called
- **Then** all morphological readings are added to the dictionary

## MODIFIED API Reference

### VoicevoxSynthesizer Extension

```python
class VoicevoxSynthesizer:
    def prepare_texts(self, texts: list[str]) -> int:
        """Prepare dictionary entries from texts using morphological analysis.

        Similar to prepare_phrases() but accepts raw text strings.
        Returns the number of dictionary entries added.
        """
```
