#!/usr/bin/env python3
"""Test skip functionality."""
import wave
from pathlib import Path

# Check existing audio files
audio_dir = Path("output/audio")
audio_files = list(audio_dir.glob("phrase_*.wav"))

print(f"Found {len(audio_files)} existing audio files")
print(f"First 5: {[f.name for f in sorted(audio_files)[:5]]}")

# Check file sizes
valid_files = [f for f in audio_files if f.stat().st_size > 0]
empty_files = [f for f in audio_files if f.stat().st_size == 0]

print(f"  Valid: {len(valid_files)} files")
print(f"  Empty: {len(empty_files)} files")

# Check total duration
total_duration = 0.0
for audio_file in valid_files[:10]:
    try:
        with wave.open(str(audio_file), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / rate
            total_duration += duration
    except:
        pass

print(f"  Sample duration (first 10): {total_duration:.2f}s")
