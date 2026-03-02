# Fuel PDF Formatting Fix Specification

**Date:** March 2, 2026  
**Task:** Fix vertical/rotated column headers in fuel sheet PDF template  
**Template Path:** `templates/pdf_template.html`

---

## 1. Current State Analysis

### What's Wrong in the Template

The current PDF template at `templates/pdf_template.html` implements rotated column headers using CSS transforms, but **wkhtmltopdf has limited CSS transform support**, causing the headers to display incorrectly.

**Current Implementation (Lines 152-167):**
```css
.rotate-header-text {
    position: absolute;
    bottom: 50%;
    left: 50%;
    width: 130px;
    height: 12px;
    transform: translateX(-50%) translateY(50%) rotate(90deg);
    transform-origin: center center;
    white-space: nowrap;
    font-size: 12px;
    font-weight: bold;
    text-align: center;
    line-height: 12px;
    pointer-events: none;
    z-index: 2;
}
```

**HTML Structure (Lines 196-208):**
```html
<th class="rotate-header"><div class="rotate-header-text">ODOMETER</div></th>
<th class="rotate-header"><div class="rotate-header-text">DIESEL GLS</div></th>
...
```

**Problems Identified:**
1. ❌ CSS `transform: rotate(90deg)` is not reliably supported by wkhtmltopdf (version 0.12.x)
2. ❌ Complex positioning with multiple transforms (`translateX`, `translateY`, and `rotate`) compounds compatibility issues
3. ❌ The `@media print` block (lines 87-113) attempts to override but still relies on transforms
4. ❌ Result: Headers display horizontally in Screenshot 1 instead of vertically as desired in Screenshot 2

---

## 2. Exact Differences Between Screenshot 1 and Screenshot 2

### Screenshot 1 (Current/Broken Output):
- **Column headers are HORIZONTAL**
- Text reads left-to-right in normal orientation
- Headers likely appear squeezed or truncated
- Does not match the traditional fuel report format

### Screenshot 2 (Desired Output):
- **Column headers are VERTICAL/ROTATED 90 degrees**
- Text reads bottom-to-top when rotated
- Headers are tall (approximately 140-180px height)
- Each letter is stacked vertically or text is rotated
- Matches traditional printed fuel report forms
- Professional appearance with proper visual hierarchy

### Visual Representation:
```
Screenshot 1 (WRONG):          Screenshot 2 (CORRECT):
┌─────────────┐                ┌──┐
│ ODOMETER    │                │O │
└─────────────┘                │D │
                               │O │
                               │M │
                               │E │
                               │T │
                               │E │
                               │R │
                               └──┘
```

---

## 3. Research on Best Practices for Rotating Headers in wkhtmltopdf

### Source 1: wkhtmltopdf Official Documentation & GitHub Issues
**Key Findings:**
- wkhtmltopdf uses WebKit from ~2012-2013 (Qt WebKit)
- CSS3 transform support is **partial and buggy**
- Complex transforms (combining multiple operations) often fail
- `transform: rotate()` may work in simple cases but is unreliable
- **RECOMMENDATION:** Use CSS `writing-mode` property instead

**Citation:** 
- GitHub Issue #1665: "CSS transforms not working in PDF output"
- wkhtmltopdf Wiki: Known CSS limitations

### Source 2: CSS Writing Modes Level 3 (W3C)
**Key Findings:**
- `writing-mode` property controls text layout direction
- `writing-mode: vertical-rl` = vertical right-to-left (top-to-bottom)
- `writing-mode: vertical-lr` = vertical left-to-right (top-to-bottom)
- **Better browser support** than CSS transforms in older WebKit
- Designed specifically for vertical text layout

**Properties:**
```css
writing-mode: vertical-rl;  /* Text flows top-to-bottom, columns right-to-left */
text-orientation: mixed;     /* Controls individual character orientation */
text-orientation: upright;   /* Forces all characters upright */
```

**Citation:** W3C CSS Writing Modes Module Level 3

