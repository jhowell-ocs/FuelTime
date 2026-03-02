# Security Scanning Quick Reference

## Overview

FuelTime uses automated security scanning to identify vulnerabilities in code, dependencies, and Docker images. This guide explains how to view results, enable GitHub Code Scanning, and troubleshoot common issues.

## GitHub Security Tab (Code Scanning)

### Status Check

```bash
# Check if code scanning is enabled
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate

# 200 + results = Working
# 200 + empty array = Enabled but no alerts
# 404 = Code scanning not enabled
# 403 = Permission issue
```

### Enable Code Scanning

#### Public Repository

Code scanning is **free** for public repositories but must be enabled:

1. Navigate to: **Settings** → **Code security and analysis**
2. Find **"Code scanning"** section
3. Click **Set up** → **Advanced**
4. Confirm workflow detected (`.github/workflows/ci-cd.yml`)
5. Enable code scanning

**Via GitHub CLI:**
```bash
# Note: This only works if you have admin permissions
gh api -X PATCH repos/jhowell-ocs/FuelTime \
  -f security_and_analysis[advanced_security][status]=enabled
```

#### Private Repository

Code scanning requires **GitHub Advanced Security (GHAS)** for private repositories:

**Requirements:**
- GHAS license (included in GitHub Enterprise or $49/user/month)
- Organization admin access to enable GHAS
- Repository admin access to enable code scanning

**Steps:**
1. Contact your organization admin to enable GHAS for your organization
2. Enable GHAS for the FuelTime repository
3. Follow the public repository steps above to enable code scanning

**Alternative (if GHAS unavailable):**
- Use artifact-based reporting (always available, see below)
- Use inline summaries in Actions tab
- Consider making repository public (if security policy allows)

### Viewing Results

#### Option 1: GitHub Security Tab (Preferred - Requires GHAS/Code Scanning)

1. Navigate to repository → **Security** tab
2. Click **"Code scanning"** in left sidebar
3. View alerts organized by:
   - **trivy-filesystem** - Dependencies and code vulnerabilities
   - **trivy-container-image** - Docker image vulnerabilities
4. Filter by severity, status, or tool
5. Click any alert for details:
   - CVE/vulnerability ID
   - Affected package and version
   - Severity level
   - Remediation advice
   - Affected file locations

#### Option 2: Actions Artifacts (Always Available)

This fallback method works regardless of GHAS/code scanning status:

1. Navigate to repository → **Actions** tab
2. Click on the most recent workflow run
3. Scroll to **"Artifacts"** section at the bottom
4. Download one or both:
   - **trivy-filesystem-report** - Dependencies and code scan results
   - **trivy-container-image-report** - Docker image scan results
5. Extract the downloaded ZIP file
6. Open the JSON file to view detailed results

**Quick analysis with jq:**
```bash
# Extract critical vulnerabilities
jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")' trivy-results.json

# Count vulnerabilities by severity
jq '.Results[]?.Vulnerabilities[]? | .Severity' trivy-results.json | sort | uniq -c

# List all CVEs
jq -r '.Results[]?.Vulnerabilities[]? | .VulnerabilityID' trivy-results.json | sort -u
```

#### Option 3: Inline Summaries (Always Available)

View quick summaries directly in the Actions tab:

1. Navigate to repository → **Actions** tab
2. Click on a workflow run
3. Click on **"Security & Code Quality"** or **"Docker Build & Test"** job
4. View the markdown summary showing:
   - Vulnerability counts by severity
   - Top critical vulnerabilities (if any)
   - Quick overview without downloading files

### Troubleshooting

#### SARIF Upload Fails

**Error Message:**
```
Advanced Security must be enabled for this repository to use code scanning.
```

**Solutions:**
- **For public repos:** Enable code scanning in Settings → Code security
- **For private repos:** Enable GHAS (requires license) or use artifacts fallback
- **Immediate workaround:** Download JSON artifacts (always available)

#### No Alerts in Security Tab

