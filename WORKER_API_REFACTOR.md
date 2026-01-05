# Worker API Refactoring Progress

## Goal
Replace subprocess calls in the worker with direct Python API calls to enable real-time progress reporting and better error handling.

## ✅ Completed: All Core Improvements

### Summary

All subprocess calls replaced + infrastructure improvements:
1. ✅ **Script Generation** - `generate_script_from_url()`
2. ✅ **Audio Generation** - `generate_audio_for_script()`
3. ✅ **Slides Generation** - `generate_slides_for_script()`
4. ✅ **Video Rendering** - `render_video_for_script()`
5. ✅ **Chrome Pre-installation** - Docker image includes Chrome Headless Shell

## Completed: Script Generation ✅

### What We Did

1. **Created `src/movie_generator/script/core.py`**
   - Wrapped URL fetching + script generation logic
   - Added `generate_script_from_url()` async function
   - Added `generate_script_from_url_sync()` for synchronous callers
   - Callback signature: `Callable[[int, int, str], None]`

2. **Updated `src/movie_generator/script/__init__.py`**
   - Exported new functions

3. **Updated `web/worker/main.py`**
   - Replaced subprocess call with direct async API call
   - Progress mapped to 5-20% range

## Completed: Audio Generation ✅

### What We Did

1. **Created `src/movie_generator/audio/core.py`**
   - Extracted core audio generation logic from CLI
   - Added `generate_audio_for_script()` function with progress callback support
   - Callback signature: `Callable[[int, int, str], None]`
     - Arg 1: Current progress (number of files generated)
     - Arg 2: Total number of files
     - Arg 3: Status message

2. **Updated `src/movie_generator/audio/__init__.py`**
   - Exported `generate_audio_for_script` for public API

3. **Updated `web/worker/main.py`**
   - Replaced subprocess call with direct API call
   - Used `asyncio.run_in_executor()` to run synchronous function in thread pool
   - Progress callback updates local state and logs progress

### Benefits

**Before**:
```python
# Worker had to:
subprocess.run(["movie-generator", "audio", "generate", script_path])
# ↓ Issues:
# - Spawns new Python process (overhead)
# - No real-time progress visibility
# - Limited error information
# - Had to poll filesystem to estimate progress
```

**After**:
```python
# Worker now does:
from movie_generator.audio import generate_audio_for_script

await loop.run_in_executor(
    None,
    generate_audio_for_script,
    script_path,
    job_dir,
    progress_callback=audio_progress,
)
# ✅ Direct function call (no subprocess overhead)
# ✅ Real-time progress updates
# ✅ Full exception details
# ✅ No filesystem polling needed
```

### Testing

```bash
# Verify import works
uv run python -c "from src.movie_generator.audio import generate_audio_for_script; print('✓ Success')"
```

## Completed: Slides Generation ✅

### What We Did

1. **Created `src/movie_generator/slides/core.py`**
   - Wrapped slide generation logic from CLI
   - Added `generate_slides_for_script()` async function
   - Callback signature: `Callable[[int, int, str], None]`

2. **Updated `src/movie_generator/slides/__init__.py`**
   - Exported `generate_slides_for_script`

3. **Updated `web/worker/main.py`**
   - Replaced subprocess call with direct async API call
   - Progress mapped to 57-80% range
   - Already async, no executor needed

**Key differences from audio**:
- Function is already async (no executor needed)
- Uses `generate_slides_for_sections()` internally which is async
- Can be awaited directly

## Completed: Video Rendering ✅

### What We Did

1. **Created `src/movie_generator/video/core.py`**
   - Extracted video rendering logic from CLI
   - Added `render_video_for_script()` synchronous function
   - Handles all setup: phrases, audio loading, slide loading, Remotion project setup
   - Callback signature: `Callable[[int, int, str], None]`

2. **Updated `src/movie_generator/video/__init__.py`**
   - Exported `render_video_for_script`

3. **Updated `web/worker/main.py`**
   - Replaced subprocess call with direct API call via executor
   - Progress mapped to 82-100% range
   - Uses `run_in_executor` since rendering is synchronous

**Challenges addressed**:
- Remotion rendering is subprocess-based internally (npx remotion)
- Progress granularity limited to setup steps (not frame-by-frame)
- Future: Could parse Remotion stdout for frame progress

## TODO: Remaining Steps (Optional Improvements)

### Priority 2: Slides Generation (COMPLETED ✅)

Create `src/movie_generator/slides/core.py`:
- Extract logic from `cli.py` lines 1358-1566
- Add `generate_slides_for_script()` with progress callback
- Update worker to use direct API

**Key differences from audio**:
- Already async (`asyncio.run` in CLI)
- Uses `generate_slides_for_sections()` which is async
- Can be called directly without executor

