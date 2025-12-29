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
    """Generate slides from script.yaml."""
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not set")
        print("   Set it with: export OPENROUTER_API_KEY='your-key'")
        return 1

    # Load script
    script_path = Path("output/script.yaml")
    if not script_path.exists():
        print(f"❌ Error: {script_path} not found")
        print("   Run: movie-generator generate <url> first")
        return 1

    with open(script_path, "r", encoding="utf-8") as f:
        script = yaml.safe_load(f)

    # Extract sections
    sections = []
    for section in script.get("sections", []):
        title = section.get("title", "")
        slide_prompt = section.get("slide_prompt", "")
        if slide_prompt:
            sections.append((title, slide_prompt))

    if not sections:
        print("❌ Error: No sections with slide_prompt found in script.yaml")
        return 1

    print(f"📊 Found {len(sections)} sections to generate slides for")
    print(f"   Model: google/gemini-2.5-flash-image-preview")
    print(f"   Output: output/slides/")
    print()

    # Generate slides
    slides_dir = Path("output/slides")
    slides_dir.mkdir(parents=True, exist_ok=True)

    slide_paths = await generate_slides_for_sections(
        sections=sections,
        output_dir=slides_dir,
        api_key=api_key,
        model="google/gemini-2.5-flash-image-preview",
        max_concurrent=2,  # Conservative to avoid rate limits
    )

    # Report results
    successful = sum(1 for p in slide_paths if p.exists() and p.stat().st_size > 0)
    failed = len(slide_paths) - successful

    print()
    print("=" * 60)
    if failed == 0:
        print(f"✅ Success! Generated all {successful} slides")
    else:
        print(f"⚠️  Generated {successful}/{len(slide_paths)} slides")
        print(f"   Failed: {failed}")
        print()
        print("   To retry failed slides:")
        print("   1. Delete 0-byte files: find output/slides -size 0 -delete")
        print("   2. Run this script again")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