**Possible Causes:**
1. GHAS/Code scanning not enabled
2. SARIF upload failed (check workflow logs)
3. No vulnerabilities found (good news!)

**Verification Steps:**
```bash
# Check if code scanning is enabled
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts

# Check latest workflow run logs
gh run view --log | grep -A 10 "Upload Trivy SARIF"
```

#### Workflow Fails After Update

**Context:**
- **Old behavior:** `continue-on-error: true` masked failures silently
- **New behavior:** Failures are explicit and visible (intentional)

**What This Means:**
- You'll now see when SARIF uploads fail (usually due to GHAS not enabled)
- Security scans still run and artifacts are still available
- Error messages guide you to the solution

**Action:**
- Check error message in workflow logs
- Follow troubleshooting guidance in the message
- Download artifacts if Security tab is unavailable

#### Permission Issues

**Error Message:**
```
Resource not accessible by integration
```

**Solution:**
Verify workflow has correct permissions (should already be configured):
```yaml
permissions:
  contents: read
  security-events: write  # Required for SARIF upload
```

#### Invalid SARIF

**Error Message:**
```
Invalid SARIF. Schema validation failed.
```

**Diagnosis:**
1. Check Trivy version: `trivy --version` (should be v0.50+)
2. Validate SARIF locally: `jq empty trivy-results.sarif`
3. Review Trivy scan step logs for errors

**Solution:**
- If Trivy generated invalid output, check for Trivy issues on GitHub
- JSON artifacts are still available as fallback
- Report issue if persistent

## Manual Scanning (Local Development)

### Filesystem Scan

Scan your local codebase before committing:

```bash
# Install Trivy (if not already installed)
# macOS
brew install aquasecurity/trivy/trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Windows (Chocolatey)
choco install trivy

# Run filesystem scan
trivy fs --severity CRITICAL,HIGH,MEDIUM --format json --output trivy-fs.json .

# View results
jq '.Results[]?.Vulnerabilities[]?' trivy-fs.json | less
```

### Container Image Scan

Scan the Docker image locally:

```bash
# Build image
docker build -t fueltime:test .

# Scan image
trivy image --severity CRITICAL,HIGH,MEDIUM --format json --output trivy-image.json fueltime:test

# View results
jq '.Results[]?.Vulnerabilities[]?' trivy-image.json | less
```

### Quick Scan (Table Format)

For human-readable output:

```bash
# Filesystem
trivy fs --severity CRITICAL,HIGH .

# Container image
trivy image fueltime:test
```

## Security Scan Schedule

### Automatic Scans

Security scans run automatically on:
- ✅ Every push to `main` branch
- ✅ Every push to `develop` branch
- ✅ Every pull request to `main` or `develop`
- ✅ Every version tag push (e.g., `v3.1.6`)

### Manual Scans

Trigger a manual scan:

```bash
# Via GitHub CLI
gh workflow run ci-cd.yml --ref main

# Via GitHub web interface
# Actions → CI/CD Pipeline → Run workflow → Select branch → Run workflow
```

### Recommended Workflow

1. **Before committing:** Run local scan to catch issues early
2. **Create PR:** Automated scan runs on PR
3. **Review results:** Check Actions tab or Security tab
4. **After merge:** Full scan runs on protected branch

## Understanding Scan Results

### Severity Levels

| Severity | Icon | Description | Action Required |
|----------|------|-------------|-----------------|
| **CRITICAL** | 🔴 | Actively exploited or trivially exploitable | **Fix immediately** |
| **HIGH** | 🟠 | Easily exploitable with significant impact | **Fix in current sprint** |
| **MEDIUM** | 🟡 | Requires specific conditions to exploit | **Fix in next release** |
| **LOW** | 🔵 | Minimal risk or requires unlikely conditions | **Consider fixing** |

### Vulnerability Types

**Dependency Vulnerabilities:**
- Outdated Python packages with known CVEs
- Transitive dependencies (indirect dependencies)
- Solution: Update to patched versions

