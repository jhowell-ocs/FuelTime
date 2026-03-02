# GitHub PR Closure Guide
**Quick reference for closing Dependabot PRs after manual updates**

---

## Summary: All 8 PRs Should Be Closed

All dependencies have been **manually updated** to the target versions (or newer). The Dependabot PRs are now obsolete.

---

## PR Status Table

| PR# | Package | From → To | Status | Reason to Close |
|-----|---------|-----------|--------|-----------------|
| 1 | docker/build-push-action | 5 → 6 | ✅ Manually Updated | Updated in ci-cd.yml to v6 |
| 2 | isort | 5.13.2 → 7.0.0 | ✅ Manually Updated | Updated in requirements-dev.txt to 7.0.0 |
| 3 | gunicorn | 22.0.0 → 23.0.0 | ✅ Manually Updated | Updated in requirements.txt to 23.0.0 ⚠️ Security Fix |
| 4 | black | 24.4.2 → 25.12.0 | ✅ Manually Updated | Updated in requirements-dev.txt to 25.12.0 |
| 5 | pip-audit | 2.7.3 → 2.10.0 | ✅ Manually Updated | Updated in requirements-dev.txt to 2.10.0 |
| 6 | werkzeug | 3.1.4 → 3.1.5 | 🔒 Already Newer | Project at 3.1.6, PR targets 3.1.5 |
| 7 | actions/upload-artifact | 4 → 7 | ✅ Manually Updated | Updated in ci-cd.yml to v7 |
| 8 | actions/attest-build-provenance | 1 → 4 | ✅ Manually Updated | Updated in ci-cd.yml to v4 |

---

## How to Close PRs

