# Web Worker Progress Improvements

## Overview

Improved progress reporting in the web worker to show detailed, real-time progress for audio and slide generation based on actual file counts.

## Changes

### Before

- Fixed progress percentages (10%, 30%, 40%, 60%, 80%, 100%)
- Generic messages like "音声を生成中..." without item counts
- No correlation between actual work done and progress shown

### After

- **Dynamic progress calculation** based on actual file creation
- **Detailed messages** showing current/total counts: "音声生成中 (5/20)"
- **Real-time monitoring** of audio and slide file creation
- **Accurate percentage** interpolated from actual progress

## Implementation Details

### 1. Script Analysis (`_count_script_items`)

After script generation, the worker reads `script.yaml` to count:
- **Phrase count**: Total narrations across all sections
- **Slide count**: Total sections (1 slide per section)

This provides the denominator for progress calculation.

### 2. File Progress Monitoring (`_monitor_file_progress`)

Monitors a directory for file creation in real-time:
- Polls directory every 2 seconds
- Counts files matching pattern (`phrase_*.wav`, `slide_*.png`)
- Updates progress based on `(current/total)` ratio
- Interpolates percentage between `progress_start` and `progress_end`

### 3. Progress Allocation

| Phase | Percentage Range | Description |
|-------|-----------------|-------------|
| Script generation | 0-20% | LLM-based script creation |
| Audio generation | 20-55% | VOICEVOX synthesis (monitored) |
| Slide generation | 55-80% | Image generation (monitored) |
| Video rendering | 80-100% | Remotion rendering |

Audio and slide phases use the largest ranges because they are the most time-consuming and have measurable progress.

### 4. Example Progress Flow

For a video with 20 phrases and 8 slides:

```
5%: スクリプトを生成中...
20%: スクリプト生成完了
22%: 音声生成中 (0/20)
27%: 音声生成中 (3/20)
32%: 音声生成中 (6/20)
...
55%: 音声生成完了 (20/20)
57%: スライド生成中 (0/8)
62%: スライド生成中 (2/8)
68%: スライド生成中 (4/8)
...
80%: スライド生成完了 (8/8)
82%: 動画をレンダリング中...
100%: 動画生成完了
```

## Benefits

1. **User Experience**: Users see meaningful progress instead of static messages
2. **Transparency**: Actual work done is visible (e.g., "5/20 audio files")
3. **Debugging**: Easier to identify where generation is stuck
4. **Predictability**: Progress percentage reflects actual completion

## Future Improvements

### Phase 2: Direct API Integration

Currently using `subprocess` with file monitoring. Future improvements:
- Call Python APIs directly instead of CLI commands
- Pass progress callbacks to underlying functions
- Get real-time progress from LLM/VOICEVOX/image generation
- Support cancellation mid-generation

### Potential Enhancements

1. **Bandwidth-aware progress**: Account for file sizes, not just counts
2. **Estimated time remaining**: Calculate ETA based on average time per item
3. **Substep progress**: Show progress within each audio/slide generation
4. **Retry indication**: Show when retries occur (e.g., slide generation failures)

## Testing

Run tests:
```bash
uv run pytest web/tests/test_worker_progress.py -v
```

Key test scenarios:
- ✓ Counting phrases and slides from script.yaml
- ✓ File monitoring with simulated creation
- ✓ Full generate_video progress flow
- ✓ Edge cases (zero files, missing directories)

## Migration Notes

No breaking changes. The progress callback interface remains the same:
```python
async def progress_callback(progress: int, message: str, step: str) -> None
```

The implementation is backward-compatible with existing PocketBase job records.
