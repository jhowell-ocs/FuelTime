#!/bin/bash

# FuelTime Dependency Verification Script
# Run this inside the container to verify all dependencies are properly installed

echo "🔍 FuelTime Dependency Verification"
echo "=================================="

# Check wkhtmltopdf
echo "1. Checking wkhtmltopdf..."
if command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "   ✓ wkhtmltopdf found"
    wkhtmltopdf --version | head -1 | sed 's/^/   /'
else
    echo "   ✗ wkhtmltopdf NOT found"
    exit 1
fi

# Check Xvfb (virtual display)
echo "2. Checking Xvfb..."
if command -v Xvfb >/dev/null 2>&1; then
    echo "   ✓ Xvfb found"
else
    echo "   ✗ Xvfb NOT found"
    exit 1
fi

# Start Xvfb if not running
echo "3. Starting virtual display..."
export DISPLAY=:99
if ! pgrep Xvfb > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    sleep 2
    echo "   ✓ Xvfb started on :99"
else
    echo "   ✓ Xvfb already running"
fi

# Check fonts
echo "4. Checking fonts..."
font_count=$(fc-list | wc -l)
if [ "$font_count" -gt 10 ]; then
    echo "   ✓ $font_count fonts available"
    echo "   Sample fonts:"
    fc-list | head -3 | sed 's/^/     /'
else
    echo "   ⚠ Only $font_count fonts found (may affect PDF quality)"
fi

# Test wkhtmltopdf functionality
echo "5. Testing PDF generation..."
test_html="<html><head><style>body{font-family:Arial;}</style></head><body><h1>Test PDF</h1><p>This is a test PDF with fonts and basic styling.</p></body></html>"
test_output="/tmp/test_wkhtmltopdf.pdf"

if echo "$test_html" | wkhtmltopdf --quiet --page-size Letter - "$test_output" 2>/dev/null; then
    if [ -f "$test_output" ] && [ -s "$test_output" ]; then
        file_size=$(stat -f%z "$test_output" 2>/dev/null || stat -c%s "$test_output" 2>/dev/null)
        echo "   ✓ PDF generation successful ($file_size bytes)"
        rm -f "$test_output"
    else
        echo "   ✗ PDF generation failed (empty file)"
        exit 1
    fi
else
    echo "   ✗ PDF generation failed"
    exit 1
fi

# Check required Python packages
echo "6. Checking Python packages..."
required_packages="flask pdfkit"
for package in $required_packages; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "   ✓ $package installed"
    else
        echo "   ✗ $package NOT installed"
        exit 1
    fi
done

# Check file permissions
echo "7. Checking file permissions..."
temp_dir="/app/temp"
if [ -d "$temp_dir" ]; then
    if [ -w "$temp_dir" ]; then
        echo "   ✓ $temp_dir is writable"
    else
        echo "   ✗ $temp_dir is NOT writable"
        exit 1
    fi
else
    echo "   ✗ $temp_dir does NOT exist"
    exit 1
fi

echo ""
echo "🎉 All dependencies verified successfully!"
echo "FuelTime should work properly for PDF generation."
