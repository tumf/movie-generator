# Design: Product Logo Asset Management

## Context

Current slide generation only passes text prompts to the LLM for image generation. When product or service logos are needed, the LLM generates arbitrary images, failing to accurately represent the actual products.

By downloading correct logos from official websites and providing them as reference information to the LLM during slide generation, we can achieve more accurate and respectful representation.

## Goals / Non-Goals

### Goals

- LLM recognizes products/services from blog content and automatically identifies required logo URLs
- Automatically download identified logos and save them as project assets
- Automatic SVG to PNG conversion
- Integrate logo information into slide generation prompts

### Non-Goals

- Manual logo URL specification (all determined automatically by LLM)
- Logo editing/modification features
- Logo license management

## Decisions

### 1. Asset Storage Location

**Decision**: Store in `projects/<name>/assets/logos/`

**Rationale**:
- Different projects may use different logos
- Maintains consistency with existing `assets/audio/`, `assets/slides/`
- Logos can be cleaned up together when deleting a project

**Alternatives considered**:
- Global cache (`~/.cache/movie-generator/logos/`)
  - Rejected: Few use cases for cross-project logo sharing, and management would be complex

### 2. SVG→PNG Conversion Tool

**Decision**: Use `cairosvg` library

**Rationale**:
- Python native, easy to install
- High-quality SVG rendering
- Minimal dependencies

**Alternatives considered**:
- Pillow + `svglib`: Unstable rendering quality
- ImageMagick: High system dependency, complex installation
- Inkscape CLI: Heavyweight, high installation overhead

### 3. How to Pass Logos to LLM

**Decision**: Phase 1 implements logo download and textual prompt description. Consider future expansion to multimodal input.

**Rationale**:
- Current OpenRouter API may not support image input
- First verify effectiveness with text descriptions ("Include logo for ProductX in the top-right corner")
- Easy to extend when image input API becomes available

**Phase 2 Expansion**:
- Encode logo images in base64 and send as multimodal input
- Enables more accurate logo representation

### 4. Script Output Format

**Decision**: LLM outputs `logo_assets` field during script generation
```yaml
logo_assets:
  - name: "ProductX"
    url: "https://example.com/logo.svg"
  - name: "ServiceY"
    url: "https://example.com/service-logo.png"
sections:
  - title: "..."
    narration: "..."
```

**Rationale**:
- LLM automatically recognizes product names from blog content
- LLM infers or searches for official logo URLs
- No manual user configuration required
- `name` field used to generate filenames (sanitized)

## Risks / Trade-offs

### Risk 1: Download Failure

**Risk**: Download may fail due to network errors or invalid URLs

**Mitigation**:
- Implement retry logic (up to 3 attempts)
- Display warning on failure and continue without logo
- Offer user the option to manually download

### Risk 2: SVG Conversion Failure

**Risk**: Conversion may fail on complex SVGs or non-standard formats

**Mitigation**:
- Save original SVG file on conversion error
- Display warning message prompting user to manually convert to PNG
- Recommend using PNG URLs directly

### Risk 3: LLM Cannot Correctly Infer Logo URLs

**Risk**: LLM outputs incorrect logo URLs or cannot find official logo URLs

**Mitigation**:
- Explicitly instruct in prompt: "Output accurate logo URLs from official sites"
- Utilize LLM's web search capability if available
- Display warning on download failure and continue slide generation
- Consider future mechanism for users to manually correct logo URLs

### Risk 4: Logos Not Reflected in Generated Slides

**Risk**: Image generation LLM may not accurately reflect logo information even when included in prompt

**Mitigation**:
- Prompt engineering with clear instructions ("MUST include logo")
- Migrate to multimodal input in Phase 2
- Improve prompts based on user feedback

## Migration Plan

### Step 1: Add New Feature (No Impact on Existing Features)

- `logo_assets` field automatically output by LLM (optional)
- If LLM determines logos are unnecessary, outputs empty list or omits field
- Maintains compatibility with existing script files

### Step 2: Prompt Adjustment and Testing

- Add logo URL output instructions to script generation prompt
- Test with multiple real blogs to verify LLM can correctly infer logo URLs
- Improve prompt if inference accuracy is low

### Step 3: Collect User Feedback

- Evaluate logo URL accuracy from actual usage examples
- Consider adding manual correction feature if needed
- Assess need for Phase 2 (multimodal input)

### Rollback

- Remove logo URL output instructions from script generation prompt
- Downloaded logos remain in `assets/logos/` but are not used

## Open Questions

1. **LLM Logo URL Inference Accuracy**: How accurately can the LLM infer official logo URLs?
   - → Verify through testing with actual blogs
   - Improve prompt engineering if accuracy is low
   - Add manual correction feature as last resort

2. **Logo Size Optimization**: Should we resize logos upon download?
   - → Phase 1 preserves original size, expecting LLM to scale appropriately
   - Consider resizing to optimal size (e.g., 512x512) in Phase 2

3. **Logo Placement**: How to specify in prompt?
   - → Initial implementation uses generic instruction ("Include logo appropriately")
   - Add detail based on user feedback

4. **Multiple Logos**: What's the priority when including multiple logos in one slide?
   - → Initial implementation includes all logos in prompt
   - Feature to select logos per section is future enhancement
