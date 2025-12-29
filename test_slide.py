#!/usr/bin/env python3
import asyncio
import os
from pathlib import Path
from movie_generator.slides.generator import generate_slide

async def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        return
    
    output_path = Path("output/test_slide.png")
    prompt = "Kaiju Engine: A game engine written in Go with Vulkan graphics"
    
    print(f"Generating slide...")
    result = await generate_slide(
        prompt=prompt,
        output_path=output_path,
        api_key=api_key,
    )
    
    if result.exists() and result.stat().st_size > 0:
        print(f"✓ Success! Slide generated: {result} ({result.stat().st_size} bytes)")
    else:
        print(f"✗ Failed: Empty or missing file")

if __name__ == "__main__":
    asyncio.run(main())
