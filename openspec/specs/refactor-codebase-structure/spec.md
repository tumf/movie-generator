# Change: Codebase Structure Refactoring

<!-- Original Japanese proposal: openspec-archive/changes/refactor-codebase-structure/proposal.md -->

## Why

Analysis of the entire codebase identified the following issues:

1. **Code Duplication** - File existence checks, retry logic, and subprocess execution patterns are duplicated across multiple locations
2. **Overly Long Functions** - `cli.py::generate()` is 409 lines with excessive responsibilities
3. **Inconsistent Error Handling** - Bare except clauses, mixed exception types
4. **Magic Numbers/Strings** - FPS value 30, directory names, etc. are hardcoded
5. **Lack of Type Safety** - 9 instances of `type: ignore`, absence of TypedDict

These issues impact maintainability, testability, and code reusability.

## What Changes

### Phase 1: Create Utility Modules
- New `src/movie_generator/utils/` package
  - `filesystem.py` - File existence checks, path operations
  - `retry.py` - Retry logic with exponential backoff
  - `subprocess.py` - Subprocess execution helpers
  - `text.py` - Text processing utilities

### Phase 2: Consolidate Constants
- New `src/movie_generator/constants.py`
  - `VideoConstants` - FPS, resolution
  - `FileExtensions` - Supported file extensions
  - `ProjectPaths` - Standard directory names
  - `RetryConfig` - Retry parameters

### Phase 3: Organize Exception Hierarchy
- New `src/movie_generator/exceptions.py`
  - `MovieGeneratorError` - Base exception
  - `ConfigurationError` - Configuration-related errors
  - `RenderingError` - Rendering errors
  - `MCPError` - MCP communication errors

### Phase 4: Split CLI Functions
- Split `cli.py::generate()` into smaller functions
- Split `cli.py::parse_scene_range()` into sub-functions

### Phase 5: Remove Dead Code
- Remove unreachable code in `video/remotion_renderer.py:109-122`
- Remove unused functions or add warnings

### Phase 6: Improve Type Safety
- Introduce TypedDict (CompositionData, PhraseDict)
- Reduce `type: ignore` annotations

## Impact

- Affected specs: None (internal refactoring only)
- Affected code:
  - `src/movie_generator/cli.py`
  - `src/movie_generator/slides/generator.py`
  - `src/movie_generator/audio/voicevox.py`
  - `src/movie_generator/video/remotion_renderer.py`
  - `src/movie_generator/project.py`
  - `src/movie_generator/assets/downloader.py`
  - `src/movie_generator/mcp/client.py`

## Risk

- **Low Risk**: Maintains backward compatibility
- All changes can be implemented incrementally
- Validation via test suite execution after each phase

## Success Criteria

- `uv run pytest` all tests pass
- `uv run mypy src/` no errors
- `uv run ruff check .` no warnings
- Code coverage maintained or improved