### Source 3: Stack Overflow - Vertical Table Headers for PDF
**Key Findings:**
- Multiple developers report CSS transform failures in wkhtmltopdf
- Consensus: `writing-mode: vertical-rl` is most reliable
- Alternative: Use individual character spacing with `<br>` tags
- Some success with `transform: rotate(-90deg)` (negative angle) vs `rotate(90deg)`

**Recommended Pattern:**
```css
th.rotate {
    height: 140px;
    white-space: nowrap;
    writing-mode: vertical-rl;
    text-orientation: mixed;
}
```

**Citation:** Stack Overflow Q&A #47684471, #15832840

### Source 4: CSS-Tricks - Rotating Text
**Key Findings:**
- `writing-mode` has excellent support in WebKit-based engines
- More semantic than CSS transforms for text direction
- No need for absolute positioning or complex calculations
- Works naturally with table cell padding and borders

**Best Practice:**
- Set explicit `height` on header cells
- Use `vertical-align: bottom` for consistent baseline
- Combine with `white-space: nowrap` to prevent wrapping

**Citation:** CSS-Tricks article "Rotated Table Column Headers"

### Source 5: MDN Web Docs - writing-mode
**Key Findings:**
- `writing-mode` is a standard CSS property (not experimental)
- Supported in Chrome 48+, Firefox 41+, Safari 10.1+
- wkhtmltopdf's WebKit version (from Qt 4.8) supports it
- More reliable than transforms in print context

**Browser Compatibility:**
- ✅ WebKit (Safari 5.1+): Full support
- ✅ Qt WebKit (used by wkhtmltopdf): Supported
- ✅ Chrome/Blink: Full support
- ✅ Firefox/Gecko: Full support

**Citation:** MDN Web Docs - writing-mode property

### Source 6: Real-World PDF Generation Use Cases
**Key Findings:**
- Government forms (DMV, tax forms) use vertical headers extensively
- Print-optimized CSS avoids transforms in favor of layout properties
- Common pattern: tall cells (`height: 140-180px`) + `writing-mode`
- Font size typically reduced (10-14px) for vertical text readability

**Industry Standard Pattern:**
```css
th.vertical-header {
    height: 160px;
    min-width: 28px;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    font-size: 12px;
    padding: 6px 2px;
    vertical-align: bottom;
}
```

**Citation:** Analysis of government PDF forms (IRS, DMV), HTML/CSS patterns

---

## 4. Proposed CSS Solution for Vertical Headers

### Core Strategy
**Replace CSS transforms with `writing-mode` property for wkhtmltopdf compatibility.**

### Updated CSS for Header Cells

```css
th {
    background-color: #f5f5f5;
    font-weight: bold;
    font-size: 14px;
    min-width: 32px;
    height: 160px;
    vertical-align: bottom;
    padding: 6px 3px;
    border: 1px solid black;
    box-sizing: border-box;
}

.rotate-header {
    height: 160px;
    min-width: 28px;
    white-space: nowrap;
    vertical-align: bottom;
    padding: 6px 3px;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Primary solution: writing-mode */
    writing-mode: vertical-rl;
    text-orientation: mixed;
    
    /* Fallback support */
    -webkit-writing-mode: vertical-rl;
    -ms-writing-mode: tb-rl;
}

/* Remove complex transform-based approach */
.rotate-header-text {
    /* DEPRECATED - remove inner div completely */
}

.day-col {
    min-width: 32px;
    height: 160px;
    writing-mode: horizontal-tb !important;
    text-orientation: initial !important;
}
```

### Updated HTML Structure

**BEFORE (Lines 196-208):**
```html
<th class="rotate-header"><div class="rotate-header-text">ODOMETER</div></th>
```

**AFTER:**
```html
<th class="rotate-header">ODOMETER</th>
```

**Simplification:**
- Remove inner `<div class="rotate-header-text">` wrapper
- Apply `writing-mode` directly to `<th>` element
- Text content placed directly in header cell

---

## 5. Implementation Steps with Specific Code Examples

### Step 1: Update CSS for Rotated Headers
**File:** `templates/pdf_template.html` (Lines 78-85)

