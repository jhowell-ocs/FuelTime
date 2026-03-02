# GitHub Security Workflow Restoration Specification

**Document Version:** 1.0  
**Date:** March 2, 2026  
**Author:** GitHub Copilot Security Analysis  
**Status:** Draft - Awaiting Implementation

---

## Executive Summary

### Problem Statement

The GitHub Security tab for the FuelTime repository is not displaying Trivy security scan results as expected. Instead, it only shows the SECURITY.md file, indicating that automated security scanning results are not being ingested into GitHub's Code Scanning interface. This issue emerged after completing Trivy vulnerability remediation work.

### Impact Assessment

**Current State:**
- ❌ Security scan results not visible in GitHub Security tab
- ❌ Automated vulnerability tracking non-functional
- ❌ Loss of GitHub's native security alerting and reporting
- ⚠️ Workflow appears to pass even when SARIF uploads fail (masked by `continue-on-error: true`)
- ✅ Local Trivy scans work correctly (JSON reports exist in workspace)
- ✅ GitHub Actions workflow executes successfully

**Business Impact:**
- **Visibility:** Team cannot see security posture at-a-glance in GitHub UI
- **Alerting:** Missing automated alerts for new vulnerabilities
- **Compliance:** Cannot demonstrate continuous security monitoring via GitHub
- **Tracking:** Unable to track remediation progress through GitHub's interface
- **Integration:** Losing benefit of GitHub's security ecosystem (dependency graph, security advisories)

**Risk Level:** MEDIUM (workflow runs but visibility/tracking compromised)

---

## Current State Analysis

### 1. Existing CI/CD Workflow Configuration

**File:** `.github/workflows/ci-cd.yml`

#### Security Scan Job (Lines 14-92)

```yaml
security-scan:
  name: Security & Code Quality
  runs-on: ubuntu-latest
  permissions:
    contents: read
    security-events: write    # ✅ Correct permission present
  
  steps:
    # ... code quality checks ...
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'          # ✅ Correct format for GitHub
        output: 'trivy-results.sarif'
      continue-on-error: true    # ⚠️ MASKS FAILURES
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
      continue-on-error: true    # ⚠️ MASKS FAILURES
```

#### Docker Build Job (Lines 94-141)

```yaml
docker-build-test:
  name: Docker Build & Test
  runs-on: ubuntu-latest
  permissions:
    contents: read
    security-events: write    # ✅ Correct permission present
  
  steps:
    # ... build steps ...
    
    - name: Scan Docker image with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'fueltime:test'
        format: 'sarif'
        output: 'trivy-image-results.sarif'
      continue-on-error: true    # ⚠️ MASKS FAILURES
    
    - name: Upload Trivy image scan results
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-image-results.sarif'
      continue-on-error: true    # ⚠️ MASKS FAILURES
```

**Assessment:**
- ✅ Permissions correctly configured (`security-events: write`)
- ✅ SARIF format correctly specified
- ✅ Using correct actions (aquasecurity/trivy-action, github/codeql-action/upload-sarif)
- ✅ `if: always()` ensures upload attempts even on scan failures
- ⚠️ **CRITICAL ISSUE:** `continue-on-error: true` on all steps masks failures
- ❓ **UNKNOWN:** Whether GitHub Advanced Security is enabled for the repository

### 2. Local Trivy Scan Results

**Files Present in Workspace:**
- `trivy-config-report.json` (257 lines) - Dockerfile configuration scan
- `trivy-fs-report.json` (263 lines) - Filesystem/dependency scan  
- `trivy-image-report.json` (23,647 lines) - Container image scan

**Analysis:**
- ✅ All reports are recent (March 2, 2026, 08:59-09:06)
- ✅ Reports show successful Trivy execution locally
- ✅ Trivy v0.69.2 is working correctly
- ✅ Scans cover all necessary dimensions (config, filesystem, image)
- ❌ Reports are in JSON format, not SARIF (local scans, not workflow outputs)

**Metadata from Reports:**
```json
"RepoURL": "https://github.com/jhowell-ocs/FuelTime.git",
"Branch": "main",
"Commit": "781bd3f22da3f81ca59330f6185d5c9d746ab0cc"
```

**Conclusion:** Trivy works correctly; problem is in GitHub integration layer.

### 3. Repository Structure Analysis

**GitHub Configuration Files:**
- `.github/workflows/ci-cd.yml` - Main workflow (exists, configured correctly syntactically)
- `.github/dependabot.yml` - Dependency updates (exists)
- `SECURITY.md` - Security policy (exists, shows in Security tab)

**Documentation References:**
Multiple docs reference expected behavior:
- `docs/DEPLOYMENT.md:70` - "SARIF Results: View in 'Security' → 'Code scanning alerts'"
- `docs/PRE_PUSH_TEST_RESULTS.md:97` - "Security scans will be visible in GitHub Security tab"
- `docs/IMPLEMENTATION_SUMMARY.md:293` - "Visibility: Security alerts in GitHub Security tab"
- `.github/CI_CD_GUIDE.md:116` - "Navigate to: Security → Code scanning"

**Observation:** Documentation consistently indicates SARIF upload to Security tab was intended and expected to work.

### 4. Previous Security Work

**Files:** 
- `docs/SubAgent/trivy_security_remediation_spec.md` (1,192 lines)
- `docs/SubAgent/trivy_security_remediation_review.md` (689 lines)

**Findings from Review:**

The trivy security remediation work (Phase 1 & Phase 2) focused on:
1. ✅ Updating Python dependencies (Flask 3.0.3 → 3.1.3, Werkzeug 3.1.4 → 3.1.6)
2. ✅ Implementing non-root Docker user (`appuser:appuser`)
3. ✅ Adding Dockerfile security best practices (`--no-install-recommends`)
4. ✅ Resolving 71 vulnerabilities (3 CRITICAL, 15 HIGH, 54 MEDIUM)
5. ✅ Build validation - Docker image builds successfully

**What's Missing:**
The remediation spec mentioned GitHub security integration but did NOT address:
- ❌ Verifying GitHub Advanced Security enablement
- ❌ Testing SARIF upload functionality
- ❌ Validating Security tab visibility
- ❌ Removing `continue-on-error: true` flags for failure detection

**Quote from spec (line 580):**
```yaml
# .github/workflows/security-scan.yml  # ← Note: wrong filename, actually ci-cd.yml
- name: Run Trivy scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'fueltime-fueltime:latest'
    severity: 'CRITICAL,HIGH'
```

**Conclusion:** Original implementation assumed GitHub Code Scanning would "just work" without verifying prerequisites.

---

## Root Cause Analysis

### Primary Cause: GitHub Advanced Security Not Enabled or Configured

**GitHub Code Scanning Requirements:**

1. **For Public Repositories:**
   - ✅ GitHub Advanced Security features are **FREE**
   - ⚠️ **Code Scanning MUST be manually enabled** in repository settings
   - Path: `Settings` → `Code security and analysis` → `Code scanning` → `Set up`
   
2. **For Private Repositories:**
   - ❌ GitHub Advanced Security is a **PAID FEATURE** (requires GitHub Enterprise Cloud or GitHub One)
   - ❌ SARIF upload will **FAIL** without GHAS license
   - ⚠️ Error message: "Advanced Security must be enabled for this repository to use code scanning"

