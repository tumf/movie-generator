#!/usr/bin/env python3
"""Test video rendering with existing audio files."""
from pathlib import Path

from movie_generator.script.phrases import Phrase
from movie_generator.video.renderer import create_composition, render_video, save_composition

# Use existing audio files
audio_dir = Path("output/audio")
audio_files = sorted(audio_dir.glob("phrase_*.wav"))[:10]  # Use first 10 for quick test

if not audio_files:
    print("Error: No audio files found in output/audio/")
    exit(1)

# Create simple phrases
phrases = []
current_time = 0.0
for i, audio_file in enumerate(audio_files):
    # Estimate duration from file size (rough estimate)
    duration = 2.0  # 2 seconds per phrase as estimate
    phrase = Phrase(
        text=f"Test phrase {i}",
        duration=duration,
        start_time=current_time,
    )
    phrases.append(phrase)
    current_time += duration

# Create dummy slides (black images or use test slide)
slides_dir = Path("output/slides_test")
slides_dir.mkdir(parents=True, exist_ok=True)
slides = [slides_dir / f"slide_{i:04d}.png" for i in range(3)]

# Use test slide or create black images
test_slide = Path("output/test_slide.png")
for slide_path in slides:
    if test_slide.exists():
        import shutil

        shutil.copy(test_slide, slide_path)
    else:
        slide_path.write_bytes(b"")  # Empty for now

print(f"Creating composition with {len(phrases)} phrases and {len(audio_files)} audio files...")

# Create composition
composition = create_composition(
    title="Test Video",
    phrases=phrases,
    slide_paths=slides,
    audio_paths=audio_files,
)

# Save composition
comp_path = Path("output/test_composition.json")
save_composition(composition, comp_path)
print(f"✓ Composition saved: {comp_path}")

# Render video
output_video = Path("output/test_output.mp4")
print(f"Rendering video to {output_video}...")
render_video(comp_path, output_video)

if output_video.exists() and output_video.stat().st_size > 0:
    print(
        f"✓ Success! Video generated: {output_video} ({output_video.stat().st_size / 1024 / 1024:.2f} MB)"
    )
else:
    print("✗ Failed: Empty or missing video file")
