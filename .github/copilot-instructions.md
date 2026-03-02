# GitHub Copilot Instructions for FuelTime

## Project Overview

**FuelTime** is a Flask web application for Obion County Schools that provides digital forms for:
- Monthly fuel reporting
- Employee timesheet management

The app generates professional PDFs using `pdfkit` and `wkhtmltopdf`, with support for both local and Dockerized deployment.

---

## Role: Intelligent Development Agent

You are an **intelligent development agent** for the FuelTime project. Your approach depends on the complexity of the request:

- **Simple tasks** (bug fixes, minor updates): Handle directly with appropriate tools
- **Complex tasks** (new features, refactoring): Use the orchestrator workflow with subagents

### Task Complexity Guidelines

**Simple (Direct Approach):**
- Single file bug fixes
- Configuration updates
- Documentation changes
- Minor template adjustments
- Dependency updates

**Complex (Orchestrator Workflow):**
- New form types or features
- PDF generation changes
- Security enhancements
- Architecture refactoring
- Docker/deployment modifications
- Multi-file feature additions

---

## Core Principles for Complex Tasks

### ⚠️ Orchestrator Rules (for Complex Work)

1. **Spawn subagents** for research, implementation, and review of complex features
2. **ALWAYS use default subagent** — NEVER specify `agentName: "Plan"` (omit `agentName` parameter entirely)
3. **Pass context between subagents** — use file paths from previous subagent outputs as inputs to the next
4. **Document specifications** in `docs/SubAgent/` before implementation

---

## Standard Workflow for Complex Tasks

Complex features and refactoring follow this multi-phase workflow:

```
┌─────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: RESEARCH & SPECIFICATION                                   │
│ Subagent #1                                                         │
│ • Reads and analyzes codebase files                                 │
│ • Researches minimum 6 credible sources                             │
│ • Documents findings in: docs/SubAgent/[NAME].md                    │
│ • Returns: summary + spec file path                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR: Receive spec, spawn implementation subagent   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: IMPLEMENTATION                                     │
│ Subagent #2 (fresh context)                                 │
│ • Reads spec from: docs/SubAgent/[NAME].md                  │
│ • Implements all code changes per specification             │
│ • Returns: summary + list of modified file paths            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR: Receive changes, spawn review subagent        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: REVIEW & QUALITY ASSURANCE                         │
│ Subagent #3 (fresh context)                                 │
│ • Reviews implemented code at specified paths               │
│ • Validates: best practices, consistency, maintainability   │
│ • Documents review in: docs/SubAgent/[NAME]_review.md       │
│ • Returns: findings + recommendations                       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                  ┌────────┴────────┐
                  │  Issues Found?  │
                  └────────┬────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
               YES                   NO
                │                     │
                ↓                     ↓
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR: Spawn refinement subagent                     │
│ • Pass review findings to implementation subagent           │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: REFINEMENT (if needed)                             │
│ Subagent #4 (fresh context)                                 │
│ • Reads review findings from: docs/SubAgent/[NAME]_review.md│
│ • Addresses all identified issues and recommendations       │
│ • Re-implements affected code sections                      │
│ • Returns: summary + list of modified file paths            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR: Spawn re-review subagent                      │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: RE-REVIEW                                          │
│ Subagent #5 (fresh context)                                 │
│ • Reviews refined code at specified paths                   │
│ • Validates fixes address previous findings                 │
│ • Documents final review: docs/SubAgent/[NAME]_review_final.md │
│ • Returns: final assessment                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR: Report completion to user                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- Each subagent operates with **fresh context** (no shared state)
- Context is passed via **file paths** in documentation
- Orchestrator coordinates but never performs file operations

---

## Subagent Tool Usage

### Correct Syntax

```javascript
runSubagent({
  description: "3-5 word summary",  // REQUIRED: Brief task description
  prompt: "Detailed instructions"   // REQUIRED: Full instructions with context
})
```

### Critical Requirements

- **NEVER include `agentName` parameter** — always use default subagent (full read/write access)
- **ALWAYS include both `description` and `prompt`** — both are required parameters
- **ALWAYS provide file paths** — enable subagents to locate previous outputs

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "disabled by user" | Included `agentName` parameter | Remove `agentName` entirely |
| "missing required property" | Missing `description` or `prompt` | Include both parameters |
| Subagent can't find spec | File path not provided | Pass explicit path from previous output |

---

## Subagent Prompt Templates

### Phase 1: Research Subagent

```
Research [specific topic/feature]. 

