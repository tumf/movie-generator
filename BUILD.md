# Build Instructions

## Quick Start

### 1. Download VOICEVOX Assets (Required for Docker builds)

```bash
./download-voicevox.sh
```

This downloads VOICEVOX binaries to `assets/voicevox/`.

### 2. Build Docker Images

```bash
cd web
docker compose build
```

## Local Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run CLI tool
uv run movie-generator generate <URL>

# Run tests
uv run pytest
```

## Docker Deployment

See [web/README.md](web/README.md) for full deployment instructions.