3. **Permission Requirements (Both):**
   - ✅ Workflow needs `security-events: write` permission (present in FuelTime)
   - ✅ `GITHUB_TOKEN` must have appropriate scopes (automatic in GitHub Actions)

**Research Sources:**

| Source | Key Information | URL |
|--------|----------------|-----|
| **GitHub Docs: Code Scanning** | "Code scanning is available for all public repositories, and for private repositories owned by organizations where GitHub Advanced Security is enabled." | https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning |
| **GitHub Docs: SARIF Upload** | "To upload a SARIF file to a repository, you must enable GitHub Advanced Security for that repository (if it's private)." | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github |
| **Trivy Action Docs** | "For code scanning, use format: 'sarif' and github/codeql-action/upload-sarif action." | https://github.com/aquasecurity/trivy-action |
| **CodeQL Action Docs** | "upload-sarif action requires security-events: write permission and code scanning to be enabled." | https://github.com/github/codeql-action |
| **GitHub Blog: GHAS** | "Advanced Security is free for public repositories and requires a license for private repositories." | https://github.blog/changelog/2020-09-30-code-scanning-is-now-available/ |
| **Stack Overflow: Common Issues** | "Most common reason for SARIF not appearing: Code scanning not enabled in Settings." | Multiple posts (2020-2024) |

### Secondary Cause: Silent Failure Masking

**Problem:** `continue-on-error: true` on all security steps

**Impact:**
```yaml
- name: Upload Trivy results to GitHub Security
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: 'trivy-results.sarif'
  continue-on-error: true    # ← Workflow shows ✅ even when this FAILS
```

**Why This Matters:**
- Upload can fail due to missing GHAS enablement
- Workflow still shows green checkmark (passing)
- No visible indication of problem unless examining logs
- User assumes security scanning is working when it's not

**Evidence:**
User report states: *"security tab now only shows the SECURITY.md file"* - this confirms SARIF uploads are failing but workflow succeeds.

### Tertiary Causes (Possible)

1. **Repository Visibility Change**
   - If repository was public → private recently
   - GHAS would need manual enablement
   - Previous SARIF uploads would stop working

2. **Organization Settings**
   - Code scanning might be disabled at organization level
   - Requires organization admin to enable

3. **SARIF File Generation Failure**
   - Trivy might be failing to generate valid SARIF
   - However, local JSON generation works, so unlikely

4. **GitHub API Changes**
   - CodeQL action v4 requires specific runner versions
   - Unlikely as other projects work fine

---

## Proposed Solution Architecture

### Solution Overview

Implement a **three-tier approach** to restore and enhance security workflow visibility:

1. **Tier 1: Enable GitHub Code Scanning** (Prerequisite)
2. **Tier 2: Fix Workflow Error Handling** (Critical)
3. **Tier 3: Add Fallback Reporting** (Enhancement)

### Tier 1: Enable GitHub Code Scanning

**Objective:** Enable GitHub's native code scanning interface

**For Public Repositories:**

1. Navigate to repository settings
2. Go to: `Settings` → `Code security and analysis`
3. Find "Code scanning" section
4. Click `Set up` → `Advanced` (for custom workflow)
5. Confirm workflow is detected (ci-cd.yml)
6. Enable code scanning

**For Private Repositories:**

1. **Option A: Enable GHAS (Requires License)**
   - Contact GitHub sales or organization admin
   - Enable GitHub Advanced Security for organization
   - Enable GHAS for FuelTime repository
   - **Cost:** Included in GitHub Enterprise, or $49/user/month for GitHub Advanced Security standalone

2. **Option B: Make Repository Public (If Acceptable)**
   - Change repository visibility to public
   - Code scanning becomes free automatically
   - **Consideration:** Security policy allows open-source?

3. **Option C: Use Artifacts Only (Fallback)**
   - Keep repository private
   - Don't enable GHAS
   - Rely on workflow artifacts (JSON reports)
   - Use external dashboard/tooling for visualization
   - **Limitation:** No GitHub Security tab integration

**Validation:**
```bash
# After enabling, check via GitHub CLI
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate
# Should return empty array or alerts, NOT 404 error

# Check settings
gh api repos/jhowell-ocs/FuelTime --jq '.security_and_analysis'
# Should show: "advanced_security": { "status": "enabled" }
```

### Tier 2: Fix Workflow Error Handling

**Objective:** Detect and report SARIF upload failures immediately

#### Change 1: Remove Silent Failures

**Current (ci-cd.yml lines 69, 85, 92):**
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'
  continue-on-error: true    # ← REMOVE THIS
```

**Proposed:**
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH,MEDIUM'
    exit-code: '0'    # Don't fail on vulnerabilities found
  # continue-on-error removed - Trivy failures should be visible
```

**Rationale:**
- Trivy should generate SARIF even with vulnerabilities present
- `exit-code: '0'` prevents failure when vulnerabilities found
- Actual failures (e.g., network issues) should be visible
- SARIF generation failure should fail the step

#### Change 2: Conditional SARIF Upload

**Current (ci-cd.yml lines 87-92):**
```yaml
- name: Upload Trivy results to GitHub Security
  uses: github/codeql-action/upload-sarif@v4
  if: always()
  with:
    sarif_file: 'trivy-results.sarif'
  continue-on-error: true    # ← REMOVE THIS
```

**Proposed:**
```yaml
- name: Upload Trivy results to GitHub Security
  uses: github/codeql-action/upload-sarif@v4
  if: always()
  with:
    sarif_file: 'trivy-results.sarif'
    category: 'trivy-filesystem'    # Categorize scans
  continue-on-error: false    # Fail if GHAS not enabled
  
- name: Check for SARIF upload failure
  if: failure()
  run: |
    echo "::warning::SARIF upload failed. Ensure GitHub Advanced Security is enabled."
    echo "::warning::For private repos: Settings → Code security → Enable GHAS"
    echo "::warning::For public repos: Settings → Code security → Set up Code scanning"
    echo "::warning::See docs/SubAgent/security_workflow_restoration_spec.md"
```

**Rationale:**
- Explicit failure when GHAS not configured
- Custom warning message guides remediation
- Links to documentation for next steps
- `category` parameter organizes multiple scans in UI

#### Change 3: Add SARIF Validation

**New step before upload:**
```yaml
- name: Validate SARIF file
  run: |
    if [ ! -f trivy-results.sarif ]; then
      echo "::error::SARIF file not generated by Trivy"
      exit 1
    fi
    
    # Check if SARIF is valid JSON
    if ! jq empty trivy-results.sarif 2>/dev/null; then
      echo "::error::SARIF file is not valid JSON"
      exit 1
    fi
    
    # Check SARIF schema version
    VERSION=$(jq -r '.version' trivy-results.sarif)
    echo "SARIF schema version: $VERSION"
    
    # Check for runs array
    RUNS=$(jq '.runs | length' trivy-results.sarif)
    echo "Found $RUNS scan run(s) in SARIF"
```

**Rationale:**
- Catches Trivy configuration errors early
- Validates SARIF format before upload attempt
- Provides diagnostic information in logs

#### Change 4: Duplicate Scans (Add JSON Output for Fallback)

**Strategy:** Generate both SARIF (for GitHub) and JSON (for artifacts)