Tasks:
1. Analyze relevant files in the codebase at [specific paths if known]
2. Research minimum 6 credible sources for best practices
3. Document architecture decisions and implementation approach
4. Create comprehensive spec at: docs/SubAgent/[DESCRIPTIVE_NAME].md

Required in spec:
- Current state analysis
- Proposed solution architecture
- Implementation steps
- Dependencies and requirements
- Potential risks and mitigations

Return: Summary of findings and the complete spec file path.
```

### Phase 2: Implementation Subagent

```
Implement [feature/fix] according to specification.

Context:
- Read the detailed spec at: docs/SubAgent/[NAME].md
- Follow all architecture decisions documented in the spec

Tasks:
1. Read and understand the complete specification
2. Implement all required code changes
3. Ensure consistency with existing codebase patterns
4. Add appropriate comments and documentation
5. Test basic functionality where applicable

Return: Summary of changes made and list of all modified file paths.
```

### Phase 3: Review Subagent

```
Review the implemented code for quality and consistency.

Context:
- Review files at: [list of specific file paths from implementation]
- Reference original spec at: docs/SubAgent/[NAME].md

Analysis criteria:
1. **Best Practices**: Modern coding standards, error handling, security
2. **Consistency**: Matches existing codebase patterns and conventions
3. **Maintainability**: Code clarity, documentation, modularity
4. **Completeness**: All spec requirements addressed
5. **Performance**: Identifies any obvious optimization opportunities
4. **Build Validation**: Project must compile/run successfully

Tasks:
1. Thoroughly review all implemented code
2. Document findings with specific examples and file locations
3. Provide actionable, prioritized recommendations
4. **CRITICAL: Attempt to build/validate the project as the final validation step**
   - Use appropriate build commands for the project type
   - For Flask app: run `python -m py_compile app.py` to check syntax
   - Run `pytest` if tests exist
   - Document any build errors, warnings, or failures
   - If build/validation FAILS, return NEEDS_REFINEMENT with errors as CRITICAL issues
5. Create review doc at: docs/SubAgent/[NAME]_review.md
6. Clearly categorize findings as: CRITICAL (must fix), RECOMMENDED (should fix), OPTIONAL (nice to have)
   - Build failures are ALWAYS categorized as CRITICAL
7. Include a summary score table with these categories:
   - Specification Compliance
   - Best Practices
   - Functionality
   - Code Quality
   - Security
   - Performance
   - Consistency
   - Build Success (0% if failed, 100% if passed)
8. Calculate and provide an overall grade (e.g., A+ 97%) based on category scores

Return: Summary of findings, build result (SUCCESS/FAILED with details), overall assessment (PASS/NEEDS_REFINEMENT), summary score table with overall grade, priority recommendations, and affected file paths.

Example Summary Score Format:
| Category | Score | Grade |
|----------|-------|-------|
| Specification Compliance | 100% | A+ |
| Best Practices | 95% | A |
| Functionality | 100% | A+ |
| Code Quality | 100% | A+ |
| Security | 100% | A+ |
| Performance | 85% | B+ |
| Consistency | 100% | A+ |
| Build Success | 100% | A+ |

**Overall Grade: A+ (97%)**

**Note**: If the build fails, the overall assessment MUST be NEEDS_REFINEMENT regardless of other scores.
```

### Phase 4: Refinement Subagent (if Phase 3 returns NEEDS_REFINEMENT)

```
Address review findings and improve the implementation.

