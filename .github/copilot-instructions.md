# Copilot Instructions for FuelTime

**Important:** Always use the context7 MCP tool to gather project context and dependencies before taking any other action in this codebase. This ensures all AI agents have the most accurate, up-to-date information for FuelTime.

## Project Overview
- **FuelTime** is a Flask web application for Obion County Schools, providing digital forms for monthly fuel reporting and employee timesheet management.
- The app generates professional PDFs for both forms using `pdfkit` and `wkhtmltopdf`.
- The app is designed for both local and Dockerized deployment, with special handling for PDF generation in containers (Xvfb, DISPLAY setup).

## Key Components
- `app.py`: Main Flask app, routes for form display, PDF generation, and health checks. Handles environment detection (local vs container) and PDF engine setup.
- `templates/`: Jinja2 HTML templates for forms and PDF output (`fuel_form.html`, `pdf_template.html`, `timesheet_pdf_template.html`).
- `static/`: Static assets (e.g., logo.png).
- `temp/`: Temporary directory for PDF generation (mounted as a Docker volume in production).

## Developer Workflows
- **Local Development:**
  - Run with `flask run` or `python app.py` (ensure `wkhtmltopdf` is installed and on PATH).
  - Temp files are stored in `./temp`.
- **Docker Deployment:**
  - Use `docker-compose up -d` to build and run. The container auto-configures Xvfb and DISPLAY for headless PDF generation.
  - Healthcheck endpoint: `/debug/temp`.
  - Temp files are stored in `/app/temp` (mounted volume).
- **Logs:**
  - Use `docker-compose logs -f` for container logs.

## Project-Specific Patterns
- **PDF Generation:**
  - Uses `pdfkit` with `wkhtmltopdf`. On Windows, attempts to auto-detect common install paths.
  - In Docker, Xvfb is started for headless PDF rendering.
- **Environment Detection:**
  - Checks for `/app` directory to distinguish container vs local.
  - Sets up temp directory and permissions accordingly.
- **Health Checks:**
  - `/debug/temp` endpoint for Docker healthcheck (verifies temp dir is writable).
- **Form Handling:**
  - Main UI is a tabbed form (`fuel_form.html`) with client-side logic for switching between fuel and timesheet forms.
  - Submissions generate PDFs using the corresponding template.

## External Dependencies
- Flask, pdfkit, wkhtmltopdf, Xvfb (in Docker), Gunicorn (in Docker), standard system fonts.

## Example: Adding a New Form
- Add a new HTML template in `templates/`.
- Add a route in `app.py` for form display and PDF generation.
- Update the main form UI (`fuel_form.html`) to include a new tab/button.

## Conventions
- All temp files for PDF generation go in the `temp/` directory (or `/app/temp` in Docker).
- Use environment detection logic in `app.py` for any file path or OS-specific code.
- All static assets should be placed in `static/`.

---
For questions, contact jhowell@ocboe.com