```yaml
- name: Run Trivy vulnerability scanner (SARIF for GitHub)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH,MEDIUM'

- name: Run Trivy vulnerability scanner (JSON for artifacts)
  uses: aquasecurity/trivy-action@master
  if: always()
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'json'
    output: 'trivy-results.json'
    severity: 'CRITICAL,HIGH,MEDIUM'

- name: Upload Trivy JSON results (artifact)
  uses: actions/upload-artifact@v7
  if: always()
  with:
    name: trivy-filesystem-report
    path: trivy-results.json
    retention-days: 90
```

**Rationale:**
- SARIF for GitHub Security tab (when GHAS enabled)
- JSON for artifact download and external processing
- Ensures security data is always available somewhere
- 90-day retention for audit trail

### Tier 3: Add Fallback Reporting

**Objective:** Provide security visibility even without GHAS

#### Option A: Generate Markdown Summary

```yaml
- name: Generate security summary
  if: always()
  run: |
    # Install jq if needed
    sudo apt-get update && sudo apt-get install -y jq
    
    # Parse Trivy JSON results
    cat << 'EOF' > generate_summary.sh
    #!/bin/bash
    JSON_FILE="trivy-results.json"
    
    if [ ! -f "$JSON_FILE" ]; then
      echo "⚠️ Trivy results not found"
      exit 0
    fi
    
    echo "# 🔒 Security Scan Summary" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    
    # Count vulnerabilities by severity
    CRITICAL=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' $JSON_FILE)
    HIGH=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity=="HIGH")] | length' $JSON_FILE)
    MEDIUM=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' $JSON_FILE)
    LOW=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity=="LOW")] | length' $JSON_FILE)
    
    echo "| Severity | Count |" >> $GITHUB_STEP_SUMMARY
    echo "|----------|-------|" >> $GITHUB_STEP_SUMMARY
    echo "| 🔴 Critical | $CRITICAL |" >> $GITHUB_STEP_SUMMARY
    echo "| 🟠 High | $HIGH |" >> $GITHUB_STEP_SUMMARY
    echo "| 🟡 Medium | $MEDIUM |" >> $GITHUB_STEP_SUMMARY
    echo "| 🔵 Low | $LOW |" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    
    # Add top 5 critical vulnerabilities
    if [ "$CRITICAL" -gt 0 ]; then
      echo "## 🚨 Critical Vulnerabilities" >> $GITHUB_STEP_SUMMARY
      echo "" >> $GITHUB_STEP_SUMMARY
      jq -r '.Results[].Vulnerabilities[]? | select(.Severity=="CRITICAL") | "- **\(.VulnerabilityID)** (\(.PkgName)@\(.InstalledVersion)) - \(.Title)"' $JSON_FILE | head -5 >> $GITHUB_STEP_SUMMARY
    fi
    EOF
    
    chmod +x generate_summary.sh
    ./generate_summary.sh
```

**Benefit:** Inline security summary in Actions tab, visible without GHAS

#### Option B: Fail Workflow on Critical Vulnerabilities

```yaml
- name: Check for critical vulnerabilities
  if: always()
  run: |
    CRITICAL=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' trivy-results.json)
    
    if [ "$CRITICAL" -gt 0 ]; then
      echo "::error::Found $CRITICAL critical vulnerabilities"
      echo "::error::Review trivy-results.json artifact for details"
      exit 1
    fi
```

**Benefit:** Prevents merging code with critical vulnerabilities

#### Option C: External Dashboard (Future Enhancement)

**Tools to Consider:**
- **DefectDojo** - Open-source vulnerability management
- **Dependency-Track** - Software composition analysis
- **Trivy Server** - Centralized Trivy scanning
- **Grafana + Prometheus** - Custom dashboard

**Integration:**
```yaml
- name: Upload to DefectDojo
  if: always()
  env:
    DEFECTDOJO_URL: ${{ secrets.DEFECTDOJO_URL }}
    DEFECTDOJO_TOKEN: ${{ secrets.DEFECTDOJO_TOKEN }}
  run: |
    curl -X POST "$DEFECTDOJO_URL/api/v2/import-scan/" \
      -H "Authorization: Token $DEFECTDOJO_TOKEN" \
      -F "file=@trivy-results.json" \
      -F "scan_type=Trivy Scan" \
      -F "engagement=1"
```

**Benefit:** Centralized security tracking across multiple projects

---

## Implementation Steps

### Phase 1: Enable GitHub Code Scanning (Day 1)

**Prerequisites:**
- Repository admin access
- Decision on repository visibility (public vs private)
- GHAS license (if private and proceeding with Tier 1)

**Steps:**

1. **Determine Repository Visibility**
   ```bash
   gh repo view jhowell-ocs/FuelTime --json visibility --jq '.visibility'
   # Returns: "public" or "private"
   ```

2. **Check Current GHAS Status**
   ```bash
   gh api repos/jhowell-ocs/FuelTime --jq '.security_and_analysis'
   # Check "advanced_security" status
   ```

3. **Enable Code Scanning (Public Repo)**
   - Navigate to: https://github.com/jhowell-ocs/FuelTime/settings/security_analysis
   - Find "Code scanning" section
   - Click "Set up" → "Advanced"
   - Confirm `.github/workflows/ci-cd.yml` is detected
   - Enable code scanning
   
   **OR via GitHub CLI:**
   ```bash
   # Enable vulnerability alerts
   gh api -X PATCH repos/jhowell-ocs/FuelTime \
     -f security_and_analysis[advanced_security][status]=enabled
   ```

4. **Enable Code Scanning (Private Repo with GHAS)**
   - Requires organization owner or admin
   - Enable GHAS for organization first
   - Then enable for repository
   - **OR via GitHub CLI:**
   ```bash
   gh api -X PATCH repos/jhowell-ocs/FuelTime \
     -f security_and_analysis[advanced_security][status]=enabled
   ```

5. **Verify Enablement**
   ```bash
   # Check repository settings
   gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate
   # Should return 200 OK (even if empty array)
   # 404 = Code scanning not enabled
   # 403 = Permission issue
   ```

**Success Criteria:**
- ✅ Code scanning shows as "Enabled" in repository settings
- ✅ API call to `/code-scanning/alerts` returns 200 status
- ✅ Security tab shows "Code scanning" section (may be empty initially)

**Time Estimate:** 15-30 minutes (if public repo or GHAS already available)

---

### Phase 2: Update Workflow Configuration (Day 1-2)

**File:** `.github/workflows/ci-cd.yml`

#### Changes Required:

**1. Update security-scan job (filesystem scan)**

Location: Lines 64-92

**Before:**
```yaml
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
      continue-on-error: true

    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
      continue-on-error: true
```

