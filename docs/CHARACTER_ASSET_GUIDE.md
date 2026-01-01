# Character Asset Creation Guide for Designers

This guide provides specifications and instructions for creating character animation assets for the Movie Generator project.

## Overview

Character assets are used to display animated characters alongside video slides. The system supports:
- **Static display** with configurable positioning
- **Lip sync** animation during speech
- **Blinking** animation at regular intervals
- **Motion animations** (sway/bounce)

## Asset Requirements

### File Format
- **Format**: PNG with transparency (alpha channel)
- **Color Mode**: RGBA
- **Bit Depth**: 8-bit per channel minimum

### Image Specifications

| Specification | Requirement | Notes |
|--------------|-------------|-------|
| **Dimensions** | 512x512px to 1024x1024px | Square aspect ratio required |
| **Background** | Transparent (alpha channel) | Essential for proper layering |
| **DPI** | 72 DPI minimum | 144 DPI recommended for quality |
| **File Size** | < 500KB per image | Optimize for web delivery |
| **Character Position** | Centered in canvas | Consistent across all variants |

### Character Framing

**Recommended composition:**
- Full-body or bust-up (shoulders and above)
- Character should occupy 70-85% of canvas height
- Leave margin space on all sides (minimum 5% of canvas)
- Ensure character elements don't touch canvas edges

## Asset Set Structure

Each character requires **3 image variants** for full animation support:

### 1. Base Image (Required)
**Filename**: `base.png`

**State**:
- Mouth: **Closed** (neutral expression)
- Eyes: **Open** (looking forward)
- Expression: Neutral or character's default personality

**Purpose**: Default idle state, displayed when not speaking or blinking.

---

### 2. Mouth Open Image (Optional, for lip sync)
**Filename**: `mouth_open.png`

**State**:
- Mouth: **Open** (speaking position)
- Eyes: **Open** (same as base)
- Expression: Speaking naturally

**Purpose**: Alternates with base image during speech (0.1-second intervals).

**Design Guidelines**:
- Keep everything identical to `base.png` **except the mouth**
- Mouth opening should be natural speaking position (not shouting/singing)
- Maintain same head/body position as base
- Only the mouth shape changes

---

### 3. Eye Close Image (Optional, for blinking)
**Filename**: `eye_close.png`

**State**:
- Mouth: **Closed** (same as base)
- Eyes: **Closed** (blinking)
- Expression: Same as base

**Purpose**: Briefly displayed every 3 seconds for 0.2 seconds.

**Design Guidelines**:
- Keep everything identical to `base.png` **except the eyes**
- Eyes should be naturally closed (not squeezed shut)
- Maintain same head/body position as base
- Eyelashes/eyelids in closed position

## Layer Alignment (Critical!)

### Positioning Consistency

All three images **must be pixel-perfect aligned**:

```
base.png          mouth_open.png    eye_close.png
┌────────┐        ┌────────┐        ┌────────┐
│  O O   │        │  O O   │        │  - -   │
│   ▬    │   →    │   O    │   →    │   ▬    │
│  body  │        │  body  │        │  body  │
└────────┘        └────────┘        └────────┘
```

**Alignment Checklist**:
- [ ] Same canvas size for all images (e.g., all 1024x1024px)
- [ ] Character head position identical in all variants
- [ ] Body position unchanged across variants
- [ ] Hair/accessories in same position
- [ ] Only mouth or eyes differ between variants

### Verification Method

**Photoshop/GIMP**:
1. Open all 3 images as layers in one document
2. Use layer blending or visibility toggle
3. Verify only mouth/eyes change when toggling layers
4. Check for "ghosting" or double-edges (indicates misalignment)

**After Effects/Premiere**:
1. Import all 3 images to timeline
2. Stack on same frame
3. Toggle visibility - should see smooth transitions

## Directory Structure

Save assets in the following structure:

```
assets/characters/
└── [character-id]/
    ├── base.png          (Required)
    ├── mouth_open.png    (Optional)
    └── eye_close.png     (Optional)
```

**Example for "Zundamon" character:**
```
assets/characters/zundamon/
├── base.png
├── mouth_open.png
└── eye_close.png
```

## Design Guidelines

### Character Style
- **Art Style**: Consistent with project branding
- **Line Art**: Clean, visible outlines recommended
- **Colors**: Vibrant, web-safe colors
- **Shading**: Soft shading recommended (avoid harsh shadows)

### Transparency Best Practices
- Clean alpha channel (no semi-transparent "fringe" pixels)
- Use "Remove White Matte" or similar before export
- Anti-aliased edges for smooth appearance

### Facial Features

**Eyes**:
- Clear, expressive eyes
- Visible pupils/highlights
- For `eye_close.png`: Natural closed position (relaxed eyelids)

**Mouth**:
- For `base.png`: Neutral closed mouth or slight smile
- For `mouth_open.png`: Natural "talking" position (not wide open)
- Avoid extreme expressions (shouting, laughing)

