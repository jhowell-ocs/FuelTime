# Specification: Timesheet PDF — Time Format & Signature Placement Fix

**Feature:** `timesheet_time_format_signature_fix`
**Date:** 2026-04-02
**Status:** DRAFT

---

## 1. Overview

Two bugs exist in the Timesheet PDF generation flow:

| # | Bug | Symptom |
|---|-----|---------|
| 1 | **Time format** | PDF shows times in 24-hour format (e.g., `16:00`) instead of 12-hour with AM/PM (e.g., `04:00 PM`) |
| 2 | **Signature placement** | Uploaded/drawn signature image appears **on top of** the signature line instead of **above** it |

---

## 2. Current State Analysis

### 2.1 Time Format Bug

#### Data Collection — `templates/fuel_form.html`

All time cells in the timesheet table use native HTML time inputs:

```html
<input type="time" class="time-input" name="time_in_1_m1" onchange="calculateHours(this)">
```

**Critical fact:** The HTML `<input type="time">` element **always returns its `.value` in `HH:MM` 24-hour format** (per the HTML Living Standard), regardless of the locale or how the browser's UI displays it to the user. A user who sees "4:00 PM" in their browser's time picker will produce the string `"16:00"` when `.value` is read.

#### Data Serialisation — `downloadTimesheetPDF()` in `fuel_form.html` (~line 1607)

```javascript
const inputs = document.querySelectorAll('#timesheet-body input');
inputs.forEach(input => {
    if (input.name) {
        formData[input.name] = input.value || '';   // ← raw 24-hour string stored here
    }
});
```

No conversion is applied. The raw `"16:00"` value is stored directly in `formData`.

#### Server Route — `app.py` `/preview-timesheet-pdf` (~line 628)

```python
for key, value in form_data.items():
    timesheet_data[key] = value     # ← copied verbatim, no formatting
```

No time-format transformation exists. The raw strings flow straight through to template rendering.

#### Template Rendering — `templates/timesheet_pdf_template.html` (~line 322)

```html
<td class="time-column">{{ form_data.get('time_in_1_m1', '') }}</td>
```

Values rendered with a plain `{{ }}` expression — no Jinja2 filter is applied. The 24-hour string is printed literally into the PDF.

#### Root Cause

The entire pipeline — HTML input → JS serialisation → Flask route → Jinja2 template — passes time strings as-is. There is **no conversion step** from `HH:MM` (24-hour) to `HH:MM AM/PM` (12-hour) anywhere. The browser UI may display times in 12-hour format visually, but `.value` always yields 24-hour.

---

### 2.2 Signature Placement Bug

#### CSS — `templates/timesheet_pdf_template.html` (~lines 172–190)

```css
.signature-line {
    border-bottom: 1px solid black;
    margin-top: 5px;
    height: 25px;
    position: relative;
}

.signature-image {
    max-width: 150px;
    max-height: 45px;
    margin-bottom: 1px;
    margin-left: 120px;
}
```

The "line" is rendered as the **bottom border** of `.signature-line`. The div has a `height: 25px`, so any content placed inside spans that same 25 px area.

#### HTML — `templates/timesheet_pdf_template.html` (~lines 388–400)

```html
<div class="signature-section">
    <div class="signature-label">Employee Signature</div>
    <div class="signature-line">
        {% if form_data.get('employee_signature') %}
            <img src="{{ form_data.get('employee_signature') }}" alt="Employee Signature" class="signature-image">
        {% endif %}
    </div>
</div>
```

The `<img>` is nested **inside** `.signature-line`. Its content flows on top of the border-bottom in normal document flow. The image renders within the box that also carries the bottom-border line, making it appear as if the signature is drawn **on** or **over** the line rather than above it.

#### Root Cause

The signature image `<img>` is a child of the same element (`div.signature-line`) whose `border-bottom` creates the signature line. Normal block-flow places the image inside the box and the border paints at the very bottom of that same box, so the image obscures or overlaps the line. The image must be **outside and above** `.signature-line`.