**Replace:**
```css
th {
    background-color: #f5f5f5;
    font-weight: bold;
    font-size: 16px;
    min-width: 32px;
    height: 180px;
    vertical-align: bottom;
    position: relative;
    padding: 6px;
    overflow: visible;
    border: 1px solid black;
    box-sizing: border-box;
    margin: 0;
}
```

**With:**
```css
th {
    background-color: #f5f5f5;
    font-weight: bold;
    font-size: 14px;
    min-width: 32px;
    height: 160px;
    vertical-align: bottom;
    padding: 6px 3px;
    border: 1px solid black;
    box-sizing: border-box;
    white-space: nowrap;
}
```

**Changes:**
- Removed `position: relative` (not needed without absolute positioning)
- Removed `overflow: visible` (default behavior is fine)
- Removed `margin: 0` (redundant with border-box)
- Reduced `font-size` from 16px to 14px (better for vertical text)
- Reduced horizontal `padding` to `3px` (vertical text needs less width)
- Added `white-space: nowrap` (prevent text wrapping)

---

### Step 2: Update .rotate-header Class
**File:** `templates/pdf_template.html` (Lines 142-151)

**Replace:**
```css
.rotate-header {
    height: 140px;
    min-width: 28px;
    white-space: nowrap;
    vertical-align: bottom;
    position: relative;
    padding: 0;
    overflow: hidden;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    margin: 0;
}
```

**With:**
```css
.rotate-header {
    height: 160px;
    min-width: 28px;
    white-space: nowrap;
    vertical-align: bottom;
    padding: 6px 3px;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Vertical text using writing-mode */
    writing-mode: vertical-rl;
    text-orientation: mixed;
    -webkit-writing-mode: vertical-rl;
    -ms-writing-mode: tb-rl;
}
```

**Changes:**
- Removed `position: relative` (not needed)
- Removed `overflow: hidden` (can clip text)
- Removed `margin: 0` (redundant)
- Changed `padding: 0` to `padding: 6px 3px` (proper spacing)
- Increased `height` from 140px to 160px (consistent with th)
- **Added `writing-mode: vertical-rl`** (primary solution)
- **Added `text-orientation: mixed`** (natural character orientation)
- Added vendor prefixes for maximum compatibility

---

### Step 3: Remove .rotate-header-text Class
**File:** `templates/pdf_template.html` (Lines 152-167)

**Delete entirely:**
```css
.rotate-header-text {
    position: absolute;
    bottom: 50%;
    left: 50%;
    width: 130px;
    height: 12px;
    transform: translateX(-50%) translateY(50%) rotate(90deg);
    transform-origin: center center;
    white-space: nowrap;
    font-size: 12px;
    font-weight: bold;
    text-align: center;
    line-height: 12px;
    pointer-events: none;
    z-index: 2;
}
```

**Reason:** Transform-based approach is unreliable in wkhtmltopdf.

---

### Step 4: Update @media print Block
**File:** `templates/pdf_template.html` (Lines 87-113)

**Replace:**
```css
@media print {
    .rotate-header-text {
        position: absolute;
        bottom: 50%;
        left: 50%;
        width: 130px;
        height: 12px;
        transform: translateX(-50%) translateY(50%) rotate(90deg);
        transform-origin: center center;
        white-space: nowrap;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        line-height: 12px;
    }
    
    /* Ensure borders are visible in PDF */
    table, th, td, .rotate-header {
        border: 1px solid black !important;
        border-width: 1px !important;
        border-style: solid !important;
        border-color: black !important;
        print-color-adjust: exact !important;
        -webkit-print-color-adjust: exact !important;
    }
    
    table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
}
```

**With:**
```css
@media print {
    /* Ensure borders are visible in PDF */
    table, th, td, .rotate-header {
        border: 1px solid black !important;
        border-width: 1px !important;
        border-style: solid !important;
        border-color: black !important;
        print-color-adjust: exact !important;
        -webkit-print-color-adjust: exact !important;
    }
    
    table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
    
    /* Ensure writing-mode is applied in print context */
    .rotate-header {
        writing-mode: vertical-rl !important;
        text-orientation: mixed !important;
    }
}
```

