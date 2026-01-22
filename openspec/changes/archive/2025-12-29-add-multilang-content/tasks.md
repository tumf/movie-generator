# Implementation Tasks

## 1. Configuration Schema Update
- [x] 1.1 Add `languages: list[str]` field to `ContentConfig` in `config.py:49`
- [x] 1.2 Set default value to `["ja"]` for backward compatibility
- [x] 1.3 Update YAML generation to include `languages` field with comment
- [x] 1.4 Add test case for multilang config in `tests/test_config.py`

## 2. Script Generation Multi-Language Support
- [x] 2.1 Create separate prompt templates for Japanese (`SCRIPT_GENERATION_PROMPT_JA`) and English (`SCRIPT_GENERATION_PROMPT_EN`)
- [x] 2.2 Add `language: str` parameter to `generate_script()` function
- [x] 2.3 Implement prompt template selection based on language code
- [x] 2.4 English prompt returns empty pronunciations array

## 3. Slide Generation Multi-Language Support
- [x] 3.1 Add `language: str` parameter to `generate_slides_for_sections()` function
- [x] 3.2 Create language-specific subdirectory structure: `output_dir/{language}/`
- [x] 3.3 Update slide path generation to use language subdirectory
- [x] 3.4 Update logging to show current language being processed

## 4. Multi-Language Integration Logic
- [x] 4.1 Create `multilang.py` module with `generate_multilang_content()` function
- [x] 4.2 Implement loop over configured languages
- [x] 4.3 Generate language-specific script files: `script_{lang}.yaml`
- [x] 4.4 Save scripts with proper YAML structure including pronunciations
- [x] 4.5 Call slide generation for each language
- [x] 4.6 Return dictionary mapping language codes to VideoScript objects

## 5. Scripts Update
- [x] 5.1 Update `scripts/generate_slides.py` to detect language-specific script files
- [x] 5.2 Add fallback to legacy `script.yaml` (treat as Japanese)
- [x] 5.3 Process each language sequentially
- [x] 5.4 Report results per language and provide final summary

## 6. Testing and Validation
- [x] 6.1 Add test for default language configuration
- [x] 6.2 Add test for multilang config loading
- [x] 6.3 Create example config file `test-multilang.yaml`
- [x] 6.4 Run pytest to verify all tests pass
- [x] 6.5 Manual test of config loading

## 7. Documentation
- [x] 7.1 Create `docs/MULTILANG_FEATURE.md` with usage guide
- [x] 7.2 Document configuration format
- [x] 7.3 Document output structure
- [x] 7.4 Provide Python API usage examples
- [x] 7.5 Document backward compatibility behavior
