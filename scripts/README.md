# Scripts

Utility scripts for the Movie Generator project.

## generate_zundamon_assets.py

Generate character animation assets from Zundamon PSD file.

### Prerequisites

- Zundamon PSD file placed at `assets/ずんだもん立ち絵素材2.3.psd`
- Download from: [坂本アヒル - Zundamon Tachie Material](https://seiga.nicovideo.jp/seiga/im10788496)

### Usage

```bash
uv run python scripts/generate_zundamon_assets.py
```

### Output

Creates three PNG files in `assets/characters/zundamon/`:

- `base.png` - Neutral expression (mouth closed, eyes open)
- `mouth_open.png` - Speaking expression (mouth open)
- `eye_close.png` - Blinking expression (eyes closed)

All images are 1024x1024px PNG format, optimized for character animation.

### Layer Configuration

The script automatically configures PSD layers:

| Asset | Mouth Layer | Eye Layer | Eyebrow Layer |
|-------|-------------|-----------|---------------|
| `base.png` | *ほあー | *普通目 | *普通眉 |
| `mouth_open.png` | *お | *普通目 | *普通眉 |
| `eye_close.png` | *ほあー | *にっこり | *普通眉 |

### Customization

To use different expressions, edit the layer names in `generate_zundamon_assets.py`:

```python
# Example: Change mouth open expression
# Find this line in generate_mouth_open_image():
if layer.name == '*お':  # Change to other mouth layer
    layer.visible = True
```

Available mouth layers:
- `*ほあー`, `*ほあ`, `*ほー`, `*むふ`, `*△`, `*んあー`, `*んへー`, `*んー`, `*はへえ`, `*おほお`, `*お`, `*ゆ`, `*むー`

Available eye layers:
- `*普通目`, `*にっこり`, `*細め目`, `*ジト目`, `*なごみ目`, `*><`, `*UU`, `*〇〇`, `*ぐるぐる`

## inspect_psd.py

Inspect PSD file layer structure.

### Usage

```bash
uv run python scripts/inspect_psd.py
```

### Output

Prints layer tree structure with visibility indicators:
- 👁️ = Visible layer
- 🔒 = Hidden layer

Useful for understanding PSD organization before customizing generation script.
