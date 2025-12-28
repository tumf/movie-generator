# VOICEVOX Setup Guide

This guide explains how to set up VOICEVOX Core for audio synthesis.

## Prerequisites

1. **VOICEVOX Core**: Python bindings for VOICEVOX
2. **OpenJTalk Dictionary**: Required for Japanese text processing
3. **Voice Model Files**: VOICEVOX speaker models (.vvm files)

## Quick Start (macOS)

For macOS users, use the automated installation script:

```bash
bash scripts/install_voicevox_macos.sh
```

This script will:
1. Download and install VOICEVOX Core Python package (version 0.16.3)
2. Download the VOICEVOX downloader tool
3. Guide you through downloading the OpenJTalk dictionary and voice models

**Note**: You will be asked to agree to the VOICEVOX license during installation. Please review the license terms and type 'y' to accept.

After installation, set the environment variables:

```bash
# Add to your ~/.zshrc or ~/.bashrc
source ~/.local/share/voicevox/env.sh

# Or set manually for the current session
export VOICEVOX_DICT_DIR="$HOME/.local/share/voicevox/dict"
export VOICEVOX_MODEL_PATH="$HOME/.local/share/voicevox/models/0.vvm"
```

## Manual Installation

### 1. Install VOICEVOX Core

VOICEVOX Core is not available via pip. You need to build or download it manually:

```bash
# Option A: Download pre-built wheels (if available)
# Check https://github.com/VOICEVOX/voicevox_core/releases

# Option B: Build from source
git clone https://github.com/VOICEVOX/voicevox_core.git
cd voicevox_core
# Follow build instructions in the repository
```

### 2. Download OpenJTalk Dictionary

```bash
# Download and extract OpenJTalk dictionary
wget https://github.com/r9y9/open_jtalk/releases/download/v1.11/open_jtalk_dic_utf_8-1.11.tar.gz
tar xzf open_jtalk_dic_utf_8-1.11.tar.gz
mv open_jtalk_dic_utf_8-1.11 ~/.local/share/voicevox/dict/
```

### 3. Download Voice Models

Download VOICEVOX voice models from the official releases:

```bash
# Create directory for models
mkdir -p ~/.local/share/voicevox/models

# Download models (example for Zundamon - speaker ID 3)
# Visit https://github.com/VOICEVOX/voicevox_core/releases
# Download the .vvm files you need
```

### 4. Download ONNX Runtime

```bash
# macOS (ARM64)
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.3/onnxruntime-osx-arm64-1.16.3.tgz
tar xzf onnxruntime-osx-arm64-1.16.3.tgz
mv onnxruntime-osx-arm64-1.16.3/lib/libonnxruntime.dylib ~/.local/share/voicevox/

# Linux
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.3/onnxruntime-linux-x64-1.16.3.tgz
# Extract and move .so file

# Windows
# Download and extract .dll file
```

## Configuration

Update your `config.yaml` with the paths to VOICEVOX files:

```yaml
audio:
  engine: "voicevox"
  speaker_id: 3  # Zundamon
  speed_scale: 1.0
  
  # Paths (can also be set via environment variables)
  dict_dir: "~/.local/share/voicevox/dict/open_jtalk_dic_utf_8-1.11"
  model_path: "~/.local/share/voicevox/models/0.vvm"
  onnxruntime_path: "~/.local/share/voicevox/libonnxruntime.dylib"
```

Alternatively, set environment variables:

```bash
export VOICEVOX_DICT_DIR="$HOME/.local/share/voicevox/dict/open_jtalk_dic_utf_8-1.11"
export VOICEVOX_MODEL_PATH="$HOME/.local/share/voicevox/models/0.vvm"
export VOICEVOX_ONNXRUNTIME_PATH="$HOME/.local/share/voicevox/libonnxruntime.dylib"
```

## Pronunciation Dictionary

VOICEVOX supports user dictionaries for correct pronunciation of proper nouns:

```yaml
pronunciation:
  custom:
    "GitHub":
      reading: "ギットハブ"
      accent: 4           # Accent position (0=auto)
      word_type: "PROPER_NOUN"  # PROPER_NOUN, COMMON_NOUN, VERB, ADJECTIVE, SUFFIX
      priority: 10        # Priority (1-10, higher = more priority)
    
    "Ratatui":
      reading: "ラタトゥイ"
      accent: 4
      word_type: "PROPER_NOUN"
      priority: 10
    
    # Simple format (uses defaults)
    "人月": "ニンゲツ"
```

### How It Works

1. **Dictionary Entries**: Define pronunciation for words that VOICEVOX might misread
2. **OpenJTalk Integration**: Entries are added to OpenJTalk's morphological analyzer
3. **Proper Parsing**: VOICEVOX correctly parses and accents the words
4. **No Text Replacement**: Original text is preserved in subtitles

### Accent Position

- `0`: Auto-detect accent (recommended for most cases)
- `1-N`: Accent position (mora count from start)
- Example: "ギットハブ" (4 morae) with accent=4 means accent on "ブ"

## Testing

Test your VOICEVOX setup:

```bash
# Run tests
uv run pytest tests/test_voicevox.py -v

# Test real synthesis (if VOICEVOX is properly installed)
uv run python -c "
from movie_generator.audio.voicevox import VOICEVOX_AVAILABLE
print(f'VOICEVOX available: {VOICEVOX_AVAILABLE}')
"
```

## Troubleshooting

### Import Error

```
ImportError: voicevox_core is not installed
```

**Solution**: VOICEVOX Core needs to be installed manually. See installation steps above.

### File Not Found

```
FileNotFoundError: OpenJTalk dictionary not found
```

**Solution**: Ensure paths in config are correct and files exist.

### Library Load Error (macOS)

```
OSError: cannot load library 'libonnxruntime.dylib'
```

**Solution**: 
```bash
# Allow unsigned library
xattr -d com.apple.quarantine ~/.local/share/voicevox/libonnxruntime.dylib
```

## Running Without VOICEVOX

### Default Behavior (Recommended)

By default, the synthesizer **requires VOICEVOX Core** to be installed:

```python
from movie_generator.audio.voicevox import VoicevoxSynthesizer

# This will raise ImportError if voicevox_core is not installed
synth = VoicevoxSynthesizer()  # ❌ Fails without VOICEVOX
```

**Error message:**
```
ImportError: VOICEVOX Core is not installed and is required for audio synthesis.
Please install voicevox_core or see docs/VOICEVOX_SETUP.md for instructions.
To run without VOICEVOX (placeholder mode for testing), set allow_placeholder=True.
```

### Placeholder Mode (Testing Only)

For development/testing without VOICEVOX, explicitly enable placeholder mode:

```python
# Allow running without VOICEVOX
synth = VoicevoxSynthesizer(allow_placeholder=True)  # ✅ OK
```

**Placeholder mode behavior:**
- Audio files will be empty placeholders (0 bytes)
- Duration estimates based on text length (~150ms per character)
- **No actual audio is generated**
- Useful for testing pipeline structure without VOICEVOX

**⚠️ Warning:** Placeholder mode is only for development/testing. Production use requires real VOICEVOX installation.

## References

- [VOICEVOX Core](https://github.com/VOICEVOX/voicevox_core)
- [OpenJTalk](https://github.com/r9y9/open_jtalk)
- [ONNX Runtime](https://github.com/microsoft/onnxruntime)
