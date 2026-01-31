#!/usr/bin/env python3
"""Demo script to visualize worker progress improvements.

This script simulates the progress flow without actually running video generation.
"""

import asyncio


async def simulate_progress():
    """Simulate progress updates like the worker would generate."""
    progress_log = []

    async def log_progress(pct: int, msg: str, step: str):
        """Mock progress callback."""
        progress_log.append({"pct": pct, "msg": msg, "step": step})
        # Color-code by step
        colors = {
            "script": "\033[94m",  # Blue
            "audio": "\033[92m",  # Green
            "slides": "\033[93m",  # Yellow
            "video": "\033[95m",  # Magenta
        }
        reset = "\033[0m"
        color = colors.get(step, "")
        print(f"{color}[{pct:3d}%]{reset} {msg}")
        await asyncio.sleep(0.3)  # Simulate time

    # Script generation
    await log_progress(5, "スクリプトを生成中...", "script")
    await asyncio.sleep(1)
    await log_progress(20, "スクリプト生成完了", "script")

    # Simulate: 20 phrases, 8 slides
    phrase_count = 20
    slide_count = 8

    # Audio generation (20-55%)
    print(f"\n📊 音声生成: {phrase_count}個のフレーズ")
    await log_progress(22, f"音声生成中 (0/{phrase_count})", "audio")

    for i in range(1, phrase_count + 1):
        # Calculate progress percentage (linear interpolation 22-55%)
        pct = 22 + int((i / phrase_count) * (55 - 22))
        if i == phrase_count:
            await log_progress(55, f"音声生成完了 ({i}/{phrase_count})", "audio")
        else:
            # Show progress every 3 files
            if i % 3 == 0:
                await log_progress(pct, f"音声生成中 ({i}/{phrase_count})", "audio")

    # Slide generation (55-80%)
    print(f"\n📊 スライド生成: {slide_count}枚")
    await log_progress(57, f"スライド生成中 (0/{slide_count})", "slides")

    for i in range(1, slide_count + 1):
        # Calculate progress percentage (linear interpolation 57-80%)
        pct = 57 + int((i / slide_count) * (80 - 57))
        if i == slide_count:
            await log_progress(80, f"スライド生成完了 ({i}/{slide_count})", "slides")
        else:
            # Show progress every 2 files
            if i % 2 == 0:
                await log_progress(pct, f"スライド生成中 ({i}/{slide_count})", "slides")

    # Video rendering
    print("\n📊 動画レンダリング")
    await log_progress(82, "動画をレンダリング中...", "video")
    await asyncio.sleep(2)
    await log_progress(100, "動画生成完了", "video")

    # Summary
    print("\n" + "=" * 60)
    print(f"Total progress updates: {len(progress_log)}")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Web Worker Progress Improvement Demo")
    print("=" * 60)
    print("\nSimulating video generation with detailed progress...\n")

    asyncio.run(simulate_progress())

    print("\n✅ Demo complete!")
    print("\nKey improvements:")
    print("  • Script analysis for accurate totals")
    print("  • Real-time file monitoring")
    print("  • Detailed progress messages (X/Y format)")
    print("  • Dynamic percentage calculation")