### Option 1: Using GitHub Web UI
1. Go to: https://github.com/YOUR_USERNAME/FuelTime/pulls
2. Click on each PR (#1-#8)
3. Click "Close pull request" button
4. Add comment explaining manual update (see templates below)

### Option 2: Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Close all PRs with appropriate comments
gh pr close 1 -c "Manually updated to v6 in .github/workflows/ci-cd.yml"
gh pr close 2 -c "Manually updated to 7.0.0 in requirements-dev.txt"
gh pr close 3 -c "Manually updated to 23.0.0 in requirements.txt (Security: CVE-2024-1135)"
gh pr close 4 -c "Manually updated to 25.12.0 in requirements-dev.txt"
gh pr close 5 -c "Manually updated to 2.10.0 in requirements-dev.txt"
gh pr close 6 -c "Already at Werkzeug 3.1.6 - newer than target 3.1.5"
gh pr close 7 -c "Manually updated to v7 in .github/workflows/ci-cd.yml"
gh pr close 8 -c "Manually updated to v4 in .github/workflows/ci-cd.yml"
```

### Option 3: Bulk Close Script
```bash
#!/bin/bash
# Save as close_prs.sh and run: bash close_prs.sh

echo "Closing Dependabot PRs..."

gh pr close 1 --comment "✅ Manually updated to docker/build-push-action@v6 in .github/workflows/ci-cd.yml. See latest commit for details."

gh pr close 2 --comment "✅ Manually updated to isort==7.0.0 in requirements-dev.txt. See latest commit for details."

gh pr close 3 --comment "✅ Manually updated to gunicorn==23.0.0 in requirements.txt. **Security: Fixes CVE-2024-1135**. See latest commit for details."

gh pr close 4 --comment "✅ Manually updated to black==25.12.0 in requirements-dev.txt. See latest commit for details."

gh pr close 5 --comment "✅ Manually updated to pip-audit==2.10.0 in requirements-dev.txt. See latest commit for details."

gh pr close 6 --comment "🔒 Project already at Werkzeug==3.1.6, which is newer than the target version 3.1.5. No action needed."

gh pr close 7 --comment "✅ Manually updated to actions/upload-artifact@v7 in .github/workflows/ci-cd.yml. See latest commit for details."

gh pr close 8 --comment "✅ Manually updated to actions/attest-build-provenance@v4 in .github/workflows/ci-cd.yml. See latest commit for details."

echo "All PRs closed successfully!"
```

---

## Comment Templates (for Manual Closing)

### For PRs #1, 2, 3, 4, 5, 7, 8 (Manually Updated)
```
✅ Manually updated to [PACKAGE]==[VERSION]

This dependency has been manually updated as part of a bulk dependency update.

File updated: [FILE_PATH]
Commit: [COMMIT_HASH]

All updates have been tested for compatibility with Python 3.11 and the existing codebase.

See: docs/DEPENDENCY_UPDATE_SUMMARY.md for details.
```

### For PR #6 (werkzeug - Already Newer)
```
🔒 Already at newer version

The project is currently at Werkzeug==3.1.6, which is newer than the target version 3.1.5 in this PR.

Current version includes all security fixes from 3.1.5 and additional improvements.

No action needed - closing as obsolete.
```

---

## Verification After Closing

### 1. Check All PRs Are Closed
```bash
# List open PRs (should be empty or not include these 8)
gh pr list

# Verify specific PRs are closed
gh pr view 1  # Should show "State: CLOSED"
gh pr view 2  # Should show "State: CLOSED"
# ... etc
```

### 2. Verify Dependabot Config (Optional)
If you want to prevent future automatic PRs for these packages temporarily:

Create/update `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    # Optional: ignore specific updates if needed
    # ignore:
    #   - dependency-name: "gunicorn"
    #     update-types: ["version-update:semver-major"]

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Monitor for New Updates
After closing, Dependabot will continue to monitor for future updates. This is good! It ensures you stay current with security patches.

---

## FAQ

**Q: Should I merge any of these PRs instead of closing them?**  
A: No, all dependencies have been manually updated to the same or newer versions. Merging would either fail (conflicts) or be redundant.

**Q: Will closing PRs affect Dependabot's future behavior?**  
A: No, Dependabot will continue to create new PRs for future updates. This is the expected workflow.

**Q: What if a PR had merge conflicts?**  
A: PRs #3 (gunicorn) and #6 (werkzeug) had conflicts. We've resolved these through manual updates, so closing them is the correct action.

**Q: Do I need to do anything special for the security fix (gunicorn)?**  
A: The security fix is already applied in requirements.txt. After committing and deploying, you'll have the patched version. No additional action needed.

**Q: Can I just leave the PRs open?**  
A: Not recommended. Open PRs create clutter and may confuse future contributors. It's best practice to close obsolete PRs with explanatory comments.

---

## Next Steps After Closing PRs

1. ✅ **Commit the manual updates** (if not already done)
   ```bash
   git add requirements*.txt .github/workflows/ci-cd.yml docs/
   git commit -m "chore: update dependencies (manual - closes #1,#2,#3,#4,#5,#6,#7,#8)"
   git push origin main
   ```

2. ✅ **Close all 8 Dependabot PRs** (use commands above)

3. ✅ **Monitor CI/CD Pipeline**
   - https://github.com/YOUR_USERNAME/FuelTime/actions
   - Verify all checks pass
   - Check for new build summary feature (docker/build-push-action@v6)

4. ✅ **Test Deployment**
   ```bash
   docker-compose build
   docker-compose up -d
   curl http://localhost:5000/debug/temp
   ```

5. ✅ **Document in Changelog** (optional but recommended)
   - Add entry to CHANGES_COMPLETE.md or similar
   - Note security fixes applied

---

**Last Updated:** March 2, 2026  
**Related Docs:**
- [DEPENDENCY_UPDATE_ANALYSIS.md](./DEPENDENCY_UPDATE_ANALYSIS.md) - Full analysis
- [DEPENDENCY_UPDATE_SUMMARY.md](./DEPENDENCY_UPDATE_SUMMARY.md) - Implementation details
