# Slide Prompt Examples for Multi-Language Support

## Overview

When generating slides for multiple languages, the slide prompts are written in English (for better compatibility with image generation APIs), but the **text to be displayed on slides** is specified in the target language.

## Script Quality Improvements

**Note**: As of January 2025, the script generation prompts have been significantly enhanced to improve storytelling quality, multi-speaker dialogue naturalness, and content depth. The improvements include:

- **Storytelling Structure**: Scripts now follow a structured narrative arc (Hook → Context → Core Content → Conclusion) to better engage viewers
- **Multi-Speaker Dynamics**: Dialogue mode now includes detailed role patterns, conversation rhythm guidance, and personality development instructions
- **Content Deepening**: Emphasis on anticipating viewer questions, providing concrete examples, and progressive explanation (overview → details → application)
- **Self-Evaluation**: LLM prompts include built-in quality checklists to ensure engaging introductions, logical flow, and satisfying conclusions

These enhancements ensure that generated scripts are more engaging, easier to understand, and maintain viewer attention throughout the video.

## Format

```
"A slide with text '<TARGET_LANGUAGE_TEXT>' <ENGLISH_DESCRIPTION>"
```

## Japanese Examples

### Example 1: Introduction Slide
```
"A slide with text 'はじめに' in the center, clean modern design, blue gradient background"
```

### Example 2: Concept Explanation
```
"A slide with text 'データベース設計の基本' at the top, with simple icons below representing tables and relationships, professional style"
```

### Example 3: Key Points
```
"A slide with text '重要なポイント' as title and bullet points '・パフォーマンス ・セキュリティ ・スケーラビリティ' in Japanese, minimalist design"
```

### Example 4: Technical Term
```
"A slide with text 'API統合' in bold at center, surrounded by connection lines and server icons, tech-focused aesthetic"
```

## English Examples

### Example 1: Introduction Slide
```
"A slide with text 'Introduction' in the center, clean modern design, blue gradient background"
```

### Example 2: Concept Explanation
```
"A slide with text 'Database Design Fundamentals' at the top, with simple icons below representing tables and relationships, professional style"
```

### Example 3: Key Points
```
"A slide with text 'Key Points' as title and bullet points '• Performance • Security • Scalability' in English, minimalist design"
```

### Example 4: Technical Term
```
"A slide with text 'API Integration' in bold at center, surrounded by connection lines and server icons, tech-focused aesthetic"
```

## Best Practices

1. **Keep text short**: Limit slide text to 3-5 words for better readability
2. **Use native script**:
   - Japanese: Use hiragana/katakana/kanji as appropriate
   - English: Use proper capitalization
3. **Consistent style**: Maintain visual consistency across all language versions
4. **Clear instructions**: Specify text position (center, top, bottom) and style (bold, large, etc.)

## Common Patterns

### Title Slides
- Japanese: `"A slide with text '<タイトル>' in large font at center, professional background"`
- English: `"A slide with text '<Title>' in large font at center, professional background"`

### Section Headers
- Japanese: `"A slide with text '<セクション名>' at the top, modern layout"`
- English: `"A slide with text '<Section Name>' at the top, modern layout"`

### Summary Slides
- Japanese: `"A slide with text 'まとめ' and key points in Japanese below, clean design"`
- English: `"A slide with text 'Summary' and key points in English below, clean design"`

## Implementation Note

The LLM (script generator) automatically generates appropriate slide prompts based on the configured language:
- For `language: "ja"` → Generates prompts with Japanese text
- For `language: "en"` → Generates prompts with English text
- For `languages: ["ja", "en"]` → Generates both versions with appropriate text in each language