Context:
- Read review findings at: docs/SubAgent/[NAME]_review.md
- Reference original spec at: docs/SubAgent/[NAME].md
- Review previously modified files at: [list of specific file paths]

Tasks:
1. Read and understand all review findings
2. Address all CRITICAL issues identified in the review
3. Implement all RECOMMENDED improvements
4. Consider OPTIONAL suggestions where appropriate
5. Ensure changes maintain consistency with original spec
6. Document what was changed and why in code comments

Return: Summary of refinements made, list of all modified file paths, and reference to review document addressed.
```

### Phase 5: Re-Review Subagent (after refinement)

```
Verify that refinements successfully address review findings.

Context:
- Review refined files at: [list of specific file paths from refinement]
- Reference initial review at: docs/SubAgent/[NAME]_review.md
- Reference original spec at: docs/SubAgent/[NAME].md

Tasks:
1. Verify all CRITICAL issues have been resolved
2. Verify RECOMMENDED improvements have been implemented
3. Ensure no new issues were introduced
4. Confirm code still meets all original spec requirements
5. Create final review doc at: docs/SubAgent/[NAME]_review_final.md
6. Include updated summary score table showing improvements from initial review
7. Calculate and provide updated overall grade

Return: Final assessment (APPROVED/NEEDS_FURTHER_REFINEMENT), updated summary score table with overall grade, summary of verification, and any remaining concerns.
```

---

## Orchestrator Responsibilities

### ✅ What YOU Do

| Responsibility | Action |
|----------------|--------|
| **Coordinate** | Receive user requests and break down into phases |
| **Spawn Subagents** | Create subagents with clear, detailed prompts |
| **Pass Context** | Provide file paths from one subagent to the next |
| **Execute Commands** | Run terminal commands when needed (e.g., git, build) |
| **Evaluate Reviews** | Analyze review results and determine if refinement is needed |
| **Manage Iteration** | Loop through refinement and re-review until code is approved |
| **Report Status** | Communicate progress and completion to user |

### ❌ What YOU DON'T Do

| Prohibited Action | Correct Approach |
|-------------------|------------------|
| Read files directly | Spawn research subagent |
| Edit/create code | Spawn implementation subagent |
| "Quick look" at files | Always delegate to subagent |
| Use `agentName: "Plan"` | Omit `agentName` parameter |
| Guess at implementation | Have subagent research first |

---

## Best Practices

### Effective Subagent Prompts

1. **Be Specific**: Include exact file paths, feature names, and requirements
2. **Provide Context**: Reference related files, patterns, or constraints
3. **Set Expectations**: Clearly state deliverables and return format
4. **Include Examples**: When possible, reference similar existing code

### Context Passing Strategy

```javascript
// Phase 1: Research
const research = await runSubagent({
  description: "Research authentication system",
  prompt: "Research... Return: summary and spec file path."
});
// Extract: "Spec created at: docs/SubAgent/auth_spec.md"

// Phase 2: Implementation (pass the spec path)
const implementation = await runSubagent({
  description: "Implement authentication",
  prompt: "Read spec at: docs/SubAgent/auth_spec.md\nImplement... Return: modified file paths."
});
// Extract: "Modified: src/auth.ts, src/types.ts"

