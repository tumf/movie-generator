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
# Also install Japanese fonts for proper text rendering
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
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fontconfig \
    ffmpeg \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Pre-install Remotion and download Chrome Headless Shell
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

# Install VOICEVOX Core Python package
WORKDIR /tmp
ARG VOICEVOX_CORE_VERSION=0.16.3
RUN pip install --no-cache-dir \
    https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_CORE_VERSION}/voicevox_core-${VOICEVOX_CORE_VERSION}-cp310-abi3-manylinux_2_34_x86_64.whl

# Set VOICEVOX environment variables
ENV VOICEVOX_DICT_DIR=/opt/voicevox/dict/open_jtalk_dic_utf_8-1.11
ENV VOICEVOX_MODEL_PATH=/opt/voicevox/models/vvms/0.vvm
ENV VOICEVOX_ONNXRUNTIME_PATH=/opt/voicevox/onnxruntime/lib/libvoicevox_onnxruntime.so.1.17.3
ENV LD_LIBRARY_PATH=/opt/voicevox/onnxruntime/lib:$LD_LIBRARY_PATH

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json pnpm-workspace.yaml /app/

# Install Remotion dependencies
RUN npm init -y \
    && npm install remotion@4.0.234 @remotion/cli@4.0.234 \
    && echo "Remotion dependencies installed"

# Copy movie-generator source code (assets are mounted at runtime)
COPY . /app/
RUN echo "Copied source code"

# Create directories for mounted assets
RUN mkdir -p /app/assets /app/backgrounds /app/bgm /app/characters

# VOICEVOX assets will be mounted at runtime
RUN mkdir -p /opt/voicevox

# Create cache directory and link Chrome from global cache
RUN mkdir -p /app/.cache/remotion \
    && ln -s /opt/remotion/chrome-headless-shell /app/.cache/remotion/chrome-headless-shell \
    && echo "Chrome linked to application cache directory"

# Install movie-generator with all dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Worker code is already included in the copy above
WORKDIR /app/web/worker

# Install worker-specific dependencies
RUN pip install --no-cache-dir httpx pydantic>=2.9.0

# Create data directory and symlink to assets
RUN mkdir -p /app/data/jobs \
    && ln -s /app/assets /app/data/assets \
    && echo "Created symlink from /app/data/assets to /app/assets"

# Set Python path
ENV PYTHONPATH=/app/src:/app/worker

# Run the worker
CMD ["python", "main.py"]
