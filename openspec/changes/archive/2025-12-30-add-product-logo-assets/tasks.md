# Implementation Tasks

## 1. Script Model Extension

- [x] 1.1 Add `logo_assets` field to `VideoScript` dataclass
  - Format: `logo_assets: list[dict[str, str]]` (`[{"name": "ProductName", "url": "https://..."}]`)
- [x] 1.2 Add logo URL output instructions to script generation prompt
  - When blog content contains products/services, list official logo URLs

## 2. Asset Management Module Implementation

- [x] 2.1 Create `src/movie_generator/assets/__init__.py`
- [x] 2.2 Implement `src/movie_generator/assets/downloader.py`
  - Image download from URL functionality
  - Filename sanitization (generate safe filenames from product names)
  - Prevent duplicate downloads (skip if file already exists)
- [x] 2.3 Implement `src/movie_generator/assets/converter.py`
  - SVG→PNG conversion functionality (cairosvg)
  - Error handling on conversion failure
- [x] 2.4 Add dependencies to `pyproject.toml` (cairosvg, pillow)

## 3. Project Structure Update

- [x] 3.1 Add `logos_dir` property to `project.py` (`assets/logos/`)
- [x] 3.2 Create `assets/logos/` directory during project initialization

## 4. Slide Generation Integration

- [x] 4.1 Add `download_logo_assets()` function to `slides/logo_downloader.py`
  - Retrieve logo URL list from script
  - Download and convert each logo
  - Return list of paths to downloaded logos
- [x] 4.2 Extend `generate_slide()` function
  - Add `logo_context` parameter
  - Include logo asset information in prompt
- [x] 4.3 Error handling
  - Display warning on download failure and continue
  - Same for conversion failure

## 5. Testing and Documentation

- [x] 5.1 Add unit tests
  - `tests/test_assets_downloader.py` (sanitize_filename test)
- [ ] 5.2 Add integration tests
  - `tests/test_logo_integration.py` - End-to-end logo download → slide generation (future implementation)
- [x] 5.3 Update README
  - Add "Logo Asset Management" to feature list
- [x] 5.4 Add feature description to `AGENTS.md`
