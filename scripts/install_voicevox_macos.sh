#!/bin/bash
# VOICEVOX Core installation script for macOS (Apple Silicon)
set -e

VOICEVOX_DIR="$HOME/.local/share/voicevox"
DICT_DIR="$VOICEVOX_DIR/dict"
MODEL_DIR="$VOICEVOX_DIR/models"

echo "🎙️  VOICEVOX Core Installation for macOS (Apple Silicon)"
echo "=================================================="
echo ""

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ] && [ "$ARCH" != "x86_64" ]; then
	echo "❌ Unsupported architecture: $ARCH"
	exit 1
fi

echo "Architecture: $ARCH"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p "$DICT_DIR"
mkdir -p "$MODEL_DIR"

# Step 1: Install VOICEVOX Core Python package
echo ""
echo "📦 Step 1: Installing VOICEVOX Core Python package..."
VOICEVOX_VERSION="0.16.3"

if [ "$ARCH" = "arm64" ]; then
	WHEEL_URL="https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_VERSION}/voicevox_core-${VOICEVOX_VERSION}-cp310-abi3-macosx_11_0_arm64.whl"
else
	WHEEL_URL="https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_VERSION}/voicevox_core-${VOICEVOX_VERSION}-cp310-abi3-macosx_10_12_x86_64.whl"
fi

echo "Downloading from: $WHEEL_URL"
uv pip install "$WHEEL_URL"
echo "✓ VOICEVOX Core installed"

# Step 2: Download the downloader
echo ""
echo "📥 Step 2: Downloading VOICEVOX downloader..."
DOWNLOADER_DIR="$VOICEVOX_DIR/bin"
mkdir -p "$DOWNLOADER_DIR"
cd "$DOWNLOADER_DIR"

if [ "$ARCH" = "arm64" ]; then
	DOWNLOADER_URL="https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_VERSION}/download-osx-arm64"
else
	DOWNLOADER_URL="https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_VERSION}/download-osx-x64"
fi

if [ ! -f "download" ]; then
	echo "Downloading downloader from: $DOWNLOADER_URL"
	curl -L -o download "$DOWNLOADER_URL"
	chmod +x download
	echo "✓ Downloader installed"
else
	echo "✓ Downloader already exists"
fi

# Step 3: Use downloader to get models and dictionary
echo ""
echo "📚🎤 Step 3: Downloading OpenJTalk Dictionary and Voice Models..."
echo ""
echo "The downloader will ask you to agree to the VOICEVOX license."
echo "Please review the license and type 'y' to agree."
echo ""
echo "Press Enter to continue..."
read

cd "$VOICEVOX_DIR"
./bin/download --only models dict --models-pattern '0.vvm' -o "$VOICEVOX_DIR"

if [ $? -eq 0 ]; then
	echo "✓ Dictionary and voice models downloaded"
else
	echo "❌ Failed to download models. Please check the error messages above."
	exit 1
fi

# Step 4: Create environment configuration
echo ""
echo "📝 Step 4: Creating configuration..."

CONFIG_FILE="$VOICEVOX_DIR/env.sh"
cat >"$CONFIG_FILE" <<EOF
# VOICEVOX Environment Variables
export VOICEVOX_DICT_DIR="$VOICEVOX_DIR/dict/open_jtalk_dic_utf_8-1.11"
export VOICEVOX_MODEL_PATH="$VOICEVOX_DIR/models/vvms/0.vvm"
export VOICEVOX_ONNXRUNTIME_PATH="$VOICEVOX_DIR/onnxruntime/lib/libvoicevox_onnxruntime.1.17.3.dylib"
EOF

echo "✓ Environment configuration created at: $CONFIG_FILE"

# Step 5: Update config/default.yaml
echo ""
echo "📝 Step 5: Updating project configuration..."

CONFIG_YAML="config/default.yaml"
if [ -f "$CONFIG_YAML" ]; then
	# Check if audio section exists
	if grep -q "^audio:" "$CONFIG_YAML"; then
		# Add paths if not already present
		if ! grep -q "dict_dir:" "$CONFIG_YAML"; then
			echo "  dict_dir: \"$VOICEVOX_DIR/dict\"" >>"$CONFIG_YAML"
		fi
		if ! grep -q "model_path:" "$CONFIG_YAML"; then
			echo "  model_path: \"$VOICEVOX_DIR/models/0.vvm\"" >>"$CONFIG_YAML"
		fi
		echo "✓ Updated config/default.yaml"
	else
		echo "⚠️  No 'audio:' section found in config/default.yaml"
		echo "   Please add manually:"
		echo "   audio:"
		echo "     dict_dir: \"$VOICEVOX_DIR/dict\""
		echo "     model_path: \"$VOICEVOX_DIR/models/0.vvm\""
	fi
else
	echo "⚠️  config/default.yaml not found, skipping config update"
fi

# Step 6: Test installation
echo ""
echo "🧪 Step 6: Testing installation..."
echo ""

# Source the env file
source "$CONFIG_FILE"

# Run Python test
python3 <<'PYTHON_TEST'
import sys
try:
    import voicevox_core
    print("✓ voicevox_core module imported successfully")
    print(f"  Version: {voicevox_core.__version__ if hasattr(voicevox_core, '__version__') else 'unknown'}")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Failed to import voicevox_core: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
	echo ""
	echo "=================================================="
	echo "✅ VOICEVOX Core installation completed!"
	echo "=================================================="
	echo ""
	echo "Next steps:"
	echo "  1. Add to your shell profile (~/.zshrc or ~/.bashrc):"
	echo "     echo 'source $CONFIG_FILE' >> ~/.zshrc"
	echo ""
	echo "  2. Or export environment variables for this session:"
	echo "     source $CONFIG_FILE"
	echo ""
	echo "  3. Download VOICEVOX ONNX Runtime (required):"
	echo "     cd $VOICEVOX_DIR"
	echo "     ./bin/download --only onnxruntime -o $VOICEVOX_DIR"
	echo "     (Accept license when prompted: q then y)"
	echo ""
	echo "  4. Test with:"
	echo "     source $CONFIG_FILE"
	echo "     uv run pytest tests/test_voicevox.py -v"
	echo ""
	echo "  5. Generate video:"
	echo "     uv run movie-generator generate <URL>"
	echo ""
else
	echo ""
	echo "❌ Installation verification failed"
	echo "Please check the error messages above"
	exit 1
fi
