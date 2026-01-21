#!/bin/bash
# Download VOICEVOX assets for Docker build using gh CLI
# Run this script before building Docker images

set -e

VOICEVOX_VERSION="0.16.3"
VOICEVOX_DIR="assets/voicevox"
REPO="VOICEVOX/voicevox_core"
DOWNLOADER="/tmp/download-linux-x64"

echo "Downloading VOICEVOX ${VOICEVOX_VERSION} using gh CLI..."
echo "This may take a few minutes..."

mkdir -p "${VOICEVOX_DIR}"

# Download VOICEVOX downloader using gh CLI with explicit tag
echo "Step 1: Downloading VOICEVOX downloader..."
gh release download "${VOICEVOX_VERSION}" --repo "${REPO}" --pattern "download-linux-x64" --dir /tmp --clobber || {
    echo "gh download failed, trying curl fallback..."
    curl -fsSL -o "${DOWNLOADER}" \
        "https://github.com/${REPO}/releases/download/${VOICEVOX_VERSION}/download-linux-x64"
}

chmod +x "${DOWNLOADER}"

# Download VOICEVOX assets
echo "Step 2: Fetching VOICEVOX assets (dict, onnxruntime, models)..."
cd "${VOICEVOX_DIR}"

if ! "${DOWNLOADER}" --output . --devices cpu --exclude c-api 2>/dev/null; then
    echo "ERROR: VOICEVOX assets download failed (likely GitHub API rate limit)"
    echo ""
    echo "Solutions:"
    echo "1. Wait ~1 hour for rate limit to reset, then run again"
    echo "2. Or authenticate with gh CLI:"
    echo "   gh auth login"
    echo "   gh auth refresh"
    echo "   ./download-voicevox.sh"
    exit 1
fi

# Cleanup
rm -f "${DOWNLOADER}"

# Verify installation
echo "Verifying VOICEVOX installation..."
if [ ! -d "${VOICEVOX_DIR}/dict" ]; then
    echo "ERROR: dict not found"
    exit 1
fi
if [ ! -d "${VOICEVOX_DIR}/onnxruntime" ]; then
    echo "ERROR: onnxruntime not found"
    exit 1
fi
if [ ! -d "${VOICEVOX_DIR}/models" ]; then
    echo "ERROR: models not found"
    exit 1
fi

echo ""
echo "✓ VOICEVOX assets downloaded successfully to ${VOICEVOX_DIR}"
ls -lh "${VOICEVOX_DIR}"
