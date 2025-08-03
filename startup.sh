#!/bin/bash

# Startup script for FuelTime container
echo "Starting FuelTime application..."

# Set up virtual display for wkhtmltopdf (headless environment)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait a moment for Xvfb to start
sleep 2

# Ensure temp directory exists with proper permissions
mkdir -p /app/temp
chmod 777 /app/temp

# Test temp directory write permissions
if touch /app/temp/test_write 2>/dev/null; then
    rm -f /app/temp/test_write
    echo "✓ Temp directory is writable"
else
    echo "✗ Warning: Temp directory is not writable"
fi

# Test wkhtmltopdf installation
if command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "✓ wkhtmltopdf is available"
    wkhtmltopdf --version | head -1
    
    # Test wkhtmltopdf with a simple HTML string
    echo "<html><body><h1>Test</h1></body></html>" | wkhtmltopdf - /tmp/test.pdf 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ wkhtmltopdf can generate PDFs"
        rm -f /tmp/test.pdf
    else
        echo "✗ Warning: wkhtmltopdf test failed"
    fi
else
    echo "✗ Warning: wkhtmltopdf not found"
fi

# Test font availability
fc-list | head -5
echo "✓ Font cache initialized"

# Start the application
echo "Starting Gunicorn server..."
exec "$@"