### Body/Clothing
- Avoid excessive detail that increases file size
- Ensure clothing/accessories don't obscure facial features
- Keep body position consistent across all variants

## Technical Specifications

### Export Settings (Photoshop)

```
File > Export > Export As...
Format: PNG
Transparency: ✓ Checked
Interlaced: ☐ Unchecked
Metadata: None
Color Space: sRGB
```

### Export Settings (GIMP)

```
File > Export As...
Format: PNG
Compression level: 9
Save background color: ☐ Unchecked
Save gamma: ☐ Unchecked
Interlacing: ☐ Unchecked
```

### Optimization (Optional)

After export, optimize file size with tools like:
- **PNGGauntlet** (Windows)
- **ImageOptim** (macOS)
- **pngquant** (CLI, all platforms)

Target: < 500KB per image without visible quality loss.

## Quality Checklist

Before delivery, verify each asset:

### Visual Quality
- [ ] Clean, sharp edges (no pixelation or blur)
- [ ] Transparent background (no white/colored fringe)
- [ ] Colors vibrant and consistent across variants
- [ ] No artifacts or compression noise
- [ ] Proper anti-aliasing on edges

### Alignment
- [ ] All images same canvas size
- [ ] Character position identical in all variants
- [ ] Only intended features differ (mouth/eyes)
- [ ] No "ghosting" when overlaid

### File Properties
- [ ] PNG format with alpha channel
- [ ] Square aspect ratio (e.g., 1024x1024px)
- [ ] File size < 500KB per image
- [ ] Filenames match specification exactly

### Animation Preview
- [ ] Test base.png + mouth_open.png toggling (lip sync preview)
- [ ] Test base.png + eye_close.png toggling (blink preview)
- [ ] Smooth transitions without "jumps" or misalignment

## Naming Conventions

### Character ID
Use lowercase with hyphens for character ID:
- ✅ `zundamon`
- ✅ `shikoku-metan`
- ❌ `Zundamon` (avoid uppercase)
- ❌ `zundamon_v2` (avoid version suffixes)

### Filenames
Use exact names (case-sensitive):
- ✅ `base.png`
- ✅ `mouth_open.png`
- ✅ `eye_close.png`
- ❌ `Base.PNG`
- ❌ `mouth-open.png`
- ❌ `eyes_closed.png`

## Examples

### Minimum Viable Asset (MVA)
For basic static display, provide only:
```
assets/characters/[id]/
└── base.png
```

### Full Animation Asset Set
For complete animation support:
```
assets/characters/[id]/
├── base.png          (idle state)
├── mouth_open.png    (speaking)
└── eye_close.png     (blinking)
```

## Common Mistakes to Avoid

### ❌ Misalignment
**Problem**: Character position shifts between variants.
**Solution**: Use layer-based workflow; duplicate base, modify only mouth/eyes.

### ❌ Inconsistent Canvas Size
**Problem**: Different image dimensions (e.g., 512x512 vs 1024x1024).
**Solution**: Set canvas size first, work on same-size artboards.

### ❌ Opaque Background
**Problem**: White or colored background instead of transparency.
**Solution**: Delete background layer before export, verify alpha channel.

### ❌ Extreme Expressions
**Problem**: Mouth too wide open, eyes tightly squeezed shut.
**Solution**: Use natural, subtle expressions for smooth animation.

### ❌ Over-detailed Art
**Problem**: File size exceeds 500KB due to excessive detail.
**Solution**: Simplify details, optimize PNG compression.

## Testing Your Assets

### Quick Visual Test
1. Open `base.png` and `mouth_open.png` in image viewer
2. Quickly alternate between images (keyboard arrows)
3. Should see only mouth changing, no "jump" or shift

### In-App Test
1. Place assets in `assets/characters/[character-id]/`
2. Configure in YAML (see below)
3. Generate test video with character enabled
4. Verify smooth lip sync and blinking

### Configuration Example

```yaml
personas:
  - id: "your-character-id"
    name: "Character Name"
    character_image: "assets/characters/your-character-id/base.png"
    character_position: "left"
    mouth_open_image: "assets/characters/your-character-id/mouth_open.png"
    eye_close_image: "assets/characters/your-character-id/eye_close.png"
    animation_style: "sway"
```

## Delivery Format

### File Delivery
Send assets as:
- ZIP archive containing folder structure above
- Or direct folder upload to project repository

### Naming Convention
Archive name: `character-assets-[character-id].zip`

Example: `character-assets-zundamon.zip`

### Contents
```
character-assets-zundamon.zip
└── assets/
    └── characters/
        └── zundamon/
            ├── base.png
            ├── mouth_open.png
            └── eye_close.png
```

## Support & Questions

For technical questions or clarification:
- **Project Repository**: [Insert GitHub URL]
- **Issue Tracker**: [Insert Issues URL]
- **Contact**: [Insert contact info]

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-01 | Initial release |