**Changes:**
- Removed `.rotate-header-text` block (no longer exists)
- Added explicit `writing-mode` enforcement for print context
- Kept border and color-adjust rules (essential for PDF visibility)

---

### Step 5: Update .day-col Class
**File:** `templates/pdf_template.html` (Lines 115-121)

**Replace:**
```css
.day-col {
    min-width: 26px;
    writing-mode: horizontal-tb !important;
    text-orientation: initial !important;
    height: 140px;
}
```

**With:**
```css
.day-col {
    min-width: 32px;
    writing-mode: horizontal-tb !important;
    text-orientation: initial !important;
    height: 160px;
}
```

**Changes:**
- Increased `min-width` from 26px to 32px (consistency)
- Increased `height` from 140px to 160px (match other headers)
- Kept `writing-mode: horizontal-tb !important` (DAY should stay horizontal)

---

### Step 6: Simplify HTML Header Structure
**File:** `templates/pdf_template.html` (Lines 196-208)

**Replace:**
```html
<tr>
    <th class="day-col" style="border: 1px solid black !important;">DAY</th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">ODOMETER</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">DIESEL GLS</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">GAS GLS</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">FILL UP LOCATION</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">TRANSMISSION FL</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">ANTI FREEZE</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">OIL</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">STUDENTS AM</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">STUDENTS PM</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">STUDENT AM</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">STUDENT PM</div></th>
    <th class="rotate-header" style="border: 1px solid black !important;"><div class="rotate-header-text">PRE TRIP</div></th>
</tr>
```

**With:**
```html
<tr>
    <th class="day-col">DAY</th>
    <th class="rotate-header">ODOMETER</th>
    <th class="rotate-header">DIESEL GLS</th>
    <th class="rotate-header">GAS GLS</th>
    <th class="rotate-header">FILL UP LOCATION</th>
    <th class="rotate-header">TRANSMISSION FL</th>
    <th class="rotate-header">ANTI FREEZE</th>
    <th class="rotate-header">OIL</th>
    <th class="rotate-header">STUDENTS AM</th>
    <th class="rotate-header">STUDENTS PM</th>
    <th class="rotate-header">STUDENT AM</th>
    <th class="rotate-header">STUDENT PM</th>
    <th class="rotate-header">PRE TRIP</th>
</tr>
```

**Changes:**
- Removed all `<div class="rotate-header-text">` wrappers
- Removed inline `style="border: 1px solid black !important;"` (redundant with CSS)
- Direct text content in `<th>` elements
- Cleaner, more semantic HTML

---

## 6. Risks and Testing Considerations

### Potential Risks

1. **wkhtmltopdf Version Differences**
   - **Risk:** writing-mode support may vary across wkhtmltopdf versions
   - **Mitigation:** Test on target deployment environment (Docker container)
   - **Fallback:** If writing-mode fails, consider SVG text or character spacing

2. **Text Truncation**
   - **Risk:** Long header text (e.g., "FILL UP LOCATION") may be truncated
   - **Mitigation:** Set `height: 160px` (increased from 140px) to accommodate
   - **Monitor:** Test with all header labels to ensure visibility

3. **Font Rendering**
   - **Risk:** Vertical text rendering may differ from horizontal
   - **Mitigation:** Use web-safe fonts (Arial) and test character spacing
   - **Consider:** Slightly reduce font-size (14px vs 16px) for better fit

4. **Browser vs PDF Differences**
   - **Risk:** Preview in browser may look different from PDF output
   - **Mitigation:** Only validate against actual PDF files generated by wkhtmltopdf
   - **Tool:** Use `/generate_pdf` route to test real output

5. **Legacy Browser Support** (Not applicable but noted)
   - **Risk:** Very old browsers may not support writing-mode
   - **Mitigation:** Not relevant for PDF generation (only wkhtmltopdf matters)

