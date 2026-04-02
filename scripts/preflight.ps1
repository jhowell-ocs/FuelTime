# FuelTime Preflight Validation
# Mirrors the security-scan and docker-build-test jobs in .github/workflows/ci-cd.yml
# Exits non-zero immediately on any failure.

$ErrorActionPreference = 'Stop'

# Navigate to project root (one level up from scripts/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir '..')

function Write-Step {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Pass {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
    Write-Host ""
}

function Write-Fail {
    param([string]$Message, [int]$Code)
    Write-Host "[FAIL] $Message (exit code $Code)" -ForegroundColor Red
}

function Assert-ExitCode {
    param([string]$Step, [int]$StepNum, [int]$Total)
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "[$StepNum/$Total] $Step" $LASTEXITCODE
        Write-Host "Cleaning up containers..." -ForegroundColor Yellow
        docker compose down 2>$null
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " FuelTime Preflight Validation"             -ForegroundColor Cyan
Write-Host " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Install dev dependencies ---
Write-Step "[1/9] Installing dev dependencies..."
pip install -r requirements-dev.txt
Assert-ExitCode "Install dev dependencies" 1 9
Write-Pass "[1/9] Dev dependencies installed."

# --- Step 2: Black ---
Write-Step "[2/9] Running Black (code formatting check, line-length 120)..."
black --check --diff .
Assert-ExitCode "Black formatting check" 2 9
Write-Pass "[2/9] Black formatting check passed."

# --- Step 3: isort ---
Write-Step "[3/9] Running isort (import sort check)..."
isort --check-only --diff .
Assert-ExitCode "isort check" 3 9
Write-Pass "[3/9] isort check passed."

# --- Step 4: Flake8 ---
Write-Step "[4/9] Running Flake8 (critical lint errors: E9, F63, F7, F82)..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
Assert-ExitCode "Flake8 critical lint check" 4 9
Write-Pass "[4/9] Flake8 critical lint check passed."

# --- Step 5: Pylint ---
Write-Step "[5/9] Running Pylint (static analysis, minimum score 7.0)..."
pylint app.py --fail-under=7.0
Assert-ExitCode "Pylint analysis" 5 9
Write-Pass "[5/9] Pylint analysis passed."

# --- Step 6: Bandit (informational only, mirrors CI) ---
Write-Step "[6/9] Running Bandit (Python security scanner — informational)..."
bandit -r . -f txt
# Bandit is informational in CI (runs with || true); do not Assert-ExitCode here
Write-Pass "[6/9] Bandit security scan completed (informational)."

# --- Step 7: pip-audit ---
Write-Step "[7/9] Running pip-audit (dependency vulnerability audit)..."
pip-audit -r requirements.txt
Assert-ExitCode "pip-audit dependency audit" 7 9
Write-Pass "[7/9] pip-audit dependency audit passed."

# --- Step 8: Docker image build ---
Write-Step "[8/9] Building Docker image (no-cache)..."
docker compose build --no-cache
Assert-ExitCode "Docker image build" 8 9
Write-Pass "[8/9] Docker image build passed."

# --- Step 9: Container smoke test ---
Write-Step "[9/9] Running container smoke test..."
try {
    docker compose up -d
    Assert-ExitCode "docker compose up" 9 9

    Write-Host "  Waiting 30 seconds for container startup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30

    Write-Host "  Hitting health endpoint: http://localhost:5000/debug/temp" -ForegroundColor Yellow
    curl.exe -f http://localhost:5000/debug/temp
    Assert-ExitCode "Container smoke test (curl health check)" 9 9
}
finally {
    Write-Host "  Stopping containers..." -ForegroundColor Yellow
    docker compose down
}
Write-Pass "[9/9] Container smoke test passed."

Write-Host "=============================================" -ForegroundColor Green
Write-Host " All preflight checks PASSED."              -ForegroundColor Green
Write-Host " Code is ready to push to GitHub."          -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