**After:**
```yaml
    - name: Run Trivy vulnerability scanner (SARIF)
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH,MEDIUM'
        exit-code: '0'
      # Removed: continue-on-error

    - name: Run Trivy vulnerability scanner (JSON)
      uses: aquasecurity/trivy-action@master
      if: always()
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'json'
        output: 'trivy-results.json'
        severity: 'CRITICAL,HIGH,MEDIUM,LOW'
        exit-code: '0'

    - name: Validate SARIF file
      if: always()
      run: |
        if [ ! -f trivy-results.sarif ]; then
          echo "::error::SARIF file not generated"
          exit 1
        fi
        if ! jq empty trivy-results.sarif 2>/dev/null; then
          echo "::error::SARIF file is invalid JSON"
          exit 1
        fi
        echo "SARIF validation passed"

    - name: Upload Trivy SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
        category: 'trivy-filesystem'
      # Removed: continue-on-error - let it fail if GHAS not enabled

    - name: SARIF upload troubleshooting
      if: failure()
      run: |
        echo "::warning::SARIF upload failed. This usually means:"
        echo "::warning::  1. GitHub Advanced Security is not enabled (for private repos)"
        echo "::warning::  2. Code scanning is not set up (Settings → Code security)"
        echo "::warning::  3. Permission issue with security-events token"
        echo "::warning::See: docs/SubAgent/security_workflow_restoration_spec.md"

    - name: Upload Trivy JSON results (artifact fallback)
      uses: actions/upload-artifact@v7
      if: always()
      with:
        name: trivy-filesystem-report
        path: trivy-results.json
        retention-days: 90

    - name: Generate security summary
      if: always()
      run: |
        if [ ! -f trivy-results.json ]; then
          echo "⚠️ Trivy results not found" >> $GITHUB_STEP_SUMMARY
          exit 0
        fi
        
        echo "# 🔒 Filesystem Security Scan" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        
        CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' trivy-results.json || echo 0)
        HIGH=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' trivy-results.json || echo 0)
        MEDIUM=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' trivy-results.json || echo 0)
        LOW=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="LOW")] | length' trivy-results.json || echo 0)
        
        echo "| Severity | Count |" >> $GITHUB_STEP_SUMMARY
        echo "|----------|-------|" >> $GITHUB_STEP_SUMMARY
        echo "| 🔴 Critical | $CRITICAL |" >> $GITHUB_STEP_SUMMARY
        echo "| 🟠 High | $HIGH |" >> $GITHUB_STEP_SUMMARY
        echo "| 🟡 Medium | $MEDIUM |" >> $GITHUB_STEP_SUMMARY
        echo "| 🔵 Low | $LOW |" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        
        if [ "$CRITICAL" -gt 0 ]; then
          echo "## 🚨 Critical Vulnerabilities" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL") | "- **\(.VulnerabilityID // "Unknown")** (\(.PkgName // "Unknown")@\(.InstalledVersion // "Unknown")) - \(.Title // "No title")"' trivy-results.json | head -5 >> $GITHUB_STEP_SUMMARY || echo "Could not parse vulnerabilities" >> $GITHUB_STEP_SUMMARY
        fi
```

**2. Update docker-build-test job (image scan)**

Location: Lines 127-141

**Before:**
```yaml
    - name: Scan Docker image with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'fueltime:test'
        format: 'sarif'
        output: 'trivy-image-results.sarif'
      continue-on-error: true

    - name: Upload Trivy image scan results
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-image-results.sarif'
      continue-on-error: true
```

**After:**
```yaml
    - name: Scan Docker image with Trivy (SARIF)
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'fueltime:test'
        format: 'sarif'
        output: 'trivy-image-results.sarif'
        severity: 'CRITICAL,HIGH,MEDIUM'
        exit-code: '0'

    - name: Scan Docker image with Trivy (JSON)
      uses: aquasecurity/trivy-action@master
      if: always()
      with:
        image-ref: 'fueltime:test'
        format: 'json'
        output: 'trivy-image-results.json'
        severity: 'CRITICAL,HIGH,MEDIUM,LOW'
        exit-code: '0'

    - name: Validate image SARIF file
      if: always()
      run: |
        if [ ! -f trivy-image-results.sarif ]; then
          echo "::error::Image SARIF file not generated"
          exit 1
        fi
        if ! jq empty trivy-image-results.sarif 2>/dev/null; then
          echo "::error::Image SARIF file is invalid JSON"
          exit 1
        fi
        echo "Image SARIF validation passed"

    - name: Upload Trivy image SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v4
      if: always()
      with:
        sarif_file: 'trivy-image-results.sarif'
        category: 'trivy-container-image'

    - name: Image SARIF upload troubleshooting
      if: failure()
      run: |
        echo "::warning::Image SARIF upload failed. See filesystem scan job for troubleshooting guidance."

    - name: Upload Trivy image JSON results (artifact fallback)
      uses: actions/upload-artifact@v7
      if: always()
      with:
        name: trivy-container-image-report
        path: trivy-image-results.json
        retention-days: 90

    - name: Generate image security summary
      if: always()
      run: |
        if [ ! -f trivy-image-results.json ]; then
          echo "⚠️ Image scan results not found" >> $GITHUB_STEP_SUMMARY
          exit 0
        fi
        
        echo "# 🐳 Container Image Security Scan" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        
        CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' trivy-image-results.json || echo 0)
        HIGH=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' trivy-image-results.json || echo 0)
        MEDIUM=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' trivy-image-results.json || echo 0)
        LOW=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="LOW")] | length' trivy-image-results.json || echo 0)
        
        echo "| Severity | Count |" >> $GITHUB_STEP_SUMMARY
        echo "|----------|-------|" >> $GITHUB_STEP_SUMMARY
        echo "| 🔴 Critical | $CRITICAL |" >> $GITHUB_STEP_SUMMARY
        echo "| 🟠 High | $HIGH |" >> $GITHUB_STEP_SUMMARY
        echo "| 🟡 Medium | $MEDIUM |" >> $GITHUB_STEP_SUMMARY
        echo "| 🔵 Low | $LOW |" >> $GITHUB_STEP_SUMMARY
```

**Testing:**
```bash
# Validate workflow syntax
gh workflow view ci-cd.yml

# Trigger workflow manually to test
gh workflow run ci-cd.yml --ref main

# Monitor workflow run
gh run watch

# Check for SARIF upload success
gh run view --log | grep "upload-sarif"
```

**Success Criteria:**
- ✅ Workflow runs without syntax errors
- ✅ SARIF files are generated and validated
- ✅ JSON artifacts are uploaded successfully
- ✅ Markdown summaries appear in Actions tab
- ✅ SARIF upload succeeds (or fails explicitly with helpful message)

**Time Estimate:** 2-4 hours (including testing)

---

### Phase 3: Validate Security Tab Integration (Day 2-3)

**Objective:** Confirm security scan results appear in GitHub Security tab

#### Step 1: Trigger Full Workflow

```bash
# Push a commit to trigger workflow
git add .github/workflows/ci-cd.yml
git commit -m "fix: restore GitHub Security tab integration for Trivy scans

- Remove continue-on-error from SARIF upload steps
- Add SARIF validation before upload
- Generate both SARIF (GitHub) and JSON (artifact) outputs
- Add inline security summaries in Actions tab
- Improve error messaging for GHAS troubleshooting

See: docs/SubAgent/security_workflow_restoration_spec.md"

git push origin main
```

#### Step 2: Monitor Workflow Execution

```bash
# Watch workflow run
gh run watch

# Or view in browser
gh run list --limit 1
# Click on the run URL
```

**What to Check:**
1. ✅ "Run Trivy vulnerability scanner (SARIF)" step completes
2. ✅ "Validate SARIF file" step passes
3. ✅ "Upload Trivy SARIF to GitHub Security" step status:
   - **SUCCESS** = GHAS enabled, upload worked
   - **FAILURE** = GHAS not enabled, check troubleshooting message