---

## 3. Proposed Solutions

### 3.1 Fix 1 — Time Format (JavaScript, client-side)

**Chosen layer:** JavaScript in `fuel_form.html`, inside `downloadTimesheetPDF()`.

**Rationale:** The conversion is simplest at the point of serialisation, requires no changes to `app.py` or the Jinja2 template, introduces no new Python dependencies, and keeps the server-side code responsible only for layout.

#### Helper function to add (immediately before `downloadTimesheetPDF`):

```javascript
function formatTimeTo12Hour(timeStr) {
    if (!timeStr) return '';
    const parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    const hours = parseInt(parts[0], 10);
    const minutes = parts[1];
    if (isNaN(hours)) return timeStr;
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours % 12 || 12;
    return `${hour12.toString().padStart(2, '0')}:${minutes} ${ampm}`;
}
```

#### Conversion block to add inside `downloadTimesheetPDF()`, after all inputs are collected and before the `fetch()` call:

```javascript
// Convert time fields from 24-hour to 12-hour AM/PM format for PDF display
Object.keys(formData).forEach(key => {
    if (key.startsWith('time_in_') || key.startsWith('time_out_')) {
        formData[key] = formatTimeTo12Hour(formData[key]);
    }
});
```

**Exact insertion point:** After the block that collects `total_days` into `formData.total_days` and the debug `console.log` calls, and **before** the `fetch('/preview-timesheet-pdf', ...)` call.

---

### 3.2 Fix 2 — Signature Placement (HTML + CSS, `timesheet_pdf_template.html`)

**Chosen approach:** Move `<img>` **outside and above** `.signature-line`; reduce `.signature-line` to a thin black border-bottom only.

#### Updated HTML structure (both Employee and Supervisor sections):

```html
<!-- BEFORE (buggy) -->
<div class="signature-section">
    <div class="signature-label">Employee Signature</div>
    <div class="signature-line">
        {% if form_data.get('employee_signature') %}
            <img src="{{ form_data.get('employee_signature') }}" alt="Employee Signature" class="signature-image">
        {% endif %}
    </div>
</div>

<!-- AFTER (fixed) -->
<div class="signature-section">
    <div class="signature-label">Employee Signature</div>
    {% if form_data.get('employee_signature') %}
        <img src="{{ form_data.get('employee_signature') }}" alt="Employee Signature" class="signature-image">
    {% endif %}
    <div class="signature-line"></div>
</div>
```

Apply the same change to the Supervisor Signature section directly below it.

#### Updated CSS for `.signature-line` and `.signature-image`:

```css
/* REPLACE existing .signature-line */
.signature-line {
    border-bottom: 1px solid black;
    margin-top: 2px;
    height: 2px;
}

/* REPLACE existing .signature-image */
.signature-image {
    display: block;
    max-width: 150px;
    max-height: 40px;
    margin-bottom: 0;
    margin-left: 10px;
}
```

**Why these values:**
- `.signature-line` `height: 2px` collapses the div to a thin line — it no longer acts as a content container.
- `.signature-image` `display: block` ensures it occupies its own line above the border.
- `margin-left: 10px` gives a small left indent (signature naturally drifts right of the label).
- `margin-bottom: 0` removes the gap between image bottom and the line.

---

## 4. Implementation Steps

### Step 1 — `templates/fuel_form.html`

1. Locate the `downloadTimesheetPDF` function (search for `function downloadTimesheetPDF`).
2. Immediately **before** `function downloadTimesheetPDF`, add the `formatTimeTo12Hour` helper function (exact code in §3.1).
3. Inside `downloadTimesheetPDF`, locate the block that begins:
   ```javascript
   // Debug: Log the form data being sent to server:
   console.log('Debug: Form data being sent to server:', formData);
   ```
4. Insert the time-conversion block (exact code in §3.1) **immediately before** that debug `console.log` line.

