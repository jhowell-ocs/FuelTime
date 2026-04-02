#!/bin/bash
# FuelTime Preflight Validation
# Mirrors the security-scan and docker-build-test jobs in .github/workflows/ci-cd.yml
# Exit non-zero immediately on any failure.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

PASS="[PASS]"
FAIL="[FAIL]"

print_header() {
    echo ""
    echo "============================================="
    echo " FuelTime Preflight Validation"
    echo " $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================="
    echo ""
}

# Ensure docker compose down runs on exit (success or failure)
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "${FAIL} Preflight failed. Cleaning up containers..."
    fi
    docker compose down 2>/dev/null || true
    exit $exit_code
}
trap cleanup EXIT

print_header

# --- Step 1: Install dev dependencies ---
echo "[1/9] Installing dev dependencies..."
pip install -r requirements-dev.txt
echo "${PASS} [1/9] Dev dependencies installed."
echo ""

# --- Step 2: Black ---
echo "[2/9] Running Black (code formatting check, line-length 120)..."
black --check --diff .
echo "${PASS} [2/9] Black formatting check passed."
echo ""

# --- Step 3: isort ---
echo "[3/9] Running isort (import sort check)..."
isort --check-only --diff .
echo "${PASS} [3/9] isort check passed."
echo ""

# --- Step 4: Flake8 ---
echo "[4/9] Running Flake8 (critical lint errors: E9, F63, F7, F82)..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
echo "${PASS} [4/9] Flake8 critical lint check passed."
echo ""

# --- Step 5: Pylint ---
echo "[5/9] Running Pylint (static analysis, minimum score 7.0)..."
pylint app.py --fail-under=7.0
echo "${PASS} [5/9] Pylint analysis passed."
echo ""

# --- Step 6: Bandit (informational only, mirrors CI) ---
echo "[6/9] Running Bandit (Python security scanner — informational)..."
bandit -r . -f txt || true
echo "${PASS} [6/9] Bandit security scan completed (informational)."
echo ""

# --- Step 7: pip-audit ---
echo "[7/9] Running pip-audit (dependency vulnerability audit)..."
pip-audit -r requirements.txt
echo "${PASS} [7/9] pip-audit dependency audit passed."
echo ""

# --- Step 8: Docker image build ---
echo "[8/9] Building Docker image (no-cache)..."
docker compose build --no-cache
echo "${PASS} [8/9] Docker image build passed."
echo ""

# --- Step 9: Container smoke test ---
echo "[9/9] Running container smoke test..."
docker compose up -d
echo "  Waiting 30 seconds for container startup..."
sleep 30
echo "  Hitting health endpoint: http://localhost:5000/debug/temp"
curl -f http://localhost:5000/debug/temp
echo ""
echo "${PASS} [9/9] Container smoke test passed."
echo ""

echo "============================================="
echo " All preflight checks PASSED."
echo " Code is ready to push to GitHub."
echo "============================================="
echo ""