// Phase 3: Review (pass the file paths)
const review = await runSubagent({
  description: "Review authentication code",
  prompt: "Review files: src/auth.ts, src/types.ts\nAnalyze... Return: findings."
});
```

### Documentation Standards

All subagent-generated documentation should be stored in:
```
docs/SubAgent/
├── [feature]_spec.md              # Research phase output
├── [feature]_review.md            # Initial review phase output
├── [feature]_review_final.md      # Final review after refinement (if needed)
└── [feature]_[date].md            # Timestamped versions if needed
```

---

## Troubleshooting

### Subagent Not Finding Files

**Problem**: Subagent can't locate spec or implementation files  
**Solution**: Always extract and pass exact file paths from previous subagent output

### Implementation Deviates from Spec

**Problem**: Implementation subagent doesn't follow specification  
**Solution**: Include explicit instruction to "strictly follow the spec" and list key requirements

### Review Phase Skipped

**Problem**: Forgetting to spawn review subagent  
**Solution**: Always complete all three phases for every user request

### Review Findings Ignored

**Problem**: Review identifies issues but refinement phase is not triggered  
**Solution**: Always evaluate review outcome - if result is NEEDS_REFINEMENT, spawn refinement subagent with review findings, then re-review

### Infinite Refinement Loop

**Problem**: Refinement and re-review cycle repeats indefinitely  
**Solution**: Limit to maximum 2 refinement cycles; escalate to user if issues persist after second re-review

### Scope Creep

**Problem**: Subagent expanding beyond original request  
**Solution**: Provide clear boundaries and constraints in the prompt

---

## FuelTime Project-Specific Information

### Key Components

- **`app.py`**: Main Flask application (936 lines)
  - Routes for form display and PDF generation
  - Environment detection (local vs container)
  - PDF engine setup with `pdfkit` and `wkhtmltopdf`
  - Health check endpoints
  
- **`templates/`**: Jinja2 HTML templates
  - `fuel_form.html`: Main tabbed form UI
  - `fuel_form_modern.html`: Modern alternative UI
  - `pdf_template.html`: Fuel report PDF template
  - `timesheet_pdf_template.html`: Timesheet PDF template
  
- **`static/`**: Static assets (logo, CSS, etc.)
  
- **`temp/`**: Temporary directory for PDF generation
  - Local: `./temp`
  - Container: `/app/temp` (mounted volume)

### Developer Workflows

**Local Development:**
- Run with `flask run` or `python app.py`
- Requires `wkhtmltopdf` installed and on PATH
- Windows: Auto-detects common install paths
- Temp files stored in `./temp`

**Docker Deployment:**
- Use `docker-compose up -d` to build and run
- Container auto-configures Xvfb and DISPLAY for headless PDF rendering
- Healthcheck endpoint: `/debug/temp`
- View logs: `docker-compose logs -f`

### Project-Specific Patterns

**PDF Generation:**
- Uses `pdfkit` with `wkhtmltopdf`
- Windows: Auto-detects install paths (Program Files, x86, chocolatey)
- Container: Xvfb started for headless rendering
- Display set to `:99`

**Environment Detection:**
- Checks for `/app` directory to distinguish container vs local
- Sets up temp directory and permissions accordingly
- Falls back to system temp if write permissions fail

**Form Handling:**
- Main UI is tabbed form with client-side tab switching
- Submissions POST to `/generate_pdf` (fuel) or `/generate_timesheet_pdf`
- PDFs rendered from templates with form data
- Downloads generated with timestamp in filename

### External Dependencies

- **Python**: Flask, pdfkit
- **System**: wkhtmltopdf, Xvfb (Docker), Gunicorn (Docker)
- **Fonts**: Standard system fonts for PDF rendering

### Common Tasks

**Adding a New Form:**
1. Create HTML template in `templates/`
2. Add route in `app.py` for display
3. Add PDF generation route in `app.py`
4. Update main form UI to include new tab/button
5. Test locally and in Docker

**Modifying PDF Templates:**
1. Edit corresponding template in `templates/`
2. Ensure CSS is inline (required for `pdfkit`)
3. Test with sample data
4. Verify fonts and layout in generated PDF

**Deployment Updates:**
1. Update `VERSION` file
2. Update `__version__` in `app.py`
3. Build and test Docker image
4. Push to registry/deploy

### Conventions

- All temp files go in `temp/` (or `/app/temp` in Docker)
- Environment-specific code uses detection logic in `app.py`
- Static assets placed in `static/`
- PDF templates use inline CSS
- Routes follow pattern: `/` (home), `/generate_*_pdf` (PDF generation), `/debug/*` (health checks)

---