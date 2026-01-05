# Dockerfile for FastAPI web service
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project (context is set to project root in compose)
COPY . /app/
WORKDIR /app/web/api

# Install Python dependencies directly (not as editable package)
COPY web/api/pyproject.toml /tmp/
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    jinja2>=3.1.4 \
    python-multipart>=0.0.12 \
    httpx>=0.27.0 \
    slowapi>=0.1.9 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.6.0

# Create directories
RUN mkdir -p /app/data/jobs /app/web/api/static

# Set Python path to include the api directory
ENV PYTHONPATH=/app/web/api:$PYTHONPATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
