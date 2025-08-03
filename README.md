# FuelTime - Obion County Schools Forms Portal

A web-based application for fuel reporting and timesheet management with professional PDF generation.

## 🚀 Quick Deploy

### **Option 1: Deploy from GitHub (Recommended)**

Create a new directory and deploy directly from GitHub:

```bash
mkdir fueltime-app
cd fueltime-app
```

Create a `docker-compose.yml` file:

```yaml
services:
  fueltime:
    build:
      context: https://github.com/Obion-County-Board-of-Education/FuelTime.git
      dockerfile: Dockerfile
    container_name: fueltime-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
    volumes:
      - fueltime_temp:/app/temp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/debug/temp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  fueltime_temp:
    driver: local
```

Then start the application:
```bash
docker-compose up -d
```

### **Option 2: Local Development**

Clone and run locally:
```bash
git clone <your-repo-url>
cd FuelTime
docker-compose up -d
```

**Access the application at:** `http://localhost:5000`

## ✨ Features

- **Fuel Reports**: Monthly fuel consumption tracking with vehicle information
- **Timesheets**: Employee hours tracking with auto-fill calendar functionality
- **PDF Generation**: Professional PDF export for both forms
- **Digital Signatures**: Canvas-based signature support for timesheets
- **Responsive Design**: Works on desktop and mobile devices

## 🔧 Prerequisites

- Docker and Docker Compose
- Modern web browser

### Install Docker
- **Windows/Mac**: [Docker Desktop](https://docs.docker.com/get-docker/)
- **Linux**: `sudo apt install docker.io docker-compose` (Ubuntu) or equivalent

## 🐳 Management Commands

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start application |
| `docker-compose down` | Stop application |
| `docker-compose logs -f` | View logs |
| `docker-compose ps` | Check container status |
| `docker-compose restart` | Restart application |

## 🔍 Quick Status Check

```bash
# Check if container is running
docker-compose ps

# Check application health
curl http://localhost:5000/debug/temp

# View recent logs
docker-compose logs --tail=50 fueltime
```

## � Key Files

```
FuelTime/
├── app.py                        # Main Flask application
├── templates/                    # HTML templates
├── static/logo.png              # Application logo  
├── docker-compose.yml           # Docker configuration
├── Dockerfile                   # Container definition
└── requirements.txt             # Python dependencies
```

## 🚨 Troubleshooting

**"Failed to fetch" error when generating PDFs:**
1. **Check if application is running**: `docker-compose ps`
   - Should show `fueltime-app` as `Up`
2. **Test application connectivity**: `curl http://localhost:5000`
   - Should return the web page HTML
3. **Check container logs**: `docker-compose logs fueltime`
   - Look for startup errors or wkhtmltopdf issues
4. **Restart if needed**: `docker-compose restart`

**Application won't start:**
- Ensure Docker is running
- Check port 5000 isn't in use: `docker-compose up -d --force-recreate`
- View logs: `docker-compose logs -f`

**PDF generation issues:**
- Restart: `docker-compose restart`
- Check health: `curl http://localhost:5000/debug/temp`
- Test wkhtmltopdf: `docker-compose exec fueltime ./test-wkhtmltopdf.sh`

**wkhtmltopdf Compatibility:**
This application uses the patched version of wkhtmltopdf for full functionality. If you see errors about unsupported switches, the container will automatically download and install the correct version.

## 📞 Support

**Obion County Schools IT Department**  
Email: jhowell@ocboe.com

For issues, include output from `docker-compose logs` and steps to reproduce.

## 📜 License

Proprietary software of Obion County Schools.
