<div align="center">
  <img src="static/logo.png" alt="Obion County Schools" width="400">
  
  # FuelTime
  
  **Professional Forms Portal for Obion County Schools**
  
  [![CI/CD Pipeline](https://github.com/jhowell-ocs/FuelTime/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/jhowell-ocs/FuelTime/actions/workflows/ci-cd.yml)
  [![Security Scan](https://img.shields.io/badge/security-scanned-brightgreen)](https://github.com/jhowell-ocs/FuelTime/security)
  [![License](https://img.shields.io/github/license/jhowell-ocs/FuelTime)](LICENSE)
  
  A web-based application for fuel reporting and timesheet management with professional PDF generation.
</div>

---

## Overview

FuelTime provides a streamlined digital solution for managing two essential administrative forms:

- **Fuel Reports**: Monthly fuel consumption tracking with vehicle information
- **Employee Timesheets**: Hours tracking with automatic calendar functionality and total calculations

Both forms feature professional PDF generation for official documentation and record-keeping.

### 🔒 Security & Quality

- Automated security scanning with Bandit, Safety, and Trivy
- Code quality checks with Pylint, Flake8, and Black
- Continuous integration and deployment via GitHub Actions
- Container vulnerability scanning
- Regular dependency updates

## Deployment

### Quick Start with GitHub Container Registry

```bash
# Pull and run the latest version
docker pull ghcr.io/jhowell-ocs/fueltime:latest
docker run -d -p 5000:5000 \
  -v fueltime_temp:/app/temp \
  ghcr.io/jhowell-ocs/fueltime:latest
```

### Using Docker Compose (Recommended)

1. **Create `docker-compose.yml`:**
   ```yaml
   services:
     fueltime:
       image: ghcr.io/jhowell-ocs/fueltime:latest
       # Or build from source:
       # build:
       #   context: https://github.com/jhowell-ocs/FuelTime.git
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

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser to `http://localhost:5000`

### Management Commands

```bash
# Start application
docker-compose up -d

# Stop application  
docker-compose down

# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Check status
docker-compose ps

# Update to latest version
docker-compose pull
docker-compose up -d
```

### Development Setup

For local development:

```bash
# Clone repository
git clone https://github.com/jhowell-ocs/FuelTime.git
cd FuelTime

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install -r requirements-dev.txt

# Run locally
python app.py
```

## Security & Code Quality

Run security checks locally:

```bash
# Code formatting
black --check .
isort --check-only .

# Linting
flake8 .
pylint app.py

# Security scans
bandit -r .
pip-audit -r requirements.txt
```

For detailed security information, see [SECURITY.md](SECURITY.md) and [DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

**Obion County Schools IT Department**  
📧 jhowell@ocboe.com