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

## generate_metan_assets.py

Generate character animation assets from Shikoku Metan PSD file.

### Prerequisites

- Shikoku Metan PSD file placed at `assets/四国めたん立ち絵素材2.1.psd`
- Download from: [坂本アヒル - Shikoku Metan Tachie Material](https://seiga.nicovideo.jp/seiga/im10806233)

### Usage

```bash
uv run python scripts/generate_metan_assets.py
```

### Output

Creates three PNG files in `assets/characters/shikoku-metan/`:

- `base.png` - Neutral expression (mouth closed, eyes open)
- `mouth_open.png` - Speaking expression (mouth open)
- `eye_close.png` - Blinking expression (eyes closed)

All images are 1024x1024px PNG format, optimized for character animation.

### Layer Configuration

The script automatically configures PSD layers:

| Asset | Mouth Layer | Eye Layer |
|-------|-------------|-----------|
| `base.png` | *ほほえみ | *目セット > *カメラ目線 |
| `mouth_open.png` | *わあー | *目セット > *カメラ目線 |
| `eye_close.png` | *ほほえみ | *目閉じ |

### Customization

To use different expressions, edit the layer paths in `generate_metan_assets.py`:

```python
# Example: Change mouth open expression
set_layer_visibility(psd, ["!口", "*わあー"], True)
# Change "*わあー" to another mouth layer name
```

Available mouth layers:
- `*ほほえみ`, `*▽`, `*にやり`, `*ぺろり`, `*お`, `*ゆ`, `*△`, `*む`, `*いー`, `*うえー`, `*んー`, `*もむー`

Available eye layers:
- `*目セット > *カメラ目線`, `*見上げ`, `*見上げ2`, `*目閉じ`, `*目閉じ2`, `*○○`, `*><`, `*ぐるぐる`

## generate_tsumugi_assets.py

Generate character animation assets from Kasukabe Tsumugi PSD file.

### Prerequisites

- Kasukabe Tsumugi PSD file placed at `assets/春日部つむぎ立ち絵素材.psd`
- Download from: [坂本アヒル - Kasukabe Tsumugi Tachie Material](https://seiga.nicovideo.jp/seiga/im10788235)

### Usage

```bash
uv run python scripts/generate_tsumugi_assets.py
```

### Output

Creates three PNG files in `assets/characters/kasukabe-tsumugi/`:

- `base.png` - Neutral expression (mouth closed, eyes open)
- `mouth_open.png` - Speaking expression (mouth open)
- `eye_close.png` - Blinking expression (eyes closed)

All images are 1082x1820px PNG format, optimized for character animation.

### Layer Configuration

The script automatically configures PSD layers:

| Asset | Mouth Layer | Eye Layer |
|-------|-------------|-----------|
| `base.png` | *ほほえみ | *基本目セット > *基本 |
| `mouth_open.png` | *わあ | *基本目セット > *基本 |
| `eye_close.png` | *ほほえみ | *閉じ |

### Customization

To use different expressions, edit the layer paths in `generate_tsumugi_assets.py`:

```python
# Example: Change mouth open expression
set_layer_visibility(psd, ["!口", "*わあ"], True)
# Change "*わあ" to another mouth layer name
```

Available mouth layers:
- `*ほほえみ`, `*わあーい`, `*む`, `*お`, `*おあー`, `*むん`, `*えあー`, `*いー`, `*にしー`

Available eye layers:
- `*基本目セット > *基本`, `*上向き`, `*上向き2`, `*閉じ`, `*にっこり`, `*><`, `*〇〇`

## inspect_psd.py

Inspect PSD file layer structure.

### Usage

```bash
uv run python scripts/inspect_psd.py <path-to-psd-file>
```

### Example

```bash
# Inspect Zundamon PSD
uv run python scripts/inspect_psd.py assets/ずんだもん立ち絵素材2.3.psd

# Inspect Shikoku Metan PSD
uv run python scripts/inspect_psd.py assets/四国めたん立ち絵素材2.1.psd

# Inspect Kasukabe Tsumugi PSD
uv run python scripts/inspect_psd.py assets/春日部つむぎ立ち絵素材.psd
```

### Output

Prints layer tree structure with visibility indicators:
- 👁️ = Visible layer
- 🔒 = Hidden layer

Useful for understanding PSD organization before customizing generation script.
