# Worker Testing Guide

## Quick Verification

### 1. Test Imports (Local)

```bash
cd /home/tumf/projects/movie-generator

# Test all core modules import correctly
uv run python -c "
from src.movie_generator.script import generate_script_from_url
from src.movie_generator.audio import generate_audio_for_script
from src.movie_generator.slides import generate_slides_for_script
from src.movie_generator.video import render_video_for_script
print('✓ All core modules ready!')
"
```

**Expected output:**
```
✓ All core modules ready!
```

### 2. Rebuild Docker Image

```bash
cd /home/tumf/projects/movie-generator/web/worker

# Rebuild with Chrome pre-installation
docker-compose build --no-cache

# Expected: Build succeeds, shows Chrome installation logs
```

**Watch for these log messages:**
- `Chrome Headless Shell installed successfully`
- `npx remotion browser list` output showing chrome-headless-shell
- `VOICEVOX installation verified successfully`

### 3. Start Worker

```bash
cd /home/tumf/projects/movie-generator/web/worker

# Start worker and dependencies
docker-compose up

# Expected: Worker starts without errors
```

**Expected logs:**
```
worker_1  | INFO:__main__:Worker started
worker_1  | INFO:__main__:Checking for stuck jobs...
worker_1  | INFO:__main__:No stuck jobs found
```

## End-to-End Test

### Test Scenario: Generate Video from URL

1. **Submit a test job** (via frontend or API):
   ```bash
   # Example: Using curl to submit job
   curl -X POST http://localhost:8090/api/collections/jobs/records \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com/blog",
       "status": "pending"
     }'
   ```

2. **Watch worker logs**:
   ```bash
   docker-compose logs -f worker
   ```

3. **Expected progress sequence**:
   ```
   INFO: Starting job <job_id>
   INFO: Generating script for job <job_id>
   DEBUG: Script progress: 0/100 - Fetching content from URL...
   DEBUG: Script progress: 20/100 - Parsing HTML content...
   DEBUG: Script progress: 40/100 - Generating script with LLM...
   DEBUG: Script progress: 100/100 - Script generation complete
   
   INFO: Generating audio for job <job_id>
   DEBUG: Audio progress: 0/50
   DEBUG: Audio progress: 25/50
   DEBUG: Audio progress: 50/50
   
   INFO: Generating slides for job <job_id>
   DEBUG: Slides progress: 0/10
   DEBUG: Slides progress: 10/10
   
   INFO: Rendering video for job <job_id>
   DEBUG: Video progress: 0/100 - Loading script...
   DEBUG: Video progress: 40/100 - Rendering video with Remotion...
   DEBUG: Video progress: 100/100 - Video rendering complete
   
   INFO: Completed job <job_id>
   ```

4. **Verify output**:
   ```bash
   # Check job data directory
   ls -la /app/data/jobs/<job_id>/
   
   # Expected files:
   # - script.yaml
   # - audio/phrase_0000.wav, phrase_0001.wav, ...
   # - slides/ja/slide_0000.png, slide_0001.png, ...
   # - output.mp4
   ```

5. **Check job status in PocketBase**:
   - Status should be `completed`
   - Progress should be `100`
   - `video_path` should point to output.mp4
   - `completed_at` timestamp should be set

## Testing Checklist

### Core Functionality

- [ ] **Script Generation**
  - [ ] URL fetching works
  - [ ] HTML parsing succeeds
  - [ ] LLM generates valid YAML
  - [ ] Progress updates appear (5-20%)
  - [ ] Errors are caught and reported

- [ ] **Audio Generation**
  - [ ] VOICEVOX synthesizes audio
  - [ ] Audio files are created
  - [ ] Existing files are reused
  - [ ] Progress updates appear (22-55%)
  - [ ] Multi-speaker mode works (if configured)

- [ ] **Slides Generation**
  - [ ] API key is used correctly
  - [ ] Slides are generated/downloaded
  - [ ] Progress updates appear (57-80%)
  - [ ] Failed slides are handled gracefully

