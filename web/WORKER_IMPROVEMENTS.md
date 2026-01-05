# Worker Improvements

## Completed Fixes (2026-01-05)

### 1. VOICEVOX Installation ✅
**Problem**: VOICEVOX dict/onnxruntime files were not being downloaded in Docker build
- `|| true` silently ignored download failures
- Worker failed at audio generation with `FileNotFoundError`

**Solution**:
- Removed `|| true` from download command
- Added verification checks for dict, onnxruntime, models
- Build now fails early if VOICEVOX installation incomplete

**Files Modified**:
- `web/worker/Dockerfile` - Lines 32-45

### 2. Progress Monitoring Path Fix ✅
**Problem**: Worker monitored wrong directories for file progress
- Audio files generated in `audio/` but monitored `audio/ja/`
- Slide files generated in `slides/ja/` but monitored `slides/`

**Solution**:
- Audio monitoring: `audio/` (no subdirectory)
- Slide monitoring: `slides/ja/` (language subdirectory)

**Files Modified**:
- `web/worker/main.py` - Lines 265, 311

### 3. Datetime Deprecation Warning ✅
**Problem**: `datetime.utcnow()` is deprecated in Python 3.13+

**Solution**: Replaced with `datetime.now(UTC)`

**Files Modified**:
- `web/worker/main.py` - Lines 6, 81, 411, 454, 469, 541

### 4. Error Logging Enhancement ✅
**Problem**: When subprocess failed, no detailed error information was logged

**Solution**: Added logging of stdout/stderr on subprocess failure

**Files Modified**:
- `web/worker/main.py` - Lines 295-301, 341-347, 373-376

## Critical Issues Remaining ❌

### 1. Subprocess Architecture (High Priority)
**Problem**: Worker uses `subprocess.run()` to call CLI commands
- Spawns new Python processes unnecessarily
- Cannot report detailed progress during execution
- Error details are incomplete
- Difficult to debug
- Resource inefficient

**Current Implementation**:
```python
# Bad: Subprocess call
result = subprocess.run([
    "movie-generator", "audio", "generate", str(script_path),
    "--force", "--quiet"
], capture_output=True, text=True, timeout=600)

# Can only check progress by monitoring files on disk
await self._monitor_file_progress(...)
```

**Proposed Solution**: Direct Python API calls with callbacks
```python
# Good: Direct function call with progress callback
from movie_generator.audio import generate_audio_for_script

await generate_audio_for_script(
    script_path=script_path,
    output_dir=audio_dir,
    progress_callback=lambda current, total, item: 
        progress_callback(
            start + int((current/total) * (end-start)),
            f"音声生成中 ({current}/{total})",
            "audio"
        )
)
```

**Benefits**:
- Real-time progress updates (not file-based polling)
- Full error context and stack traces
- No process spawning overhead
- Better resource utilization
- Easier testing and debugging

**Implementation Plan**:
1. Extract core logic from CLI commands into reusable functions
2. Add progress callback parameters to these functions
3. Update worker to call functions directly
4. Remove subprocess calls

**Files to Modify**:
- `src/movie_generator/script/generator.py` - Extract script generation
- `src/movie_generator/audio/*.py` - Extract audio generation
- `src/movie_generator/slides/generator.py` - Extract slide generation  
- `src/movie_generator/video/remotion_renderer.py` - Extract video rendering
- `web/worker/main.py` - Replace subprocess calls

### 2. Error Detection (High Priority)
**Problem**: When subprocess fails, worker continues waiting indefinitely
- Monitor task waits for files that will never be created
- No timeout on file monitoring
- Job appears "stuck" with no error visible to user

**Current Issue**:
```python
# subprocess fails silently
result = subprocess.run([...])  # returns non-zero

# But monitor waits forever for files
await monitor_task  # Blocks indefinitely

# Error check never reached
if result.returncode != 0:  # Never executed!
    raise RuntimeError(...)
```

**Solution Applied** (Partial):
- Check `result.returncode` immediately after subprocess
- Cancel monitor_task on failure
- Log detailed error information

**Remaining Issue**: This only works because `subprocess.run()` is synchronous. With direct API calls, need proper task coordination.

### 3. Chrome Headless Shell Installation
**Problem**: Chrome download fails during video rendering
```
subprocess.CalledProcessError: Command '['npx', 'remotion', 'browser', 'ensure']' 
returned non-zero exit status 1.
```

**Solution**: Pre-install Chrome in Docker image
```dockerfile
# Add to Dockerfile after Node.js installation
RUN npx remotion browser ensure \
    && npx remotion browser download chrome-headless-shell
```

**Files to Modify**:
- `web/worker/Dockerfile`

## Testing Checklist

When implementing above fixes:

- [ ] Audio generation reports progress correctly
- [ ] Slide generation reports progress correctly
- [ ] Video rendering reports progress correctly
- [ ] Errors are detected immediately (no indefinite waiting)
- [ ] Error messages include full context
- [ ] Failed jobs are marked as "failed" in database
- [ ] Progress percentages are accurate
- [ ] Multiple concurrent jobs work correctly
- [ ] Job resumption works after worker restart

## Performance Metrics

**Before fixes**:
- Progress updates: File polling every 2s
- Error detection: Never (indefinite wait)
- Process overhead: 3-4 subprocess spawns per job

**After subprocess removal** (estimated):
- Progress updates: Real-time callbacks
- Error detection: Immediate
- Process overhead: Zero (direct function calls)
- Memory usage: ~30% reduction (no duplicate Python processes)

## Migration Notes

When removing subprocess calls:

1. **Backward Compatibility**: Keep CLI commands working for manual use
2. **API Design**: Progress callbacks should be optional (default to no-op)
3. **Error Handling**: Ensure exceptions propagate correctly
4. **Testing**: Add integration tests for worker API calls
5. **Documentation**: Document the new internal API

## See Also

- `PROGRESS_IMPROVEMENTS.md` - Details on progress monitoring implementation
- `docs/REMOTION_BEST_PRACTICES.md` - Remotion-specific issues and solutions