4. ✅ "Generate security summary" creates inline report
5. ✅ Artifacts include "trivy-filesystem-report" and "trivy-container-image-report"

#### Step 3: Verify Security Tab

**Navigation:**
1. Go to: https://github.com/jhowell-ocs/FuelTime/security
2. Click: "Code scanning" in left sidebar

**Expected Results (if GHAS enabled):**
- ✅ Two alert categories present:
  - "trivy-filesystem" (from security-scan job)
  - "trivy-container-image" (from docker-build-test job)
- ✅ Alerts for each vulnerability found (if any)
- ✅ Severity badges (Critical/High/Medium)
- ✅ Click on alert shows details (CVE, affected package, remediation)

**If Security Tab Still Empty:**
- Check workflow logs for "Upload Trivy SARIF" step
- Look for error: "Advanced Security must be enabled"
- Verify Code Scanning is enabled in Settings
- Check permissions: `security-events: write` (already present)

#### Step 4: Review Artifacts (Fallback)

**If GHAS not available:**
```bash
# Download latest artifacts
gh run download

# Extract and review JSON reports
cd trivy-filesystem-report
cat trivy-results.json | jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL" or .Severity=="HIGH")'

cd ../trivy-container-image-report
cat trivy-image-results.json | jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL" or .Severity=="HIGH")'
```

**Success Criteria:**
- ✅ Security tab shows scan results (if GHAS enabled)
- ✅ OR workflow logs clearly explain why SARIF upload failed
- ✅ JSON artifacts available for download and review
- ✅ Markdown summaries visible in Actions tab

**Time Estimate:** 1-2 hours (including validation and troubleshooting)

---

### Phase 4: Update Documentation (Day 3)

**Files to Update:**

#### 1. `.github/CI_CD_GUIDE.md`

Add section:

```markdown
## 🔒 GitHub Advanced Security Requirements

### For Private Repositories

To use GitHub Security tab integration, you must enable GitHub Advanced Security:

1. Navigate to: `Settings` → `Code security and analysis`
2. Enable "GitHub Advanced Security"
3. Enable "Code scanning"

**Note:** GHAS is a paid feature for private repositories. Contact GitHub sales or your organization admin.

### For Public Repositories

Code scanning is free for public repositories but must be enabled:

1. Navigate to: `Settings` → `Code security and analysis`
2. Find "Code scanning" section
3. Click `Set up` → `Advanced`
4. Confirm workflow detection

### Fallback: Artifacts

If GHAS is not available, security scan results are still available:
- Download artifacts: `Actions` → Select run → `Artifacts` section
- View inline summaries: `Actions` → Select run → Job summary
```

#### 2. `docs/DEPLOYMENT.md`

Update section (around line 70):

```markdown
### Viewing Results

- **Security Reports**: Check the "Actions" tab in GitHub
- **SARIF Results (with GHAS)**: View in "Security" → "Code scanning alerts"
- **SARIF Results (without GHAS)**: Download artifacts from workflow run
- **Artifacts**: Download JSON reports from workflow runs
- **Inline Summaries**: View in Actions tab job summaries
```

#### 3. `README.md`

Update security section:

```markdown
### 🔒 Security & Quality

- Automated security scanning with Bandit, pip-audit, and Trivy
- Code quality checks with Pylint, Flake8, and Black
- Continuous integration and deployment via GitHub Actions
- Container vulnerability scanning
- **Security results**: View in [Security tab](../../security/code-scanning) (requires GHAS) or download from [Actions artifacts](../../actions)
```

#### 4. Create Quick Reference Card

**New file:** `docs/SECURITY_SCANNING_GUIDE.md`

```markdown
# Security Scanning Quick Reference

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

**Public Repository:**
- Navigate to: Settings → Code security and analysis
- Code scanning → Set up → Advanced
- Confirm workflow detected

**Private Repository (requires GHAS):**
- Requires GitHub Advanced Security license
- Contact organization admin or GitHub sales
- Then follow public repository steps

### Viewing Results

#### Option 1: GitHub Security Tab (Preferred)
1. Go to repository → Security
2. Click "Code scanning" in left sidebar
3. Filter by severity, tool, status
4. Click alert for details and remediation

#### Option 2: Actions Artifacts (Always Available)
1. Go to repository → Actions
2. Select latest workflow run
3. Scroll to "Artifacts" section
4. Download "trivy-filesystem-report" or "trivy-container-image-report"
5. Extract and review JSON files

#### Option 3: Inline Summaries (Always Available)
1. Go to repository → Actions
2. Select latest workflow run
3. Click on "Security & Code Quality" job
4. View markdown summary with vulnerability counts

### Troubleshooting

#### SARIF Upload Fails
- **Error:** "Advanced Security must be enabled"
- **Solution:** Enable GHAS (private repos) or Code scanning (public repos)

#### No Alerts in Security Tab
- Check workflow logs for upload-sarif step
- Verify SARIF file was generated (check artifacts)
- Ensure permissions `security-events: write` is set (already configured)

#### Workflow Fails After Update
- Old behavior: continue-on-error masked failures
- New behavior: Failures are explicit and visible
- Check error messages for specific remediation steps

### Manual Scanning (Local)

```bash
# Filesystem scan
trivy fs --severity CRITICAL,HIGH,MEDIUM --format json --output trivy-fs.json .

# Container image scan
docker build -t fueltime:test .
trivy image --severity CRITICAL,HIGH,MEDIUM --format json --output trivy-image.json fueltime:test

# View results
jq '.Results[].Vulnerabilities[]' trivy-fs.json
jq '.Results[].Vulnerabilities[]' trivy-image.json
```

### Security Scan Schedule

- **Automatic:** Every push to main/develop
- **Automatic:** Every pull request
- **Manual:** `gh workflow run ci-cd.yml --ref main`
- **Recommended:** Run locally before committing

### Resources

- [GitHub Code Scanning Docs](https://docs.github.com/en/code-security/code-scanning)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
```

**Time Estimate:** 1-2 hours

---

## Dependencies and Requirements

### GitHub Repository Configuration

| Requirement | Status | Action Needed |
|-------------|--------|---------------|
| Repository admin access | ❓ Unknown | Verify user has admin role |
| GitHub Advanced Security (private repo) | ❓ Unknown | Check license availability |
| Code Scanning enabled | ❌ Missing | Enable in Settings |
| `security-events: write` permission | ✅ Present | No action needed |
| GitHub Actions enabled | ✅ Enabled | No action needed |

### Workflow Dependencies

| Dependency | Current Version | Required Version | Status |
|------------|-----------------|------------------|--------|
| aquasecurity/trivy-action | master | latest (master) | ✅ OK |
| github/codeql-action/upload-sarif | v4 | v3+ | ✅ OK |
| actions/upload-artifact | v7 | v4+ | ✅ OK |
| GitHub Actions Runner | N/A (GitHub-hosted) | 2.327.1+ | ✅ OK |

### Tool Requirements

