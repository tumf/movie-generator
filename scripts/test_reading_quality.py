#!/usr/bin/env python3
"""Test script to verify reading field quality from LLM generation.

This script tests the improved prompts for katakana reading generation.
"""

import asyncio
import os
import sys

from movie_generator.script.generator import generate_script


async def test_reading_quality() -> None:
    """Test reading field quality with various edge cases."""
    # Test content with challenging words
    test_content = """
# ESPとは何か

ESPは新しい技術です。APIとの連携も可能です。
これって便利ですよね！CPUの性能も重要です。

## 特徴

- 高速な処理
- USBで接続可能
- RAGとの統合

97%の性能向上を実現しました。
"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        sys.exit(1)

    print("Testing single-speaker mode (JA)...")
    script = await generate_script(
        content=test_content,
        title="ESP技術解説",
        description="ESPの基本的な説明",
        character="ずんだもん",
        style="casual",
        language="ja",
        api_key=api_key,
        model="openai/gpt-4o-mini",  # Use cheaper model for testing
    )

    print("\n=== Generated Script (Single-Speaker) ===")
    print(f"Title: {script.title}")
    print(f"Sections: {len(script.sections)}\n")

    # Check reading field quality
    issues = []
    for i, section in enumerate(script.sections):
        print(f"\n--- Section {i + 1}: {section.title} ---")
        for j, narration in enumerate(section.narrations):
            print(f"  [{j + 1}] text: {narration.text}")
            print(f"      reading: {narration.reading}")

            # Check for common mistakes
            if not narration.reading:
                issues.append(f"Section {i + 1}, Narration {j + 1}: Missing reading field")
            elif "ESP" in narration.text and "イーエスピージ" in narration.reading:
                issues.append(
                    f"Section {i + 1}, Narration {j + 1}: "
                    f"ESP read as イーエスピージ (should be イーエスピー)"
                )
            elif "API" in narration.text and "エーピーアイジ" in narration.reading:
                issues.append(
                    f"Section {i + 1}, Narration {j + 1}: "
                    f"API read as エーピーアイジ (should be エーピーアイ)"
                )
            elif "CPU" in narration.text and "シーピーユージ" in narration.reading:
                issues.append(
                    f"Section {i + 1}, Narration {j + 1}: "
                    f"CPU read as シーピーユージ (should be シーピーユー)"
                )

    # Test multi-speaker mode
    print("\n\n=== Testing Multi-Speaker Mode (JA) ===")
    personas = [
        {"id": "zundamon", "name": "ずんだもん", "character": "元気で明るい"},
        {"id": "metan", "name": "四国めたん", "character": "落ち着いていて丁寧"},
    ]

    script_dialogue = await generate_script(
        content=test_content,
        title="ESP技術解説（対話版）",
        description="ESPの基本的な説明を対話形式で",
        style="casual",
        language="ja",
        api_key=api_key,
        model="openai/gpt-4o-mini",
        personas=personas,
    )

    print(f"Title: {script_dialogue.title}")
    print(f"Sections: {len(script_dialogue.sections)}\n")

    for i, section in enumerate(script_dialogue.sections):
        print(f"\n--- Section {i + 1}: {section.title} ---")
        for j, narration in enumerate(section.narrations):
            speaker = narration.persona_id or "unknown"
            print(f"  [{speaker}] text: {narration.text}")
            print(f"           reading: {narration.reading}")

            # Check for common mistakes
            if not narration.reading:
                issues.append(f"Dialogue Section {i + 1}, Narration {j + 1}: Missing reading field")

    # Report issues
    print("\n\n=== Quality Check Results ===")
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
        sys.exit(1)
    else:
        print("✅ All reading fields generated correctly!")


if __name__ == "__main__":
    asyncio.run(test_reading_quality())
