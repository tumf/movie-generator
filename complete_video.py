#!/usr/bin/env python3
"""Complete video generation using existing audio files."""
import asyncio
import json
import os
from pathlib import Path
from movie_generator.slides.generator import generate_slides_for_sections
from movie_generator.video.renderer import create_composition, save_composition, render_video
from movie_generator.script.phrases import Phrase

async def main():
    # Load audio files
    audio_dir = Path("output/audio")
    audio_files = sorted(audio_dir.glob("phrase_*.wav"))
    
    if not audio_files:
        print("Error: No audio files found. Run generate command first.")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    # Create phrases with timing
    phrases = []
    current_time = 0.0
    
    # Load audio durations (estimate from file size)
    import wave
    for i, audio_file in enumerate(audio_files):
        try:
            with wave.open(str(audio_file), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / rate
        except:
            duration = 1.0  # Fallback
        
        phrase = Phrase(
            text=f"Phrase {i}",
            duration=duration,
            start_time=current_time,
        )
        phrases.append(phrase)
        current_time += duration
    
    print(f"Total audio duration: {current_time:.2f}s")
    
    # Generate slides
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: OPENROUTER_API_KEY not set, creating placeholder slides")
        slides_dir = Path("output/slides")
        slides_dir.mkdir(parents=True, exist_ok=True)
        slide_paths = []
        for i in range(12):
            slide_path = slides_dir / f"slide_{i:04d}.png"
            # Copy test slide or create placeholder
            test_slide = Path("output/test_slide.png")
            if test_slide.exists():
                import shutil
                shutil.copy(test_slide, slide_path)
            else:
                slide_path.write_bytes(b"")
            slide_paths.append(slide_path)
    else:
        # Generate real slides
        sections = [
            ("Introduction", "Kaiju Engine: A game engine written in Go"),
            ("Performance", "Unity比3倍高速: Go and Vulkan performance"),
            ("Architecture", "Engine architecture and design"),
            ("Graphics", "Vulkan graphics pipeline"),
            ("Memory", "Memory management in Go"),
            ("ECS", "Entity Component System"),
            ("Rendering", "3D rendering techniques"),
            ("Physics", "Physics simulation"),
            ("Audio", "Audio system"),
            ("Tools", "Development tools"),
            ("Future", "Future roadmap"),
            ("Conclusion", "Summary and conclusion"),
        ]
        
        slides_dir = Path("output/slides")
        print(f"Generating {len(sections)} slides...")
        slide_paths = await generate_slides_for_sections(
            sections,
            slides_dir,
            api_key,
            model="google/gemini-3-pro-image-preview"
        )
        print(f"✓ Generated {len(slide_paths)} slides")
    
    # Create composition
    print("Creating composition...")
    composition = create_composition(
        title="Kaiju Engine解説",
        phrases=phrases,
        slide_paths=slide_paths,
        audio_paths=audio_files,
    )
    
    comp_path = Path("output/composition.json")
    save_composition(composition, comp_path)
    print(f"✓ Composition saved: {comp_path}")
    
    # Render video
    output_video = Path("output/output.mp4")
    print("Rendering video...")
    render_video(comp_path, output_video)
    
    if output_video.exists() and output_video.stat().st_size > 0:
        size_mb = output_video.stat().st_size / 1024 / 1024
        print(f"\n✅ Success! Video generated: {output_video} ({size_mb:.2f} MB)")
        print(f"   Duration: {current_time:.2f}s")
        print(f"\nPlay with: open {output_video}")
    else:
        print("\n✗ Failed: Empty or missing video file")

if __name__ == "__main__":
    asyncio.run(main())
