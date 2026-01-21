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

## Font Requirements

### Subtitle Font Configuration

**Problem**: Subtitles may appear garbled or display incorrectly on Linux systems.

**Symptoms**:
- Japanese/Chinese/Korean characters not displaying correctly
- Subtitles showing as boxes or question marks
- Subtitles appearing blank despite text being present in composition.json

**Root Cause**:
Remotion uses the fontFamily CSS property for subtitle rendering. The default Arial font may not be available on Linux systems and does not support CJK (Chinese/Japanese/Korean) characters.

**Solution**:
The subtitle fontFamily in `templates.py` is configured with a font stack that prioritizes:
1. Noto Sans JP (Google Fonts - Japanese)
2. Noto Sans CJK JP (System font - Japanese)
3. Yu Gothic (System font - Japanese)
4. Hiragino Sans (macOS - Japanese)
5. Meiryo (Windows - Japanese)
6. Arial (fallback for English)
7. sans-serif (generic fallback)

**Current Configuration** (templates.py:443):
```typescript
fontFamily: '"Noto Sans JP", "Noto Sans CJK JP", "Yu Gothic", "Hiragino Sans", "Meiryo", Arial, sans-serif',
```

**System Font Installation** (Linux):

For best results, install Noto Sans CJK fonts on Linux:

```bash
# Debian/Ubuntu
sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra

# Fedora/RHEL
sudo dnf install google-noto-sans-cjk-jp-fonts

# Arch Linux
sudo pacman -S noto-fonts-cjk
```

**Verification**:

After rendering, check subtitle rendering in the output video:
```bash
# Play video and check subtitle display
ffplay output.mp4

# Extract a frame with subtitles for visual inspection
ffmpeg -i output.mp4 -ss 00:00:05 -vframes 1 subtitle_check.png
```

**Web Fonts Alternative** (not currently implemented):

If system fonts are unreliable, consider using Google Fonts:
```typescript
// Add to remotion project
import '@fontsource/noto-sans-jp';
```

However, this requires additional package installation and increases bundle size.

## pnpm Workspace Compatibility

### Chrome Headless Shell Installation

**Problem**: `pnpm install` fails in temporary download directories when project has `pnpm-workspace.yaml`.

**Symptoms**:
- `npx remotion browser ensure` fails with "could not determine executable to run"
- Chrome Headless Shell download fails with exit code 1
- Error: "No projects found in ..." during pnpm install

**Root Cause**:
When a `pnpm-workspace.yaml` exists at the project root, pnpm operates in workspace mode. It only installs dependencies for packages listed in the workspace configuration and ignores other directories (like `.cache/remotion/_temp_download`).

**Solution**:
Use `--ignore-workspace` flag when installing dependencies outside workspace packages:

```bash
pnpm install --no-frozen-lockfile --ignore-workspace
```

This is implemented in `remotion_renderer.py:207` for the Chrome Headless Shell download process.

**Code Reference**:
```python
# remotion_renderer.py:205-212
# Install remotion CLI in temp directory
# NOTE: --ignore-workspace is required because the project may have
# pnpm-workspace.yaml, and pnpm would otherwise refuse to install
# dependencies outside the workspace-defined packages
subprocess.run(
    ["pnpm", "install", "--no-frozen-lockfile", "--ignore-workspace"],
    cwd=temp_download_dir,
    check=True,
    capture_output=True,
    text=True,
)
```

**When to Consider**:
- If adding new pnpm install commands outside workspace-defined packages
- When debugging dependency installation failures in temporary directories
- When the project uses pnpm workspaces for Remotion project management

## Docker Worker Optimization

### Pre-installed Dependencies

**Problem**: Without optimization, every video render in worker containers would:
- Download Chrome Headless Shell (~109MB, ~30-60 seconds)
- Install Remotion dependencies (~163MB, ~10-30 seconds)

**Solution**: The Docker image pre-installs all dependencies at build time:

1. **Chrome Headless Shell** (`web/worker/Dockerfile:47-56`)
   - Downloaded during image build
   - Cached at `/opt/remotion/chrome-headless-shell`
   - Symlinked to `/app/.cache/remotion/chrome-headless-shell` at runtime
   - **Runtime overhead: 0 seconds**

2. **Remotion Dependencies** (`web/worker/Dockerfile:89-95`)
   - Workspace root `package.json` declares all Remotion packages
   - `pnpm install` runs during image build
   - Shared via pnpm workspace (`node_modules/` at project root)
   - **Runtime overhead: 0 seconds**

**Benefit**:
- **Before**: 40-90 seconds of dependency installation per render
- **After**: Instant - dependencies already present in image

**Maintenance**:
When updating Remotion versions:
1. Update `package.json` (root)
2. Update `web/worker/Dockerfile` (Remotion version in npm install)
3. Rebuild Docker image
4. Run `pnpm install` locally to update `pnpm-lock.yaml`

**Files**:
- `package.json` - Workspace root dependencies (tracked in git)
- `pnpm-lock.yaml` - Dependency version lock (tracked in git)
- `pnpm-workspace.yaml` - Workspace configuration
- `web/worker/Dockerfile` - Build instructions

## Linux System Dependencies

### Chrome Headless Shell Requirements

**Problem**: Chrome headless shell fails to launch with "error while loading shared libraries" errors.

**Symptoms**:
- `Error: Failed to launch the browser process!`
- `libatk-1.0.so.0: cannot open shared object file: No such file or directory`
- Remotion rendering fails with exit code 1

**Root Cause**:
Chrome headless shell requires multiple system libraries that may not be installed by default on Linux systems.

**Solution** (Ubuntu/Debian):

```bash
sudo apt-get update && sudo apt-get install -y \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2t64
```

**Note**: Package names may vary by Ubuntu version:
- Ubuntu 24.04+: `libasound2t64`, `libatk1.0-0t64`, `libcups2t64`
- Ubuntu 22.04 and earlier: `libasound2`, `libatk1.0-0`, `libcups2`

**Solution** (Fedora/RHEL):

```bash
sudo dnf install -y \
  nss \
  nspr \
  atk \
  at-spi2-atk \
  cups-libs \
  libdrm \
  libxkbcommon \
  libXcomposite \
  libXdamage \
  libXfixes \
  libXrandr \
  mesa-libgbm \
  pango \
  cairo \
  alsa-lib
```

**Troubleshooting**:

If you encounter a "missing library" error, use `ldd` to check dependencies:

```bash
# Check which libraries are missing
ldd /path/to/chrome-headless-shell | grep "not found"
```

The Chrome headless shell location is typically:
```
<project_output_dir>/remotion/node_modules/.remotion/chrome-headless-shell/linux64/chrome-headless-shell-linux64/chrome-headless-shell
```

**Reference**: https://remotion.dev/docs/troubleshooting/browser-launch

## Testing Checklist

Before releasing video generation changes:

- [ ] Generate video with BGM enabled
- [ ] Generate video with background video enabled
- [ ] Play in QuickTime Player - no unexpected stops
- [ ] Play in Chrome - no unexpected stops
- [ ] Seek to middle and play - continues smoothly
- [ ] Check audio/video sync at beginning, middle, end
- [ ] Verify subtitle rendering on Linux (Japanese/CJK characters)
- [ ] Check subtitle font fallback on systems without Noto Sans