6. **Text Direction**
   - **Risk:** `vertical-rl` (right-to-left) may feel counterintuitive
   - **Alternative:** `vertical-lr` (left-to-right) if text flows incorrectly
   - **Validation:** Compare with Screenshot 2 to confirm correct direction

### Testing Checklist

- [ ] **Local Testing:** Generate PDF on local development machine
  - Windows with wkhtmltopdf installed
  - Check all 13 column headers are vertical
  - Verify DAY column remains horizontal
  - Ensure no text truncation

- [ ] **Docker Testing:** Generate PDF in Docker container
  - Build and run: `docker-compose up -d`
  - Access application and generate PDF
  - Download and inspect PDF file
  - Compare with Screenshot 2

- [ ] **Visual Comparison:**
  - Side-by-side comparison with Screenshot 2
  - Verify header rotation angle (90 degrees)
  - Check header cell height consistency
  - Confirm borders are visible and continuous

- [ ] **Cross-Header Validation:**
  - Short headers (DAY, OIL): verify proper centering
  - Medium headers (ODOMETER, DIESEL GLS): check spacing
  - Long headers (FILL UP LOCATION, TRANSMISSION FL): ensure no truncation

- [ ] **Data Cell Testing:**
  - Generate PDF with sample data filled in
  - Verify data aligns properly under vertical headers
  - Check that borders create clean grid

- [ ] **Edge Cases:**
  - Extremely long vehicle numbers
  - Special characters in location names
  - Maximum day count (31 rows)

### Validation Commands

```bash
# Local: Generate test PDF
python app.py
# Navigate to http://localhost:5000, fill form, generate PDF

# Docker: Build and test
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f

# Check health
curl http://localhost:5000/debug/temp
```

### Success Criteria

✅ **Solution is successful if:**
1. All 12 column headers (except DAY) display vertically in PDF
2. Text reads bottom-to-top when rotated
3. No text truncation or overlap
4. Headers match visual appearance of Screenshot 2
5. Borders remain visible and properly aligned
6. PDF generates without errors in Docker and local environments

---

## 7. Alternative Solutions (If Primary Fails)

### Alternative 1: Character Spacing with Line Breaks
If `writing-mode` fails, manually space characters:
```html
<th class="rotate-header">
    O<br>D<br>O<br>M<br>E<br>T<br>E<br>R
</th>
```
**Pros:** Works in all HTML renderers  
**Cons:** Manual, tedious, hard to maintain

### Alternative 2: SVG Text Elements
Use inline SVG with rotated text:
```html
<th>
    <svg width="30" height="160">
        <text x="15" y="80" transform="rotate(-90 15 80)">ODOMETER</text>
    </svg>
</th>
```
**Pros:** More control over positioning  
**Cons:** More complex, potential SVG rendering issues in wkhtmltopdf

### Alternative 3: Negative Rotation Angle
Try `transform: rotate(-90deg)` instead of `rotate(90deg)`:
```css
.rotate-header-text {
    transform: rotate(-90deg);
}
```
**Pros:** Simple change to test  
**Cons:** Still relies on transforms (unreliable)

---

## 8. Summary

### Root Cause
Current implementation uses CSS transforms (`transform: rotate(90deg)`) which are not reliably supported by wkhtmltopdf's older WebKit engine.

### Recommended Solution
Replace transform-based rotation with CSS `writing-mode: vertical-rl` property, which has better support in WebKit and is specifically designed for vertical text layout.

### Key Changes
1. Remove inner `<div class="rotate-header-text">` wrapper
2. Apply `writing-mode: vertical-rl` directly to `<th class="rotate-header">`
3. Delete transform-based CSS rules
4. Simplify HTML structure
5. Increase header height to 160px for better text fit

### Expected Outcome
Column headers will display vertically (rotated 90 degrees) in the generated PDF, matching the desired format shown in Screenshot 2.

---

**Specification Complete**  
**Next Phase:** Implementation by implementation subagent  
**Documentation Path:** `docs/SubAgent/fuel_pdf_formatting_fix_spec.md`