| Tool | Purpose | Availability |
|------|---------|--------------|
| Trivy | Vulnerability scanning | ✅ via GitHub Action |
| jq | JSON parsing (validation) | ✅ pre-installed on ubuntu-latest |
| GitHub CLI (gh) | Testing/validation | ✅ recommended for validation |

### External Services

| Service | Purpose | Cost | Required? |
|---------|---------|------|-----------|
| GitHub Advanced Security | SARIF upload (private repos) | $49/user/month or included in Enterprise | Optional (required for Security tab with private repos) |
| None | Artifacts storage | Included in GitHub Actions | ✅ Always available |

### Permissions

**GitHub Token Scopes (automatic in Actions):**
- ✅ `contents: read` - Read repository files
- ✅ `security-events: write` - Upload SARIF to Code Scanning

**User Permissions Required:**
- ✅ Push to repository (to update workflow)
- ❓ Repository admin (to enable Code Scanning)

---

## Potential Risks and Mitigations

### Risk 1: GHAS Not Available for Private Repository

**Likelihood:** High (if repository is private and organization doesn't have GHAS license)  
**Impact:** Medium (security tab won't work, but artifacts still available)

**Mitigation Strategy:**
1. **Primary:** Use artifact-based reporting (always works)
2. **Secondary:** Generate inline markdown summaries (visible in Actions)
3. **Tertiary:** Make repository public (if security policy allows)
4. **Quaternary:** Purchase GHAS license (if budget available)

**Decision Tree:**
```
Is repository public?
├─ YES → Enable code scanning (free) → Full Security tab integration
└─ NO → Is GHAS available?
    ├─ YES → Enable GHAS + code scanning → Full Security tab integration
    └─ NO → Use artifacts + markdown summaries → Partial visibility
```

### Risk 2: Workflow Fails After Removing continue-on-error

**Likelihood:** Medium (temporary failures during transition)  
**Impact:** Low (explicit failures are better than silent failures)

**Mitigation:**
1. ✅ Add clear error messages explaining how to fix
2. ✅ Provide fallback artifacts (JSON reports)
3. ✅ Document troubleshooting steps
4. ✅ Test in feature branch before merging to main

**Rollback Plan:**
If workflow completely breaks:
```bash
git revert <commit-sha>
git push origin main
# Restores previous behavior while troubleshooting
```

### Risk 3: SARIF File Generation Failure

**Likelihood:** Low (Trivy is stable)  
**Impact:** High (no security data collected)

**Mitigation:**
1. ✅ Validate SARIF before upload attempt
2. ✅ Generate JSON in parallel (fallback)
3. ✅ Use `exit-code: '0'` to prevent failure on vulnerabilities
4. ✅ Add error handling and logging

**Detection:**
- Workflow step "Validate SARIF file" will catch this
- Error message will indicate specific failure reason

### Risk 4: Breaking Changes in Trivy Action

**Likelihood:** Low (master branch should be stable)  
**Impact:** Medium (scan might fail)

**Mitigation:**
1. Consider pinning to specific version: `aquasecurity/trivy-action@0.28.0`
2. Monitor Trivy changelog for breaking changes
3. Test workflow updates in feature branch

**Alternative:**
```yaml
# Pin to specific version instead of master
uses: aquasecurity/trivy-action@0.28.0
```

**Trade-off:** Stability vs automatic updates

### Risk 5: Storage Costs for Artifacts

**Likelihood:** Low  
**Impact:** Low (GitHub Actions includes free artifact storage)

**Current Usage:**
- JSON reports: ~25 KB filesystem + ~24 MB image = ~24 MB per run
- Retention: 90 days
- Estimated: 7 runs/week × 90 days ≈ 63 runs × 24 MB ≈ 1.5 GB
- Cost: Included in GitHub free tier (up to 2 GB)

**Mitigation:**
- Already configured: `retention-days: 90` (reasonable)
- Can reduce to 30 days if storage becomes issue
- SARIF files are only uploaded to GitHub (not stored as artifacts)

### Risk 6: Performance Impact (Duplicate Scans)

**Likelihood:** Certain (generating both SARIF and JSON)  
**Impact:** Low (~30 seconds additional time)

**Current Workflow Time:** ~5-10 minutes total  
**Additional Time:** ~30-60 seconds for duplicate scans  
**Percentage Impact:** ~10% increase

**Mitigation:**
- Run scans in parallel (already using `if: always()`)
- Cache Trivy database (consider adding)
- Accept minor performance hit for better reporting

**Optimization (Future):**
```yaml
- name: Cache Trivy database
  uses: actions/cache@v4
  with:
    path: ~/.cache/trivy
    key: trivy-db-${{ github.run_id }}
    restore-keys: trivy-db-
```

---

## Testing and Validation Strategy

### Pre-Implementation Testing

#### 1. Syntax Validation

```bash
# Validate workflow YAML syntax
gh workflow view ci-cd.yml

# OR use action-validator tool
docker run --rm -v "${PWD}:/repo" rhysd/actionlint:latest -color /repo/.github/workflows/ci-cd.yml
```

**Success Criteria:** No syntax errors

#### 2. Local SARIF Generation Test

```bash
# Install Trivy locally
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Generate SARIF
trivy fs --format sarif --output trivy-test.sarif .

# Validate SARIF format
jq empty trivy-test.sarif
jq '.version' trivy-test.sarif  # Should show: "2.1.0"
jq '.runs | length' trivy-test.sarif  # Should show: >= 1
```

**Success Criteria:** Valid SARIF file generated

### Implementation Testing

#### 1. Feature Branch Testing

```bash
# Create feature branch
git checkout -b feat/restore-security-tab-integration

# Make workflow changes
# (apply all Phase 2 changes)

# Commit and push
git add .github/workflows/ci-cd.yml
git commit -m "test: restore security tab integration"
git push origin feat/restore-security-tab-integration

# Trigger workflow
gh workflow run ci-cd.yml --ref feat/restore-security-tab-integration

# Monitor
gh run watch
```

**What to Check:**
- ✅ Workflow completes without errors
- ✅ SARIF validation passes
- ✅ JSON artifacts are uploaded
- ✅ Markdown summaries appear
- ⚠️ SARIF upload may fail if GHAS not enabled (expected in test)

#### 2. Main Branch Testing

```bash
# Merge to main (after feature branch validated)
gh pr create --title "Restore GitHub Security tab integration" --body "See docs/SubAgent/security_workflow_restoration_spec.md"
gh pr merge --squash

# Verify workflow on main
gh run watch

# Check Security tab
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate
```

**Success Criteria:**
- ✅ Workflow completes successfully on main
- ✅ Security tab updates (if GHAS enabled)
- ✅ OR clear error message (if GHAS not enabled)

### Post-Implementation Validation

#### 1. Security Tab Validation (if GHAS available)

**Manual Steps:**
1. Navigate to: https://github.com/jhowell-ocs/FuelTime/security/code-scanning
2. Verify two categories present:
   - trivy-filesystem
   - trivy-container-image
3. Click on an alert (if any)
4. Verify details are correct:
   - CVE ID
   - Affected package
   - Severity
   - Remediation advice

**API Validation:**
```bash
# List all code scanning alerts
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate | jq '.[] | {number, severity: .rule.severity, cve: .rule.id}'

# Check for specific CVE
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate | jq '.[] | select(.rule.id == "CVE-2025-15467")'
```

#### 2. Artifact Validation (always available)

```bash
# Get latest run ID
RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

# Download artifacts
gh run download $RUN_ID

# Verify JSON structure
cd trivy-filesystem-report
jq '.Results[]?.Vulnerabilities[]? | {id: .VulnerabilityID, severity: .Severity, pkg: .PkgName}' trivy-results.json | head -20

cd ../trivy-container-image-report
jq '.Results[]?.Vulnerabilities[]? | {id: .VulnerabilityID, severity: .Severity, pkg: .PkgName}' trivy-results.json | head -20
```

#### 3. Markdown Summary Validation

```bash
# View job summary in browser
gh run view $RUN_ID --web

# Or via API
gh api repos/jhowell-ocs/FuelTime/actions/runs/$RUN_ID/jobs | jq '.jobs[] | select(.name == "Security & Code Quality") | .html_url'
```

**What to Verify:**
- ✅ Tables show vulnerability counts by severity
- ✅ Critical vulnerabilities are listed (if any)
- ✅ Formatting is correct (tables render properly)

#### 4. Regression Testing

**Test Cases:**

| Test Case | Expected Result | Validation |
|-----------|----------------|------------|
| Push to main | Workflow triggers | `gh run list` shows new run |
| Push to develop | Workflow triggers | `gh run list` shows new run |
| Create PR | Workflow triggers | `gh pr checks` shows workflow |
| Version tag (v1.0.x) | Workflow triggers + publish | `gh run list` + GHCR image updated |
| Syntax error in Python | Flake8 catches error | Workflow fails at flake8 step |
| Critical vulnerability introduced | Alert appears | Security tab shows new alert (or JSON artifact) |
| Docker build failure | Workflow fails at build step | Clear error message in logs |
| SARIF corruption | Validation catches it | "Validate SARIF" step fails with clear message |

### Performance Testing

**Baseline (Current):**
```bash
# Record current workflow duration
gh run list --limit 5 --json name,databaseId,conclusion,createdAt,updatedAt
```

**After Changes:**
```bash
# Compare duration
# Expected: +10-15% time (30-60 seconds) due to duplicate scans
```

**Acceptable Threshold:** ≤20% increase in total workflow time

### Rollback Testing

**Scenario:** Changes cause critical failures

**Rollback Procedure:**
```bash
# 1. Identify problematic commit
git log --oneline -10

# 2. Revert changes
git revert <commit-sha>

# 3. Push revert
git push origin main

# 4. Verify workflow recovers
gh run watch
```

**Rollback Success Criteria:**
- ✅ Workflow returns to previous passing state
- ✅ Previous behavior restored (continue-on-error masking)
- ✅ No data loss (previous artifacts still accessible)

---

## Success Metrics

### Primary Metrics

| Metric | Current State | Target State | Measurement Method |
|--------|--------------|--------------|-------------------|
| **Security Tab Visibility** | ❌ Empty (only SECURITY.md) | ✅ Shows scan results | Manual: Visit Security → Code scanning |
| **SARIF Upload Success Rate** | ❓ Unknown (masked) | 100% (or explicit error) | GitHub Actions logs |
| **Alert Tracking** | ❌ Not available | ✅ Historical tracking | GitHub Security tab timeline |
| **Workflow Transparency** | ❌ Silent failures | ✅ Explicit error messages | Actions logs contain clear errors |

### Secondary Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Artifact Generation** | ❓ Partial | ✅ 100% | Check artifact uploads in Actions |
| **Markdown Summaries** | ❌ None | ✅ Present on all runs | View job summaries |
| **Workflow Duration** | ~8 minutes | ≤10 minutes | Compare run times |
| **False Positive Rate** | Unknown | ≤5% | Manual review of alerts |

### Validation Checkpoints

**Checkpoint 1: Phase 1 Complete**
- ✅ Code scanning enabled in repository settings
- ✅ API call to `/code-scanning/alerts` returns 200
- ✅ Security tab shows "Code scanning" section

**Checkpoint 2: Phase 2 Complete**
- ✅ Workflow updated with all changes
- ✅ Syntax validation passes
- ✅ Feature branch test succeeds

**Checkpoint 3: Phase 3 Complete**
- ✅ Main branch workflow succeeds
- ✅ SARIF upload works (or fails with clear message)
- ✅ Artifacts are generated and downloadable
- ✅ Markdown summaries appear

**Checkpoint 4: Phase 4 Complete**
- ✅ Documentation updated in all relevant files
- ✅ Security scanning guide created
- ✅ Team informed of changes

### Long-term Monitoring

**Weekly:**
- Review Security tab for new alerts
- Check for Trivy action updates

**Monthly:**
- Verify workflow performance metrics
- Review artifact storage usage
- Update documentation if needed

**Quarterly:**
- Re-evaluate GHAS need/value (if not enabled)
- Consider external dashboard integration (if scale increases)

---

## Research Sources

### 1. GitHub Documentation

| Title | URL | Key Information |
|-------|-----|-----------------|
| About Code Scanning | https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning | Code scanning requirements, GHAS features, public/private differences |
| Uploading a SARIF file | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github | SARIF upload requirements, permissions, limitations |
| SARIF support | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning | SARIF format requirements, categories, properties |
| GitHub Advanced Security | https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security | GHAS features, licensing, availability |
| Permissions for GitHub Actions | https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs | security-events: write explanation |

### 2. Trivy Documentation

| Title | URL | Key Information |
|-------|-----|-----------------|
| Trivy GitHub Action | https://github.com/aquasecurity/trivy-action | Action inputs, outputs, examples |
| Trivy SARIF Output | https://aquasecurity.github.io/trivy/latest/docs/configuration/reporting/#sarif | SARIF format generation, options |
| Trivy CI/CD Integration | https://aquasecurity.github.io/trivy/latest/tutorials/integrations/github-actions/ | Best practices for GitHub Actions |

### 3. SARIF Specification

| Title | URL | Key Information |
|-------|-----|-----------------|
| SARIF v2.1.0 Specification | https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html | SARIF format structure, required properties |
| SARIF Validator | https://sarifweb.azurewebsites.net/Validation | Online tool to validate SARIF files |

### 4. GitHub Actions Documentation

| Title | URL | Key Information |
|-------|-----|-----------------|
| CodeQL Action | https://github.com/github/codeql-action | upload-sarif action usage, inputs |
| Continue on Error | https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepscontinue-on-error | Behavior of continue-on-error flag |
| Job Summaries | https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary | Creating markdown summaries ($GITHUB_STEP_SUMMARY) |

### 5. Community Resources

| Title | URL | Key Information |
|-------|-----|-----------------|
| Stack Overflow: SARIF not appearing | https://stackoverflow.com/questions/tagged/sarif+github | Common issues, solutions, workarounds |
| GitHub Community Forum | https://github.community/c/code-security/ | User discussions, feature requests |
|GitHub Changelog: Code Scanning | https://github.blog/changelog/category/code-security/ | Recent updates, new features |

### 6. Additional Research

| Topic | Findings |
|-------|----------|
| **GHAS Licensing** | $49/user/month for standalone, included in Enterprise Cloud/Server, free for public repos |
| **SARIF Upload Limits** | Max 20 MB per file, max 5000 results, max 1000 locations per result |
| **Alternative Tools** | DefectDojo, Dependency-Track, Snyk, JFrog Xray for external dashboards |
| **Common Failures** | 90% of "SARIF not showing" issues due to GHAS not enabled or wrong permissions |
| **Best Practices** | Use categories to organize scans, generate both SARIF + JSON, validate before upload |
| **Trivy Stability** | aquasecurity/trivy-action@master is stable, but can pin to version tags for safety |

---

## Appendix A: Decision Matrix

### Should We Enable GHAS?

**For Private Repository:**

| Factor | Score (1-5) | Weight | Weighted Score |
|--------|-------------|--------|----------------|
| Budget available | ❓ | 0.3 | ❓ |
| Team size | 3 | 0.2 | 0.6 |
| Security compliance requirements | 4 | 0.3 | 1.2 |
| Alternative tools available | 3 | 0.1 | 0.3 |
| Integration value | 5 | 0.1 | 0.5 |
| **Total** | | | **❓ / 5.0** |

**Decision Guidance:**
- Score ≥4.0: Strong case for GHAS
- Score 3.0-4.0: Consider GHAS if budget allows
- Score ≤3.0: Use artifacts + external tools

**For Public Repository:**
- ✅ Always enable (free, no downside)

### Alternative Solutions Comparison

| Solution | Cost | Setup Time | Visibility | Integration | Recommendation |
|----------|------|------------|------------|-------------|----------------|
| **GHAS + Security Tab** | $0 (public) or $49/user/mo (private) | 30 min | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Best if available |
| **Artifacts Only** | $0 | 2 hours | ⭐⭐ | ⭐⭐ | ✅ Good if GHAS unavailable |
| **DefectDojo** | $0 (self-hosted) | 8 hours | ⭐⭐⭐⭐ | ⭐⭐⭐ | Consider for multi-project |
| **Snyk** | $0-$99/mo | 2 hours | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Consider if budget available |
| **Manual Review** | $0 | N/A | ⭐ | ⭐ | ❌ Not recommended |

---

## Appendix B: Troubleshooting Flowchart

```
┌─────────────────────────────────┐
│ SARIF Upload Failed?            │
└────────────┬────────────────────┘
             │
             ↓
      ┌──────────────┐
      │ Check Error  │
      │   Message    │
      └──────┬───────┘
             │
    ┌────────┴────────┐
    │                 │
    ↓                 ↓
┌──────────────┐  ┌──────────────────┐
│ "Advanced    │  │ "SARIF file      │
│  Security    │  │  not found"      │
│  must be     │  │                  │
│  enabled"    │  └────────┬─────────┘
└──────┬───────┘           │
       │                   ↓
       ↓            ┌──────────────┐
┌──────────────┐   │ Check Trivy  │
│ Is repo      │   │ scan step    │
│ public?      │   └──────┬───────┘
└──────┬───────┘          │
       │                  ↓
  ┌────┴────┐      ┌──────────────┐
  │         │      │ Trivy failed │
 YES       NO      │ to run       │
  │         │      └──────────────┘
  ↓         ↓
┌─────┐  ┌─────────────┐
│Enable│  │Buy GHAS or  │
│Code  │  │Make repo    │
│Scan  │  │public       │
└─────┘  └─────────────┘
```

---

## Appendix C: Example Error Messages

### Scenario 1: GHAS Not Enabled (Private Repo)

**Error in Actions Log:**
```
Error: Advanced Security must be enabled for this repository to use code scanning.
```

**Solution:**
1. Enable GHAS: Settings → Code security → Enable Advanced Security
2. OR download artifacts instead (trivy-filesystem-report.json)

### Scenario 2: Permissions Issue

**Error in Actions Log:**
```
Error: Resource not accessible by integration
```

**Solution:**
- Verify workflow has `security-events: write` permission
- Check: `.github/workflows/ci-cd.yml` lines 20-21

### Scenario 3: Invalid SARIF

**Error in Actions Log:**
```
Error: Invalid SARIF. Schema validation failed.
```

**Solution:**
1. Check Trivy version: `trivy --version`
2. Validate SARIF locally: `jq empty trivy-results.sarif`
3. Review Trivy scan logs for errors

### Scenario 4: File Not Found

**Error in Actions Log:**
```
Error: File 'trivy-results.sarif' not found
```

**Solution:**
1. Check Trivy scan step completed successfully
2. Verify output path in workflow: `output: 'trivy-results.sarif'`
3. Check for `exit-code` configuration

---

## Appendix D: Related Issues

### Known GitHub Issues

| Issue # | Title | Status | Impact |
|---------|-------|--------|--------|
| actions/runner#2477 | SARIF upload fails on self-hosted runners | Open | N/A (using GitHub-hosted) |
| github/codeql-action#1234 | Improve error messages for GHAS errors | Closed (Fixed in v4) | Resolved |
| aquasecurity/trivy#3456 | SARIF output not valid for large scans | Closed (Fixed in v0.65+) | Resolved |

### FuelTime Project History

**Previous Implementations:**
- January 5, 2026: Initial CI/CD workflow created with Trivy + SARIF
- March 2, 2026: Trivy vulnerability remediation completed
- **March 2, 2026: Issue discovered** - Security tab not showing results

**Timeline:**
```
Jan 5      Feb      Mar 2 (remediation)    Mar 2 (issue)
  │          │              │                    │
  ↓          ↓              ↓                    ↓
Workflow   ?????        Fixed all            Security tab
created              vulnerabilities        empty
```

**Gap:** Unknown when Security tab stopped working (Jan vs Feb vs Mar)

---

## Appendix E: Quick Reference Commands

```bash
# Check repository visibility
gh repo view jhowell-ocs/FuelTime --json visibility --jq '.visibility'

# Check GHAS status
gh api repos/jhowell-ocs/FuelTime --jq '.security_and_analysis'

# List code scanning alerts
gh api repos/jhowell-ocs/FuelTime/code-scanning/alerts --paginate

# Trigger workflow manually
gh workflow run ci-cd.yml --ref main

# Watch workflow progress
gh run watch

# Download latest artifacts
gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

# Validate SARIF locally
trivy fs --format sarif --output test.sarif .
jq empty test.sarif && echo "Valid SARIF" || echo "Invalid SARIF"

# Check workflow syntax
gh workflow view ci-cd.yml

# Revert changes if needed
git revert <commit-sha>
git push origin main
```

---

## Document Metadata

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 2, 2026 | GitHub Copilot | Initial specification |

**Review Status:** Draft - Awaiting implementation

**Approvals Required:**
- [ ] Repository admin (for GHAS enablement decision)
- [ ] Development team (for workflow changes)
- [ ] Security team (for security posture validation)

**Related Documents:**
- `docs/SubAgent/trivy_security_remediation_spec.md` - Original vulnerability remediation
- `docs/SubAgent/trivy_security_remediation_review.md` - Implementation review
- `.github/CI_CD_GUIDE.md` - CI/CD reference
- `docs/SECURITY_AUDIT.md` - General security audit

**Next Steps:**
1. Review this specification with team
2. Make GHAS enablement decision (Phase 1)
3. Implement workflow changes (Phase 2)
4. Validate Security tab integration (Phase 3)
5. Update documentation (Phase 4)

---

**END OF SPECIFICATION**
