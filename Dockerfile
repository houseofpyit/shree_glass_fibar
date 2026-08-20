# Multi-stage build for production
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/uploads/images /app/uploads/pdfs /app/logs && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", \
    "--bind", "0.0.0.0:8000", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--workers", "2", \
    "--timeout", "120", \
    "--keep-alive", "5", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