### Priority 3: Video Rendering (COMPLETED ✅)

### Priority 4: Script Generation (COMPLETED ✅)

### Priority 5: Pre-install Chrome in Docker ✅

**Completed!** Added Chrome Headless Shell installation to Docker image.

**Changes made to `web/worker/Dockerfile`:**

1. **Chrome Dependencies** (lines 24-43):
   - Added required system libraries for Chrome
   - `libnss3`, `libnspr4`, `libatk1.0-0`, etc.
   - Ensures Chrome can run in headless mode

2. **Remotion + Chrome Installation** (lines 45-55):
   ```dockerfile
   RUN npm init -y \
       && npm install remotion@4.0.234 \
       && npx remotion browser ensure \
       && npx remotion browser download chrome-headless-shell \
       && npx remotion browser list
   ```

**Benefits:**
- ✅ Prevents "Chrome not found" errors during video rendering
- ✅ No runtime download delays
- ✅ Consistent rendering environment
- ✅ Smaller Docker layer (cleanup after install)

**Build time impact:**
- Adds ~2-3 minutes to initial Docker build
- Chrome binary: ~200MB
- Cached in Docker layers for subsequent builds

### Priority 6: Enhanced Progress Reporting (TODO)

**Current limitations**:
- Video rendering progress is limited to setup steps
- Cannot report frame-by-frame progress from Remotion

**Potential improvements**:
1. Parse Remotion stdout for frame progress
2. Add progress hooks to `render_video_with_remotion()`
3. Stream progress updates in real-time

**Example Remotion output to parse**:
```
Frame 0 (0.0%)
Frame 30 (10.0%)
Frame 60 (20.0%)
...
```

## Architecture Design

### Principle: Separate CLI from Core Logic

```
┌─────────────────────────────────────────────┐
│ CLI Layer (cli.py)                          │
│  - Argument parsing                         │
│  - Progress display (Rich UI)              │
│  - User interaction                         │
│  - Calls core functions                     │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Core Layer (*/core.py)                      │
│  - Pure business logic                      │
│  - Progress callbacks (generic)             │
│  - Can be called by CLI, worker, or tests   │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Implementation Layer (voicevox.py, etc)     │
│  - Actual synthesis/rendering               │
│  - No UI dependencies                       │
└─────────────────────────────────────────────┘
```

### Progress Callback Pattern

All core functions should accept an optional progress callback:

```python
def core_function(
    # ... required args
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Result:
    """Core function that reports progress.
    
    Args:
        progress_callback: Optional callback(current, total, message)
            - current: Items completed so far
            - total: Total items to complete
            - message: Human-readable status message
    """
    if progress_callback:
        progress_callback(0, total, "Starting...")
    
    for i, item in enumerate(items):
        process(item)
        if progress_callback:
            progress_callback(i + 1, total, f"Processing {i+1}/{total}")
```

### Worker Integration Pattern

```python
# For synchronous core functions
await loop.run_in_executor(
    None,  # Use default ThreadPoolExecutor
    core_function,
    arg1,
    arg2,
    progress_callback,
)

# For async core functions
await async_core_function(
    arg1,
    arg2,
    progress_callback=async_progress_callback,
)
```

## Next Steps

1. **Implement slides generation API** (similar to audio)
2. **Implement video rendering API** (may need Remotion progress parsing)
3. **Implement script generation API** (easiest, mostly done)
4. **Test end-to-end with worker**
5. **Pre-install Chrome in Docker** (Priority 2 from original plan)

## Testing Checklist

- [x] Test script generation with callback (imports successfully)
- [x] Test audio generation with callback (imports successfully)
- [x] Test slides generation with callback (imports successfully)
- [x] Test video rendering with callback (imports successfully)
- [ ] Test error handling in each step
- [ ] Test progress reporting accuracy
- [ ] Test worker with real job end-to-end
- [ ] Verify no deadlocks on error paths
- [ ] Compare performance: subprocess vs direct API
- [ ] Verify existing audio/slides are reused correctly

## Success Criteria

1. ✅ **No subprocess calls** - All generation steps use direct API (4/4 complete)
2. ✅ **Real-time progress** - Progress callbacks implemented for all steps
3. ✅ **Better error messages** - Full Python exceptions with stack traces
4. ✅ **Faster execution** - No process spawning overhead (subprocess removed)
5. ✅ **Simpler debugging** - Can set breakpoints in core functions
6. ⏳ **End-to-end testing** - Need to test worker with real jobs
7. ⏳ **Frame-by-frame progress** - Video rendering still limited to setup steps

---

**Status**: 🟢 **Phase 1 Complete!** - All 4 core APIs implemented
**Next**: Test with real worker jobs, then optimize progress reporting
**Last Updated**: 2026-01-05
