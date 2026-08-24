FROM python:3.11-slim

# Set environment variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disc
# - PYTHONUNBUFFERED: Ensures standard output and error are sent straight to terminal (Coolify logs)
# - PIP_NO_CACHE_DIR: Disables pip caching to minimize image size
# - QP_DATA_DIR: Sets default unified storage directory for databases, uploads, exports, and config
# - PORT: Default application listening port
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    QP_DATA_DIR=/app/data \
    PORT=8888

WORKDIR /app

# Create a dedicated non-root system group and user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -d /home/appuser -m appuser

# Copy dependency requirements first to leverage Docker layer caching
COPY app/requirements.txt /app/app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r /app/app/requirements.txt

# Copy the rest of the application codebase
COPY . /app

# Ensure persistent data directories exist and set non-root ownership
RUN mkdir -p /app/data/tenants /app/data/uploads /app/data/exports && \
    chown -R appuser:appgroup /app /home/appuser

# Switch to non-root user for security
USER appuser

# Expose internal application port
EXPOSE 8888

# Built-in container health check using Python standard library
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8888\")}/health')" || exit 1

# Start the application using Python (NiceGUI runs production Uvicorn ASGI server with signal handling)
CMD ["python", "app/main.py"]
