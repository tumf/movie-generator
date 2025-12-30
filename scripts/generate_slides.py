#!/usr/bin/env python3
"""Generate slides from script.yaml sections."""

import asyncio
import os
import sys
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movie_generator.slides.generator import generate_slides_for_sections


async def main():
    """Generate slides from script.yaml or language-specific script files."""
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not set")
        print("   Set it with: export OPENROUTER_API_KEY='your-key'")
        return 1

    # Detect script files (legacy script.yaml or language-specific)
    output_dir = Path("output")
    script_files = []

    # Check for language-specific scripts first
    for lang_script in output_dir.glob("script_*.yaml"):
        lang_code = lang_script.stem.replace("script_", "")
        script_files.append((lang_code, lang_script))

    # Fallback to legacy script.yaml (treat as Japanese)
    if not script_files:
        legacy_script = output_dir / "script.yaml"
        if legacy_script.exists():
            script_files.append(("ja", legacy_script))

    if not script_files:
        print("❌ Error: No script files found")
        print("   Run: movie-generator generate <url> first")
        return 1

    print(f"📊 Found {len(script_files)} language(s) to generate slides for")
    print(f"   Model: google/gemini-3-pro-image-preview")
    print()

    total_successful = 0
    total_failed = 0

    # Generate slides for each language
    for lang_code, script_path in script_files:
        print(f"\n{'=' * 60}")
        print(f"Processing language: {lang_code.upper()}")
        print(f"Script file: {script_path}")
        print(f"{'=' * 60}\n")

        with open(script_path, "r", encoding="utf-8") as f:
            script = yaml.safe_load(f)

        # Extract sections
        sections = []
        for section in script.get("sections", []):
            title = section.get("title", "")
            slide_prompt = section.get("slide_prompt", "")
            source_image_url = section.get("source_image_url")

            # Include section if it has either a prompt or source image
            if slide_prompt or source_image_url:
                sections.append((title, slide_prompt, source_image_url))

        if not sections:
            print(
                f"⚠️  Warning: No sections with slide_prompt or source_image_url found in {script_path}"
            )
            continue

        print(f"📊 Found {len(sections)} sections to generate slides for")
        print(f"   Output: output/slides/{lang_code}/")
        print()

        # Generate slides
        slides_dir = Path("output/slides")
        slides_dir.mkdir(parents=True, exist_ok=True)

        slide_paths = await generate_slides_for_sections(
            sections=sections,
            output_dir=slides_dir,
            api_key=api_key,
            language=lang_code,
            model="google/gemini-3-pro-image-preview",
            max_concurrent=2,  # Conservative to avoid rate limits
        )

        # Report results for this language
        successful = sum(1 for p in slide_paths if p.exists() and p.stat().st_size > 0)
        failed = len(slide_paths) - successful
        total_successful += successful
        total_failed += failed

        print()
        print(f"Results for {lang_code.upper()}:")
        if failed == 0:
            print(f"  ✅ Generated all {successful} slides")
        else:
            print(f"  ⚠️  Generated {successful}/{len(slide_paths)} slides")
            print(f"     Failed: {failed}")

    # Final summary
    print()
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    if total_failed == 0:
        print(f"✅ Success! Generated all {total_successful} slides across all languages")
    else:
        print(f"⚠️  Generated {total_successful}/{total_successful + total_failed} slides")
        print(f"   Failed: {total_failed}")
        print()
        print("   To retry failed slides:")
        print("   1. Delete 0-byte files: find output/slides -size 0 -delete")
        print("   2. Run this script again")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
