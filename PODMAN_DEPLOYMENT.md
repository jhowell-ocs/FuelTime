# FuelTime Podman/Docker Deployment Troubleshooting Guide

## 🔧 **CRITICAL DEPENDENCY FIXES (Updated)**

You were absolutely right! The previous version was missing essential `wkhtmltopdf` dependencies. This has now been **COMPLETELY FIXED** with:

### **New Dependencies Added:**
- **Display Server**: `xvfb` for headless PDF generation
- **Font Libraries**: `fontconfig`, `libfontconfig1`, `fonts-liberation`, `fonts-dejavu-core`
- **Graphics Libraries**: `libfreetype6`, `libjpeg62-turbo`, `libpng16-16`
- **X11 Libraries**: `libx11-6`, `libxcb1`, `libxext6`, `libxrender1`
- **SSL/Security**: `libssl3`, `ca-certificates`
- **System Tools**: `wget`, `curl` for health checks

### **Enhanced Container Features:**
- **Virtual Display**: Automatic Xvfb setup on container start
- **Font Cache**: Proper font initialization for PDF rendering
- **Comprehensive Testing**: Startup script tests all dependencies
- **Enhanced Debug**: `/debug/temp` endpoint tests actual PDF generation

## 🚀 **Deployment Options**

### Option 1: Use the New Podman-Optimized Compose File
```bash
# Use the new optimized compose file (with all dependencies)
podman-compose -f docker-compose.podman.yml up -d

# Or with Docker
docker-compose -f docker-compose.podman.yml up -d
```

### Option 2: Update Your Existing Deployment
```bash
# Rebuild with the fixes
podman-compose down
podman-compose build --no-cache
podman-compose up -d
```

### Option 3: Manual Volume Mount (if needed)
```bash
# Create a temp directory with proper permissions
mkdir -p ./temp
chmod 777 ./temp

# Run with explicit volume mount
podman run -d \
  --name fueltime-app \
  -p 5000:5000 \
  -v ./temp:/app/temp:Z \
  -e FLASK_ENV=production \
  your-fueltime-image
```

## 🔍 **Testing & Debugging**

### 1. Check Application Health
```bash
curl http://localhost:5000/debug/temp
```
This should return:
```json
{
  "temp_dir": "/app/temp",
  "exists": true,
  "writable": true,
  "files": [],
  "wkhtmltopdf_installed": true
}
```

### 2. Test PDF Generation
1. Go to `http://localhost:5000`
2. Fill out a fuel report or timesheet
3. Click "Generate PDF"
4. If it fails, check the debug endpoint above

### 3. Check Container Logs
```bash
# For Podman
podman logs fueltime-app

# For Docker
docker logs fueltime-app
```

Look for:
- ✓ Temp directory is writable
- ✓ wkhtmltopdf is available
- Any error messages during PDF generation

## 🐛 **Common Issues & Solutions**

### Issue: "File not found" errors
**Solution:** The temp directory isn't properly mounted or writable
```bash
# Check if volume is mounted correctly
podman inspect fueltime-app | grep -A5 -B5 "temp"

# Recreate with proper volume
podman-compose down
podman-compose up -d
```

### Issue: Permission denied errors
**Solution:** SELinux or permission issues
```bash
# If using SELinux, add :Z to volume mount
-v ./temp:/app/temp:Z

# Or disable SELinux temporarily for testing
sudo setenforce 0
```

### Issue: PDF generation fails
**Solution:** wkhtmltopdf not working in container
```bash
# Check if wkhtmltopdf is installed
podman exec fueltime-app wkhtmltopdf --version

# If missing, rebuild the container
podman-compose build --no-cache
```

## 📝 **File Structure After Fix**

New/Modified files:
- `docker-compose.podman.yml` - Optimized for Podman/Docker
- `startup.sh` - Container initialization script
- `app.py` - Fixed temp directory handling
- `Dockerfile` - Improved permissions and startup

## 🎯 **What Was Fixed**

1. **Hardcoded Paths** - Removed hardcoded `/app/temp` paths
2. **Permission Issues** - Added proper 777 permissions for temp directory
3. **Volume Mounting** - Created named volume for better reliability
4. **Error Handling** - Added detailed error messages and debugging
5. **Initialization** - Added startup script to ensure proper setup

The app should now work correctly in both local development and containerized environments!