### Step 2 — `templates/timesheet_pdf_template.html` — CSS

1. Locate `.signature-line` CSS rule (currently `height: 25px; position: relative;`).
2. Replace the entire `.signature-line` rule with the new version from §3.2.
3. Locate `.signature-image` CSS rule (currently `margin-left: 120px`).
4. Replace the entire `.signature-image` rule with the new version from §3.2.

### Step 3 — `templates/timesheet_pdf_template.html` — HTML (Employee Signature)

1. Locate the HTML block:
   ```html
   <div class="signature-line">
       {% if form_data.get('employee_signature') %}
           <img src="{{ form_data.get('employee_signature') }}" alt="Employee Signature" class="signature-image">
       {% endif %}
   </div>
   ```
2. Replace with:
   ```html
   {% if form_data.get('employee_signature') %}
       <img src="{{ form_data.get('employee_signature') }}" alt="Employee Signature" class="signature-image">
   {% endif %}
   <div class="signature-line"></div>
   ```

### Step 4 — `templates/timesheet_pdf_template.html` — HTML (Supervisor Signature)

1. Locate the identical structure for Supervisor Signature immediately below the Employee block.
2. Apply the same change as Step 3, replacing `employee_signature` → `supervisor_signature` and alt text accordingly.

---

## 5. Files to Modify

| File | Changes |
|------|---------|
| `templates/fuel_form.html` | Add `formatTimeTo12Hour()` helper; add time-conversion loop in `downloadTimesheetPDF()` |
| `templates/timesheet_pdf_template.html` | Update `.signature-line` CSS; update `.signature-image` CSS; restructure both signature HTML blocks |

**`app.py` — NO CHANGES REQUIRED.** The time strings arrive pre-formatted; the server is format-agnostic.

---

## 6. Dependencies

- No new Python packages required.
- No Jinja2 custom filters required.
- No changes to Docker configuration, Dockerfile, or `requirements.txt`.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Browser `<input type="time">` returns `""` for empty cells; `formatTimeTo12Hour("")` must return `""` | Low — already handled by `if (!timeStr) return '';` guard | Covered by the helper |
| Minutes field contains seconds in some browsers (e.g., `"16:00:00"`) | Low — modern browsers emit `HH:MM` only for time inputs | Helper uses `parts[1]` which takes only the minutes segment; seconds would be silently ignored |
| `margin-left: 10px` on `.signature-image` may not align appropriately for very long or short signatures | Low | Value is cosmetic; implementation agent may adjust to taste; no functional impact |
| wkhtmltopdf renders `display: block` on `<img>` differently from full browsers | Low — wkhtmltopdf respects `display: block` | Test by running the container smoke test after change |
| `formatTimeTo12Hour` called on auto-fill values already in 24h (from `start-time`, `lunch-out`, etc.) | Certain — this is intended | The function handles all `time_in_*` / `time_out_*` keys, including auto-filled ones |
| If a time value is already empty (`""`) when auto-fill was not used for a day | Certain — empty rows exist | `if (!timeStr) return '';` guard returns empty string unchanged — PDF cell stays blank |

---

## 8. Acceptance Criteria

1. When "Download Timesheet PDF" is clicked with a time value of `16:00` entered, the PDF renders `04:00 PM`.
2. When a time value of `08:30` is entered, the PDF renders `08:30 AM`.
3. When a time value of `12:00` is entered, the PDF renders `12:00 PM`.
4. When `00:00` is entered, the PDF renders `12:00 AM`.
5. When a user uploads a signature image and downloads the PDF, the signature appears **above** the signature line, not overlapping or obscuring it.
6. When no signature is provided, the signature line renders as a plain black horizontal rule with blank space above it.
7. All CI quality gates pass: `black --check`, `isort --check-only`, `flake8 --select=E9,F63,F7,F82`, `pylint --fail-under=7.0`, `bandit`, `pip-audit`, Docker build, and `/debug/temp` health check.
