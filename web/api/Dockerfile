# Dockerfile for FastAPI web service
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy API code
COPY . /app/api
WORKDIR /app/api

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir -p /app/data/jobs /app/api/static

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
