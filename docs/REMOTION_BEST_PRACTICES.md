# Remotion Best Practices

This document captures lessons learned and best practices for using Remotion in this project.

## Audio File Requirements

### BGM Files: No Attached Pictures (Album Art)

**Problem**: MP3 files with embedded album art cause video playback to stop at irregular intervals.

**Symptoms**:
- Video stops playing every 10-15 seconds
- Resuming playback continues from where it stopped
- Stopping occurs at same time offset regardless of seek position
- Only affects videos with BGM enabled

**Root Cause**:
MP3 files with album art contain two streams:
```
Stream #0: audio/mp3 (the actual music)
Stream #1: video/mjpeg (album art, marked as attached_pic)
```

When Remotion's FFmpeg-based audio processing encounters this "fake video stream", it causes timing synchronization issues in the rendered output. The resulting MP4 file has subtle audio/video sync problems that manifest as playback interruptions.

**Solution**:
The system automatically strips attached pictures from BGM files during the copy-to-public phase. This is handled by `_strip_attached_picture()` in `remotion_renderer.py`.

**Manual Fix** (if needed):
```bash
# Remove album art from MP3
ffmpeg -i input.mp3 -map 0:a:0 -c:a copy output.mp3

# Verify only audio stream remains
ffprobe -v error -show_entries stream=codec_type,codec_name -of csv=p=0 output.mp3
# Should output: audio,mp3
```

**Prevention**:
- Use audio files without embedded artwork
- Prefer M4A (AAC) format which handles metadata more cleanly
- The system now auto-strips album art, but clean source files are still preferred

### Audio Format Recommendations

| Format | Recommendation | Notes |
|--------|----------------|-------|
| MP3 (no art) | Good | Widely compatible |
| MP3 (with art) | Auto-fixed | Album art stripped automatically |
| M4A/AAC | Best | Clean metadata handling |
| WAV | Good | Large file size |
| OGG | Avoid | Browser compatibility issues |

## Video Background Requirements

### Loop Duration Matching

When using video backgrounds with looping, ensure `loopDurationInFrames` matches the actual video duration:

```typescript
// Good: Duration calculated from actual video
loopDurationInFrames={240} // 8 seconds at 30fps

// Bad: Arbitrary value causing visual glitches
loopDurationInFrames={150}
```

The system automatically calculates `loopDurationInFrames` from the background video using FFprobe.

## Component Best Practices

### Audio Component

```typescript
// Phrase audio - simple, no loop
<Audio src={staticFile(audioFile)} />

// BGM audio - with volume control and loop
<Audio
  src={staticFile(path)}
  volume={currentVolume}
  loop={loop}
/>
```

**Avoid**:
- `pauseWhenBuffering` - Can cause unexpected pauses in rendered output
- Complex volume calculations that depend on external state

### Sequence and Timing

```typescript
// Each phrase gets its own Sequence
{scenes.map((scene) => (
  <Sequence
    key={scene.id}
    from={scene.startFrame}
    durationInFrames={scene.durationFrames}
  >
    <AudioSubtitleLayer ... />
  </Sequence>
))}
```

**Key Points**:
- Use `from` and `durationInFrames` for precise timing
- Keep audio and visuals in the same Sequence for sync
- Total duration should match sum of all phrase durations

## Debugging Playback Issues

### Step 1: Check Audio Streams

```bash
# List all streams in source audio
ffprobe -v error -show_entries stream=codec_type,codec_name -of csv=p=0 <audio_file>
```

Expected for clean audio: `audio,mp3` or `audio,aac`
Problem indicator: Multiple lines including `video,mjpeg`

### Step 2: Analyze Output MP4

```bash
# Check video properties
ffprobe -v error -show_entries format=duration,bit_rate -of default=nw=1 output.mp4

# Check for timestamp discontinuities
ffprobe -v error -select_streams a:0 -show_packets -read_intervals 0%+30 \
  -show_entries packet=pts_time,dts_time -of csv=p=0 output.mp4 | head -50
```

### Step 3: Test with ffplay

```bash
# If ffplay works but QuickTime/Chrome don't, it's likely a container issue
ffplay output.mp4
```

## Known Issues and Workarounds

### Issue: Keyframe Interval Too Large

**Symptom**: Seeking is slow or inaccurate

**Solution**: Remotion uses reasonable defaults, but you can add to `remotion.config.ts`:
```typescript
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
```

### Issue: Rendering Timeout

**Symptom**: `delayRender` timeout errors

**Solution**: Add to `remotion.config.ts`:
```typescript
Config.setDelayRenderTimeoutInMilliseconds(120000); // 2 minutes
```

## Configuration Reference

### remotion.config.ts

```typescript
import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setDelayRenderTimeoutInMilliseconds(120000);
```

### composition.json Structure

```json
{
  "title": "project-name",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "phrases": [...],
  "transition": {
    "type": "fade",
    "duration_frames": 15,
    "timing": "linear"
  },
  "background": {
    "type": "video",
    "path": "backgrounds/bg.mp4",
    "fit": "cover",
    "loopDurationInFrames": 240
  },
  "bgm": {
    "path": "bgm/music.mp3",
    "volume": 0.3,
    "fade_in_seconds": 2.0,
    "fade_out_seconds": 2.0,
    "loop": true
  }
}
```

## Testing Checklist

Before releasing video generation changes:

- [ ] Generate video with BGM enabled
- [ ] Generate video with background video enabled
- [ ] Play in QuickTime Player - no unexpected stops
- [ ] Play in Chrome - no unexpected stops
- [ ] Seek to middle and play - continues smoothly
- [ ] Check audio/video sync at beginning, middle, end
