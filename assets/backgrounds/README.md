# Background Assets

Background images and videos for video generation.

## Available Background Files

| File | Type | Size | Description | Use Case |
|------|------|------|-------------|----------|
| `default-background.mp4` | Video | ~23 MB | Default background video | General purpose, default setting |
| `abstract-loop.mp4` | Video | ~858 KB | Abstract looping animation | Modern, abstract content |
| `gradient-blue.jpg` | Image | ~512 KB | Blue gradient background | Simple, clean backgrounds |

## Usage

### In Configuration File

```yaml
video:
  background:
    type: "video"  # or "image"
    path: "assets/backgrounds/default-background.mp4"
    fit: "cover"  # cover, contain, or fill
```

### Background Types

#### Video Backgrounds
- **default-background.mp4**
  - General purpose background video
  - Default setting in `config/default.yaml`
  - Suitable for most content types

- **abstract-loop.mp4**
  - Lightweight looping abstract animation
  - Good for modern, tech-focused content
  - Smaller file size for faster rendering

#### Image Backgrounds
- **gradient-blue.jpg**
  - Simple blue gradient
  - Good for minimal, professional look
  - Fastest rendering (static image)

### Fit Options

| Fit | Description | When to Use |
|-----|-------------|-------------|
| `cover` | Fills entire frame, maintains aspect ratio (default) | Most cases - ensures no empty space |
| `contain` | Fits inside frame, maintains aspect ratio | When you want to see the entire background |
| `fill` | Stretches to fill frame | Not recommended (may distort) |

## Video Background Guidelines

### Performance
- **File size**: Keep under 50 MB for reasonable render times
- **Duration**: 30-60 seconds is ideal (will loop automatically)
- **Resolution**: 1920x1080 or higher recommended
- **Format**: MP4 (H.264) for best compatibility

### Visual Design
- **Subtle motion**: Background should not distract from content
- **Low contrast**: Avoid high-contrast patterns that compete with text/slides
- **Seamless loops**: Ensure video loops smoothly

## Adding Custom Backgrounds

### Adding a Video Background

1. Place your MP4 file in this directory
2. Update your config file:
   ```yaml
   video:
     background:
       type: "video"
       path: "assets/backgrounds/your-custom-video.mp4"
       fit: "cover"
   ```

### Adding an Image Background

1. Place your image file in this directory
2. Update your config file:
   ```yaml
   video:
     background:
       type: "image"
       path: "assets/backgrounds/your-custom-image.jpg"
       fit: "cover"
   ```

Supported formats:
- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp`
- **Videos**: `.mp4`, `.webm`, `.mov`

## Tips

- Use `fit: "cover"` for full-screen backgrounds (default)
- Test render a short clip to verify background appearance
- Consider using static images for faster rendering
- Keep background subtle to maintain focus on content
