# ==============================================================================
# ADCRA — Docker Container Definition
# Autonomous Digital Campaign & Creative Production System (Headless / Cloud Mode)
# ==============================================================================
FROM python:3.12-slim-bookworm

# Metadata
LABEL maintainer="ADCRA Systems <maintainers@adcra.io>"
LABEL description="Autonomous Digital Campaign & Creative Production System"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_VERSION=20.x \
    ADCRA_HOST=0.0.0.0 \
    ADCRA_PORT=8080 \
    DEFAULT_RENDER_ENGINE=headless

# Install system dependencies & multimedia tools (FFmpeg, Node.js, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    ffmpeg \
    libavcodec-extra \
    fonts-liberation \
    fonts-noto-color-emoji \
    procps \
    git \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_VERSION nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications first for caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY . .

# Ensure CLI wrapper is executable
RUN chmod +x bin/adcra adcra_cli.py dashboard_server.py

# Create persistent storage directories
RUN mkdir -p /app/campaign/memory /app/campaign/deliverables /app/campaign/reports

# Expose web dashboard port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Default entrypoint: launch Mission Control Dashboard Server
CMD ["python3", "dashboard_server.py", "--port", "8080", "--host", "0.0.0.0"]
