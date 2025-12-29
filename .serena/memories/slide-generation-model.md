# Slide Generation Model - IMPORTANT

## Required Model

**DO NOT CHANGE**: `google/gemini-3-pro-image-preview`

## Forbidden

- **NEVER** use `google/gemini-2.5-flash-image-preview`
- **NEVER** change the model without explicit user request

## Reason

- `gemini-3-pro-image-preview` works correctly for image generation
- `scripts/generate_slides.py` uses this model and succeeds
- Changing to other models was done without evidence and caused confusion

## API Request Format

The `content` field should be a **string**, not an array:

```python
# CORRECT (matches generate_image.py)
"content": prompt

# WRONG
"content": [{"type": "text", "text": prompt}]
```

The `modalities` order should be `["image", "text"]`:

```

## Files Using This Model

- `src/movie_generator/slides/generator.py`
- `src/movie_generator/config.py` (SlidesLLMConfig default)
- `scripts/generate_slides.py`
- `config/default.yaml`

## Root Cause of CLI Bug (Fixed)

The CLI was using `Config()` without loading `config/default.yaml`, so it used the 
default `LLMConfig.model` which was `openai/gpt-5.2` (not an image model).

Fixed by creating `SlidesLLMConfig` with the correct default model.
