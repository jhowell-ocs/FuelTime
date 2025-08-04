FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
    libgconf-2-4 \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf using a more reliable method
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/temp /app/static && \
    chmod -R 777 /app/temp && \
    chmod -R 755 /app/static && \
    chmod -R 755 /app

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

# Start Xvfb and the application in one command
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & sleep 2 && exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"]
