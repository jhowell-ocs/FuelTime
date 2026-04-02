FROM python:3.11-slim

# Install system dependencies and apply all available security patches
# Security: apt-get upgrade ensures latest OS-level CVE fixes (OpenSSL, libpng, gnutls, etc.)
# Security: Using --no-install-recommends to minimize attack surface (fixes DS-0029)
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    xvfb \
    curl \
    wget \
    fontconfig \
    libfontconfig1 \
    libfreetype6 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libssl3 \
    libjpeg62-turbo \
    libpng16-16 \
    libxss1 \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from official source
# Security: Using --no-install-recommends to minimize attack surface (fixes DS-0029)
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Security: Create non-root user and group (fixes DS-0002 - container running as root)
# Using UID/GID 1000 for compatibility with common host user IDs
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app --shell=/bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade pip wheel

# Copy application files
COPY . .

# Security: Create necessary directories with proper ownership for non-root user
# /app/temp needs write access for PDF generation
# Setting appuser as owner ensures principle of least privilege
RUN mkdir -p /app/temp /app/static && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/temp

# Set environment variables for headless operation
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Expose port
EXPOSE 5000

# Add comprehensive health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/debug/temp || exit 1

# Security: Switch to non-root user before starting application (fixes DS-0002)
# This ensures the application runs with minimal privileges, reducing container escape risk
USER appuser

# Start Xvfb and the application in one command
# Note: Xvfb can run as non-root with -ac flag (access control disabled)
# Display :99 is available to non-root users in modern X11 implementations
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & sleep 2 && exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"]
