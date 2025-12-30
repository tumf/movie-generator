"""Multi-language content generation utilities.

Handles script and slide generation for multiple languages.
"""

import asyncio
import os
from pathlib import Path

import yaml

from .config import Config
from .script.generator import generate_script, VideoScript
from .slides.generator import generate_slides_for_sections


async def generate_multilang_content(
    content: str,
    title: str | None,
    description: str | None,
    config: Config,
    output_dir: Path,
    api_key: str,
    images: list[dict[str, str]] | None = None,
) -> dict[str, VideoScript]:
    """Generate scripts and slides for multiple languages.

    Args:
        content: Source content (markdown or text).
        title: Content title.
        description: Content description.
        config: Project configuration.
        output_dir: Output directory for scripts and slides.
        api_key: OpenRouter API key.
        images: List of image metadata dicts with 'src', 'alt', 'title' keys.

    Returns:
        Dictionary mapping language codes to VideoScript objects.
    """
    languages = config.content.languages
    results = {}

    print(f"\n🌐 Generating content for {len(languages)} language(s): {', '.join(languages)}")

    for lang_code in languages:
        print(f"\n{'=' * 60}")
        print(f"Processing language: {lang_code.upper()}")
        print(f"{'=' * 60}\n")

        # Generate script for this language
        print(f"📝 Generating {lang_code.upper()} script...")
        script = await generate_script(
            content=content,
            title=title,
            description=description,
            character=config.narration.character,
            style=config.narration.style,
            language=lang_code,
            api_key=api_key,
            model=config.content.llm.model,
            images=images,
        )

        # Save script to language-specific file
        script_path = output_dir / f"script_{lang_code}.yaml"
        script_data = {
            "title": script.title,
            "description": script.description,
            "sections": [
                {
                    "title": section.title,
                    "narration": section.narration,
                    "slide_prompt": section.slide_prompt,
                    "source_image_url": section.source_image_url,
                }
                for section in script.sections
            ],
        }
        if script.pronunciations:
            script_data["pronunciations"] = [
                {
                    "word": p.word,
                    "reading": p.reading,
                    "word_type": p.word_type,
                    "accent": p.accent,
                }
                for p in script.pronunciations
            ]

        with script_path.open("w", encoding="utf-8") as f:
            yaml.dump(script_data, f, allow_unicode=True, sort_keys=False)
        print(f"✓ Saved script to: {script_path}")

        # Generate slides for this language
        sections_for_slides: list[tuple[str, str, str | None]] = []
        for section in script.sections:
            if section.slide_prompt or section.source_image_url:
                # Ensure slide_prompt is not None (use empty string as fallback)
                prompt = section.slide_prompt or ""
                sections_for_slides.append((section.title, prompt, section.source_image_url))

        if sections_for_slides:
            print(f"\n📊 Generating {len(sections_for_slides)} slides for {lang_code.upper()}...")
            slides_dir = output_dir / "slides"
            slides_dir.mkdir(parents=True, exist_ok=True)

            await generate_slides_for_sections(
                sections=sections_for_slides,
                output_dir=slides_dir,
                api_key=api_key,
                language=lang_code,
                model=config.slides.llm.model,
                max_concurrent=3,
            )
        else:
            print(f"⚠️  No slide prompts or source images found in {lang_code.upper()} script")

        results[lang_code] = script

    print(f"\n{'=' * 60}")
    print(f"✅ Completed content generation for all languages")
    print(f"{'=' * 60}\n")

    return results