**Container Image Vulnerabilities:**
- Outdated base image layers
- System packages in the container
- Solution: Update base image, rebuild

**Configuration Issues:**
- Insecure Dockerfile practices
- Missing security headers
- Solution: Follow security best practices

### False Positives

Sometimes vulnerabilities are flagged that don't apply:

**Common Cases:**
- Vulnerability in unused dependency features
- Already mitigated by configuration
- Applies to different OS/environment

**What To Do:**
1. Investigate whether vulnerability actually applies
2. If false positive, document in PR or issue
3. Consider suppressing in Trivy config (`.trivyignore`)
4. Report false positive to Trivy project if appropriate

## GitHub Actions Integration

### Workflow Structure

```
┌─────────────────────────────────────┐
│  security-scan job                  │
│  ├─ Run Trivy (SARIF)              │
│  ├─ Run Trivy (JSON)               │
│  ├─ Validate SARIF                 │
│  ├─ Upload to Security tab          │
│  ├─ Upload artifact                 │
│  └─ Generate summary                │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  docker-build-test job              │
│  ├─ Build Docker image              │
│  ├─ Scan image (SARIF)             │
│  ├─ Scan image (JSON)              │
│  ├─ Validate SARIF                 │
│  ├─ Upload to Security tab          │
│  ├─ Upload artifact                 │
│  └─ Generate summary                │
└─────────────────────────────────────┘
```

### Artifact Retention

- **Default retention:** 90 days
- **Storage:** Included in GitHub Actions free tier
- **Access:** Available to repository contributors
- **Cleanup:** Automatic after retention period

### Permissions

The workflow requires:
- `contents: read` - Read repository code
- `security-events: write` - Upload SARIF to code scanning

These permissions are scoped to the workflow run and don't expose sensitive data.

## Advanced Topics

### Customizing Scans

Edit `.github/workflows/ci-cd.yml` to customize:

**Change severity levels:**
```yaml
severity: 'CRITICAL,HIGH'  # Only critical and high
```

**Add vulnerability types:**
```yaml
vuln-type: 'os,library'  # Scan OS packages and libraries
```

**Scan specific paths:**
```yaml
scan-ref: './app'  # Only scan app directory
```

### Suppressing False Positives

Create `.trivyignore` in repository root:

```
# Ignore specific CVE (with reason)
CVE-2023-12345  # False positive: we don't use affected feature

# Ignore by package
pkg:pypi/package-name
```

### External Dashboards

For centralized security tracking across multiple projects:

**DefectDojo (Open Source):**
```yaml
- name: Upload to DefectDojo
  env:
    DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
    DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
  run: |
    curl -X POST "$DEFECTDOJO_URL/api/v2/import-scan/" \
      -H "Authorization: Token $DEFECTDOJO_TOKEN" \
      -F "file=@trivy-results.json" \
      -F "scan_type=Trivy Scan"
```

**Other Options:**
- Snyk (commercial)
- Dependency-Track (open source)
- JFrog Xray (commercial)

## Resources

### Documentation

- [GitHub Code Scanning Docs](https://docs.github.com/en/code-security/code-scanning)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)

### Quick Commands Reference

```bash
# Check code scanning status
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate

# Trigger manual scan
gh workflow run ci-cd.yml --ref main

# Watch workflow progress
gh run watch

# Download latest artifacts
gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

# View workflow logs
gh run view --log

# Local scan (filesystem)
trivy fs --severity CRITICAL,HIGH .

# Local scan (image)
trivy image fueltime:test

# Validate SARIF
jq empty trivy-results.sarif && echo "Valid" || echo "Invalid"
```

### Support

- **Trivy Issues:** https://github.com/aquasecurity/trivy/issues
- **GitHub Support:** https://support.github.com/
- **Project Issues:** [Create an issue](../../issues/new/choose)

---

**Last Updated:** March 2, 2026  
**Maintained By:** FuelTime Development Team
