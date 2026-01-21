# Dockerfile for worker service
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for Remotion)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm (required for Remotion)
RUN npm install -g pnpm@9

# Install Chrome dependencies for Remotion rendering
# These are required for Chrome Headless Shell to run properly
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Pre-install Remotion and download Chrome Headless Shell
# This prevents "Chrome not found" errors during video rendering
# Chrome is cached at /opt/remotion/chrome-headless-shell for reuse
WORKDIR /tmp/remotion-setup
RUN npm init -y \
    && npm install remotion@4.0.234 @remotion/cli@4.0.234 \
    && npx remotion browser ensure \
    && echo "Chrome Headless Shell installed successfully" \
    && mkdir -p /opt/remotion \
    && mv node_modules/.remotion/chrome-headless-shell /opt/remotion/ \
    && echo "Chrome cached at /opt/remotion/chrome-headless-shell" \
    && cd / \
    && rm -rf /tmp/remotion-setup

# Install VOICEVOX Core and dependencies using official downloader
WORKDIR /tmp
ARG VOICEVOX_CORE_VERSION=0.16.3

# Install VOICEVOX Core Python package
RUN pip install --no-cache-dir \
    https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_CORE_VERSION}/voicevox_core-${VOICEVOX_CORE_VERSION}-cp310-abi3-manylinux_2_34_x86_64.whl

# Download VOICEVOX core, onnxruntime, dict, and models using downloader
RUN mkdir -p /opt/voicevox \
    && wget -q -O /tmp/download-linux-x64 https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_CORE_VERSION}/download-linux-x64 \
    && chmod +x /tmp/download-linux-x64 \
    && cd /opt/voicevox \
    && yes | /tmp/download-linux-x64 --output . --devices cpu --exclude c-api \
    && rm -f /tmp/download-linux-x64 \
    && echo "Verifying VOICEVOX installation..." \
    && test -d /opt/voicevox/dict || (echo "ERROR: dict not found" && exit 1) \
    && test -d /opt/voicevox/onnxruntime || (echo "ERROR: onnxruntime not found" && exit 1) \
    && test -d /opt/voicevox/models || (echo "ERROR: models not found" && exit 1) \
    && echo "VOICEVOX installation verified successfully" \
    && ls -la /opt/voicevox/

# Set VOICEVOX environment variables
ENV VOICEVOX_DICT_DIR=/opt/voicevox/dict/open_jtalk_dic_utf_8-1.11
ENV VOICEVOX_MODEL_PATH=/opt/voicevox/models/vvms/0.vvm
ENV VOICEVOX_ONNXRUNTIME_PATH=/opt/voicevox/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3
ENV LD_LIBRARY_PATH=/opt/voicevox/onnxruntime/lib:$LD_LIBRARY_PATH

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json pnpm-workspace.yaml /app/

# Pre-install shared Remotion dependencies in workspace
# This prevents re-downloading dependencies for each project
RUN pnpm install --frozen-lockfile=false \
    && echo "Workspace dependencies installed" \
    && du -sh node_modules

# Copy movie-generator source code from parent directory
COPY . /app/
WORKDIR /app

# Create cache directory and link Chrome from global cache
# This allows the application to find Chrome without re-downloading
RUN mkdir -p /app/.cache/remotion \
    && ln -s /opt/remotion/chrome-headless-shell /app/.cache/remotion/chrome-headless-shell \
    && echo "Chrome linked to application cache directory"

# Install movie-generator with all dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Worker code is already included in the copy above
WORKDIR /app/web/worker

# Install worker-specific dependencies
RUN pip install --no-cache-dir httpx pydantic>=2.9.0

# Create data directory
RUN mkdir -p /app/data/jobs

# Set Python path
ENV PYTHONPATH=/app/src:/app/worker

# Run the worker
CMD ["python", "main.py"]