- [ ] **Video Rendering**
  - [ ] Remotion project is set up
  - [ ] Chrome Headless Shell is found
  - [ ] Video is rendered successfully
  - [ ] Progress updates appear (82-100%)
  - [ ] Output file exists and is playable

### Error Handling

- [ ] **Missing API Key**
  - [ ] Script generation fails gracefully
  - [ ] Slides generation fails gracefully
  - [ ] Error message is clear

- [ ] **Invalid URL**
  - [ ] Script generation reports error
  - [ ] Job status is set to `failed`
  - [ ] Error message explains the issue

- [ ] **VOICEVOX Failure**
  - [ ] Audio generation reports error
  - [ ] Job status is set to `failed`
  - [ ] Stack trace is logged

- [ ] **Remotion Failure**
  - [ ] Video rendering reports error
  - [ ] Job status is set to `failed`
  - [ ] Chrome issues are identified

### Progress Reporting

- [ ] **Real-time Updates**
  - [ ] Progress updates appear within 1-2 seconds
  - [ ] Progress percentage is accurate
  - [ ] Progress message is descriptive

- [ ] **Database Updates**
  - [ ] `progress` field updates in real-time
  - [ ] `progress_message` field updates
  - [ ] `current_step` field updates

### Performance

- [ ] **Execution Time**
  - [ ] No subprocess overhead
  - [ ] Faster than old implementation
  - [ ] Compare before/after benchmarks

- [ ] **Resource Usage**
  - [ ] Memory usage is reasonable
  - [ ] CPU usage is consistent
  - [ ] No memory leaks

## Debugging

### Worker Not Starting

```bash
# Check logs
docker-compose logs worker

# Common issues:
# 1. PocketBase not accessible
# 2. Environment variables missing
# 3. Port conflicts
```

### Progress Not Updating

```bash
# Enable debug logging
docker-compose exec worker python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"

# Check if callbacks are being called
grep "progress:" /var/log/worker.log
```

### Video Rendering Fails

```bash
# Check if Chrome is installed
docker-compose exec worker npx remotion browser list

# Expected output:
# chrome-headless-shell: <path>

# If missing, rebuild Docker image
docker-compose build --no-cache
```

### Audio Generation Fails

```bash
# Verify VOICEVOX environment variables
docker-compose exec worker env | grep VOICEVOX

# Expected:
# VOICEVOX_DICT_DIR=/opt/voicevox/dict/open_jtalk_dic_utf_8-1.11
# VOICEVOX_MODEL_PATH=/opt/voicevox/models/vvms/0.vvm
# VOICEVOX_ONNXRUNTIME_PATH=/opt/voicevox/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3
```

## Benchmarking

### Compare Before/After

**Before (subprocess):**
```bash
time docker-compose exec worker movie-generator generate <URL>
```

**After (direct API):**
```bash
time docker-compose exec worker python -c "
import asyncio
from pathlib import Path
from movie_generator.script import generate_script_from_url

asyncio.run(generate_script_from_url(
    url='<URL>',
    output_dir=Path('/tmp/test'),
    api_key='...'
))
"
```

**Expected improvement:**
- 10-20% faster execution
- No subprocess spawn overhead
- More accurate progress reporting

## Success Criteria

✅ **All tests pass**
✅ **Progress updates in real-time**
✅ **No Chrome errors**
✅ **Video renders successfully**
✅ **Error messages are clear**
✅ **Performance is better than before**

## Known Issues

### Issue 1: Frame-by-frame progress not available
**Status:** Known limitation  
**Impact:** Video progress limited to setup steps (82-100%)  
**Workaround:** Future enhancement to parse Remotion stdout

### Issue 2: Type checker errors in worker
**Status:** Pre-existing  
**Impact:** None (runtime works correctly)  
**Files:** `web/worker/main.py` - httpx import, callable type hints

## Next Steps

After testing passes:
1. Monitor production worker for issues
2. Collect performance metrics
3. Implement frame-level progress (Priority 6)
4. Consider async VOICEVOX wrapper for better progress
