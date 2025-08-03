#!/bin/bash
# Test script to verify wkhtmltopdf installation and functionality

echo "🔍 Testing wkhtmltopdf installation..."

# Test 1: Check if wkhtmltopdf is installed
if command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "✓ wkhtmltopdf found"
    wkhtmltopdf --version
else
    echo "✗ wkhtmltopdf not found"
    exit 1
fi

# Test 2: Check if it's the patched version
echo -e "\n🔍 Checking if wkhtmltopdf is patched..."
if wkhtmltopdf --version 2>&1 | grep -q "with patched qt"; then
    echo "✓ Using patched wkhtmltopdf (full functionality)"
else
    echo "⚠ Using unpatched wkhtmltopdf (limited functionality)"
fi

# Test 3: Simple PDF generation test
echo -e "\n🔍 Testing PDF generation..."
test_html="<html><head><title>Test</title></head><body><h1>Test PDF</h1><p>This is a test document.</p></body></html>"
test_output="/tmp/test_wkhtmltopdf.pdf"

# Start Xvfb if in container environment
if [ -d "/app" ] && [ -z "$DISPLAY" ]; then
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &
    sleep 2
    echo "✓ Started Xvfb for headless operation"
fi

# Test with minimal options
if echo "$test_html" | wkhtmltopdf --quiet --page-size Letter - "$test_output" 2>/dev/null; then
    if [ -f "$test_output" ] && [ -s "$test_output" ]; then
        file_size=$(stat -f%z "$test_output" 2>/dev/null || stat -c%s "$test_output" 2>/dev/null)
        echo "✓ PDF generation successful ($file_size bytes)"
        rm -f "$test_output"
    else
        echo "✗ PDF generation failed (empty file)"
        exit 1
    fi
else
    echo "✗ PDF generation failed"
    exit 1
fi

echo -e "\n🎉 All tests passed! wkhtmltopdf is working correctly."
