# Audio Furigana Generation Specification

## Overview

This specification defines the automatic furigana (reading) generation capability for Japanese text using morphological analysis to improve VOICEVOX text-to-speech pronunciation accuracy.

## ADDED Requirements

### Requirement: Morphological Analysis Integration

The system SHALL use morphological analysis to generate accurate readings for Japanese text.

#### Scenario: Basic text analysis
- **Given** a Japanese text "表計算"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns morphemes with readings "ヒョウ" for "表" and "ケイサン" for "計算"

#### Scenario: Person-month reading
- **Given** a Japanese text containing "人月"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns the reading "ニンゲツ" (not "ジンゲツ")

#### Scenario: English word in dictionary
- **Given** a text containing "Excel"
- **When** the FuriganaGenerator analyzes the text
- **Then** it returns the reading "エクセル"

### Requirement: Automatic Dictionary Registration

The system SHALL automatically register morphological analysis results to the pronunciation dictionary.

#### Scenario: Auto-register readings
- **Given** a FuriganaGenerator and PronunciationDictionary
- **When** prepare_phrases() is called with phrases containing kanji
- **Then** readings are automatically added to the dictionary with priority 5

#### Scenario: Manual entries take precedence
- **Given** a manual dictionary entry for "東京" with reading "トーキョー" (priority 10)
- **And** morphological analysis result "トウキョウ" (priority 5)
- **When** both are registered to the dictionary
- **Then** the manual entry "トーキョー" is used

### Requirement: Configuration Option

The system SHALL provide a configuration option to enable/disable furigana generation.

#### Scenario: Enable furigana via config
- **Given** a configuration with `audio.enable_furigana: true`
- **When** VoicevoxSynthesizer is created from config
- **Then** automatic furigana generation is enabled

#### Scenario: Disable furigana via config
- **Given** a configuration with `audio.enable_furigana: false`
- **When** VoicevoxSynthesizer is created from config
- **Then** automatic furigana generation is disabled

### Requirement: Batch Processing

The system SHALL support batch processing of multiple phrases for efficiency.

#### Scenario: Analyze multiple texts
- **Given** a list of phrases ["表計算", "人月", "ボタン"]
- **When** analyze_texts() is called
- **Then** a combined dictionary of all readings is returned

#### Scenario: Process before initialization
- **Given** a VoicevoxSynthesizer with furigana enabled
- **When** prepare_phrases() is called before initialize()
- **Then** all readings are registered to the dictionary for use in initialization

## Dependencies

- `fugashi>=1.3.0`: MeCab wrapper for Python
- `unidic>=1.1.0`: UniDic dictionary (full version)

## API Reference

### FuriganaGenerator

```python
class FuriganaGenerator:
    def analyze(self, text: str) -> list[MorphemeReading]:
        """Analyze text and return morphemes with readings."""

    def get_readings_dict(self, text: str) -> dict[str, str]:
        """Get dictionary mapping surface forms to readings."""

    def analyze_texts(self, texts: list[str]) -> dict[str, str]:
        """Analyze multiple texts and return combined readings."""
```

### PronunciationDictionary Extension

```python
class PronunciationDictionary:
    def add_from_morphemes(
        self,
        readings: dict[str, str],
        priority: int = 5,
        word_type: str = "COMMON_NOUN",
    ) -> int:
        """Add entries from morphological analysis results."""
```

### VoicevoxSynthesizer Extension

```python
class VoicevoxSynthesizer:
    def __init__(
        self,
        ...,
        enable_furigana: bool = True,
    ):
        """Initialize with optional furigana generation."""

    def prepare_phrases(self, phrases: list[Phrase]) -> int:
        """Prepare dictionary entries for all phrases."""
```

## Configuration Schema

```yaml
audio:
  enable_furigana: true  # Enable automatic furigana generation (default: true)
```
