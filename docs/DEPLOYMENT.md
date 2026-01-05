# FuelTime - Enhanced Security & Docker Deployment Guide

## 🔒 Security Features

This repository now includes comprehensive security and code quality checks via GitHub Actions. Every push triggers automated scans for:

- **Code Quality**: Black, isort, Flake8, Pylint
- **Security Vulnerabilities**: Bandit, Safety, Trivy
- **Dependency Scanning**: Automated CVE detection
- **Docker Image Scanning**: Container vulnerability assessment

## 📦 GitHub Container Registry (GHCR)

Docker images are automatically built and published to GitHub Container Registry on every push to `main` or when version tags are created.

### Pulling Images

```bash
# Pull latest version
docker pull ghcr.io/YOUR_USERNAME/fueltime:latest

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/fueltime:v1.0.0

# Pull from branch
docker pull ghcr.io/YOUR_USERNAME/fueltime:main
```

### Using the GHCR Image

Update your `docker-compose.yml` to use the published image:

```yaml
services:
  fueltime:
    image: ghcr.io/YOUR_USERNAME/fueltime:latest
    # ... rest of your configuration
```

Or run directly:

```bash
docker run -d -p 5000:5000 \
  -v fueltime_temp:/app/temp \
  ghcr.io/YOUR_USERNAME/fueltime:latest
```

## 🚀 CI/CD Pipeline

### Workflow Stages

1. **Security Scan** - Runs on all pushes and PRs
   - Code formatting checks
   - Security vulnerability scanning
   - Dependency validation
   
2. **Docker Build & Test** - Builds and validates container
   - Multi-platform build test
   - Container health check validation
   - Image vulnerability scanning
   
3. **Publish to GHCR** - Publishes to GitHub Container Registry
   - Triggered on pushes to `main` or version tags
   - Generates multiple tags (latest, version, commit SHA)
   - Creates build attestation for supply chain security

### Viewing Results

- **Security Reports**: Check the "Actions" tab in GitHub
- **SARIF Results**: View in "Security" → "Code scanning alerts"
- **Artifacts**: Download detailed reports from workflow runs

## 🛡️ Security Best Practices

### Before Deployment

1. Review security scan results in GitHub Actions
2. Update dependencies regularly: `pip install -U -r requirements.txt`
3. Run local security checks:
   ```bash
   bandit -r .
   safety check
   ```

### Production Configuration

1. **Disable debug endpoints** - Set environment variable:
   ```bash
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```

2. **Use secrets management** - Never commit sensitive data
3. **Enable HTTPS** - Use reverse proxy (nginx/traefik) with SSL
4. **Implement rate limiting** - Protect against abuse
5. **Regular updates** - Monitor security advisories

## 🏷️ Version Tagging

To trigger a new release:

```bash
# Update VERSION file
echo "1.0.3" > VERSION

# Commit and tag
git add VERSION
git commit -m "Bump version to 1.0.3"
git tag v1.0.3
git push origin main --tags
```

This will automatically:
- Run security scans
- Build Docker image
- Publish to GHCR with tags: `v1.0.3`, `1.0`, `1`, `latest`

## 📋 Manual Security Checks

### Run Locally

```bash
# Install tools
pip install bandit safety pylint flake8 black isort

# Code formatting
black --check .
isort --check-only .

# Linting
flake8 .
pylint app.py

# Security scans
bandit -r .
safety check
```

### Docker Security Scan

```bash
# Build image
docker build -t fueltime:local .

# Scan with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image fueltime:local
```

## 🔐 GitHub Secrets

No additional secrets are required! The workflow uses the built-in `GITHUB_TOKEN` for GHCR authentication.

For custom registries, add these secrets in repository settings:
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`

## 📊 Monitoring & Alerts

- **Security Alerts**: Enable Dependabot alerts in repository settings
- **Code Scanning**: Automatic SARIF upload to GitHub Security
- **Workflow Notifications**: Configure in personal settings

## 🆘 Troubleshooting

### Image Pull Permissions

If you get "permission denied" when pulling:

```bash
# Authenticate with GitHub
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

Make sure the repository visibility allows package access (Settings → Packages).

### Build Failures

Check the Actions tab for detailed logs. Common issues:
- Dependency conflicts: Update requirements.txt
- Security vulnerabilities: Review Bandit/Safety reports
- Docker build errors: Check Dockerfile syntax

## 📞 Support

For security issues, see [SECURITY.md](../SECURITY.md)

For general questions: jhowell@ocboe.com
