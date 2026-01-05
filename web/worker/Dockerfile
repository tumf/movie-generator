# Dockerfile for worker service
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for Remotion)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy movie-generator source code
COPY ../.. /app/
WORKDIR /app

# Install movie-generator with all dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy worker code
COPY worker /app/worker
WORKDIR /app/worker

# Install worker dependencies
RUN pip install --no-cache-dir httpx

# Create data directory
RUN mkdir -p /app/data/jobs

# Set Python path
ENV PYTHONPATH=/app/src:/app/worker

# Run the worker
CMD ["python", "main.py"]
