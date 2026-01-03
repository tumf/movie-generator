# BGM Assets

Background music files for video generation.

## Available BGM Files

| File | Description | Duration | Mood | Use Case |
|------|-------------|----------|------|----------|
| `default-bgm.mp3` | やさしい解説ループ | ~4.0 MB | Gentle, soft | Default BGM for most videos |
| `high-tempo.mp3` | ループする解説ハイテンポ | ~5.5 MB | Energetic, upbeat | Tech reviews, exciting content |
| `calm-ambient.mp3` | Calm ambient music | ~4.5 MB | Calm, ambient | Relaxing, educational content |

## Usage

### In Configuration File

```yaml
video:
  bgm:
    path: "assets/bgm/default-bgm.mp3"  # Or high-tempo.mp3, calm-ambient.mp3
    volume: 0.3  # 0.0-1.0 (default: 0.3)
    fade_in_seconds: 2.0
    fade_out_seconds: 2.0
    loop: true
```

### Choosing the Right BGM

- **default-bgm.mp3** (やさしい解説ループ)
  - General purpose, gentle mood
  - Good for tutorials, explanations, and educational content
  - Default setting in `config/default.yaml`

- **high-tempo.mp3** (ループする解説ハイテンポ)
  - Energetic, fast-paced mood
  - Best for tech reviews, product announcements, exciting news
  - Use when you want to create an upbeat atmosphere

- **calm-ambient.mp3**
  - Calm, relaxing mood
  - Best for meditative content, documentation walkthroughs
  - Use when you want to maintain a peaceful atmosphere

## Volume Guidelines

| Volume | Description | Recommended Use |
|--------|-------------|-----------------|
| 0.1-0.2 | Very quiet | Background presence only |
| 0.3 | Default | Balanced with narration (recommended) |
| 0.4-0.5 | Moderate | When BGM is part of the content |
| 0.6+ | Loud | Not recommended (overpowers narration) |

## Adding Custom BGM

1. Place your MP3/WAV file in this directory
2. Update your config file to reference it:
   ```yaml
   video:
     bgm:
       path: "assets/bgm/your-custom-bgm.mp3"
   ```

Supported formats: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac`
