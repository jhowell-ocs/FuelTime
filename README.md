<div align="center">
  <img src="static/logo.png" alt="Obion County Schools" width="400">
  
  # FuelTime
  
  **Professional Forms Portal for Obion County Schools**
  
  A web-based application for fuel reporting and timesheet management with professional PDF generation.
</div>

---

## Overview

FuelTime provides a streamlined digital solution for managing two essential administrative forms:

- **Fuel Reports**: Monthly fuel consumption tracking with vehicle information
- **Employee Timesheets**: Hours tracking with automatic calendar functionality and total calculations

Both forms feature professional PDF generation for official documentation and record-keeping.

## Deployment

### Using Docker Compose

1. **Create a project directory:**
   ```bash
   mkdir fueltime-app
   cd fueltime-app
   ```

2. **Create `docker-compose.yml`:**
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

3. **Start the application:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
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
```

---

**Obion County Schools IT Department**  
📧 jhowell@ocboe.com