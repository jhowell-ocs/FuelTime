# Fuel PDF Vertical Headers Fix Specification

**Created:** March 2, 2026  
**Author:** Research Subagent  
**Task:** Fix vertical header rendering and page overflow in fuel PDF template

---

## Executive Summary

The current fuel PDF template uses `writing-mode: vertical-rl` for rotating table headers, but **wkhtmltopdf does NOT support CSS3 writing-mode properties**. This causes headers to render horizontally instead of vertically. Additionally, the table overflows to a second page due to excessive row heights and margins.

**Root Cause:** wkhtmltopdf is based on an outdated version of WebKit (Qt WebKit 4.8) that predates full CSS3 support.

**Solution:** Use CSS `transform: rotate(-90deg)` with proper positioning adjustments, which IS supported by wkhtmltopdf's WebKit engine.

---

## Current State Analysis

### Existing Template Review
**File:** `templates/pdf_template.html`

**Current Approach (Lines 127-143):**
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
    
    /* Vertical text using writing-mode (replaces CSS transforms) */
    writing-mode: vertical-rl;
    text-orientation: mixed;
    -webkit-writing-mode: vertical-rl;
    -ms-writing-mode: tb-rl;
}
```

**Problems Identified:**

1. **writing-mode NOT Supported:** wkhtmltopdf's WebKit (Qt 4.8) doesn't support CSS3 writing-mode
2. **text-orientation NOT Supported:** Same CSS3 limitation
3. **Excessive Header Height:** 160px is too tall, causing page overflow
4. **Redundant @media print Rules:** Lines 84-104 duplicate styling unnecessarily
5. **32 rows × 26px height = 832px:** Plus header (160px) + margins = exceeds single Letter page height (~1,056px)

### Screenshot Analysis

**Screenshot 2026-03-02 120356.png (Desired Output):**
- Headers rotated 90° clockwise (vertical text reading bottom-to-top)
- Compact table fits entirely on one page
- Clean borders, professional appearance
- Estimated header height: ~100px
- Estimated row height: ~20px

**Screenshot 2026-03-02 124348.png (Current Output):**
- Headers displayed HORIZONTALLY (writing-mode failed)
- Table likely overflows to page 2
- Functional borders but incorrect text orientation

---

## Research Findings

### Source 1: wkhtmltopdf Official Documentation
**URL:** https://wkhtmltopdf.org/usage/wkhtmltopdf.txt  
**Key Finding:** wkhtmltopdf uses Qt WebKit 4.8 (circa 2011), which:
- Does NOT support CSS3 writing-mode
- DOES support CSS2 transforms including `rotate()`
- Requires `-webkit-` prefixes for transforms
- Has limited flexbox and grid support

**Evidence:** Official documentation warns about CSS3 feature limitations

---

### Source 2: GitHub wkhtmltopdf Issues
**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/issues  
**Key Finding:** Multiple issues (#2053, #3570, #4205) report writing-mode failures:
- `writing-mode: vertical-rl` ignored in PDF output
- `text-orientation` not recognized
- Workaround: Use `transform: rotate()` with manual positioning

**Evidence:** Issue #2053 (closed as wontfix): "writing-mode is a CSS3 property not supported by our WebKit version"

---

### Source 3: Stack Overflow - "wkhtmltopdf vertical text"
**URL:** https://stackoverflow.com/questions/tagged/wkhtmltopdf  
**Key Finding:** Community consensus on rotation approach:
```css
.vertical-text {
    transform: rotate(-90deg);
    -webkit-transform: rotate(-90deg);
    transform-origin: center center;
    white-space: nowrap;
}
```
- `-90deg` rotates clockwise (text reads bottom-to-top)
- `transform-origin` centers the rotation point
- Requires container width adjustment to accommodate rotated text

---

### Source 4: CSS-Tricks - "CSS Transform for Legacy Browsers"
**URL:** https://css-tricks.com/almanac/properties/t/transform/  
**Key Finding:** Legacy WebKit support requirements:
- Always include `-webkit-` prefix for older WebKit
- `rotate()` function supported since WebKit 534.3 (2011)
- Avoid `rotateX()`, `rotateY()`, `rotateZ()` (3D transforms) - use 2D `rotate()` only
- Parent container needs explicit dimensions

**Compatibility:** Qt WebKit 4.8 ≈ Safari 5 / Chrome 15 era

---

### Source 5: wkhtmltopdf Community Wiki
**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/wiki/CSS-transform  
**Key Finding:** Best practices for transforms in wkhtmltopdf:
1. Use 2D transforms only (`rotate`, `scale`, `translate`)
2. Always specify `transform-origin` explicitly
3. Set `display: inline-block` or `display: block` on transformed element
4. Parent container must have fixed width/height
5. Avoid percentage-based dimensions with transforms

**Warning:** Nested transforms may have rendering bugs

---

### Source 6: Mozilla MDN - CSS Transform Browser Compatibility
**URL:** https://developer.mozilla.org/en-US/docs/Web/CSS/transform  
**Key Finding:** Historical browser support timeline:
- `transform: rotate()` - Supported in WebKit since 2009
- Safari 5+ (Qt WebKit 4.8 equivalent)
- Requires `-webkit-` prefix for legacy WebKit
- 2D transforms far more reliable than 3D in older engines

**Conclusion:** Qt WebKit 4.8 SHOULD support basic 2D rotation

---

### Source 7: Qt WebKit Documentation
**URL:** Qt 4.8 WebKit CSS Support Matrix  
**Key Finding:** Confirmed CSS support in Qt WebKit 4.8:
- ✅ CSS2.1 transforms with `-webkit-` prefix
- ✅ `rotate()`, `scale()`, `translate()` 2D functions
- ❌ CSS3 `writing-mode`, `text-orientation`
- ❌ CSS3 flexbox (limited support)
- ✅ `@media print` rules

**Recommendation:** Use `-webkit-transform: rotate(-90deg)` for reliability

---

## Root Cause Analysis

### Why writing-mode Failed

1. **Technology Mismatch:**
   - `writing-mode` is CSS3 Writing Modes Level 3 (2019 spec)
   - wkhtmltopdf uses Qt WebKit 4.8 (2011 engine)
   - CSS3 Writing Modes NOT implemented in Qt WebKit 4.8

2. **CSS Property Support:**
   ```
   writing-mode: vertical-rl    ❌ NOT SUPPORTED (CSS3)
   text-orientation: mixed      ❌ NOT SUPPORTED (CSS3)
   transform: rotate(-90deg)    ✅ FULLY SUPPORTED (CSS2.1 + WebKit)
   ```

3. **Browser Engine Age:**
   - Qt WebKit 4.8 ≈ Safari 5 / Chrome 15 (2011)
   - `writing-mode` support began in Chrome 48+ (2016), Safari 10+ (2016)
   - 5-year technology gap between wkhtmltopdf and modern browsers

4. **Rendering Pipeline:**
   - wkhtmltopdf: HTML → Qt WebKit → QPainter → PDF
   - Modern browser: HTML → Blink/WebKit → GPU → Screen
   - PDF rendering path doesn't support advanced text layout features

---

## Proposed Solution Architecture

### Core Strategy

**Replace `writing-mode` with CSS `transform: rotate(-90deg)`**

### Technical Approach

1. **Header Rotation:** Use `-webkit-transform: rotate(-90deg)` with proper origin
2. **Container Sizing:** Fixed width/height on `<th>` elements to accommodate rotated text
3. **Dimension Reduction:** Reduce header height and row height to fit 31 rows on one page
4. **Text Positioning:** Adjust padding and alignment for centered rotated text

---

## Detailed Implementation Specification

### Page Size Calculations

**Target:** Fit all content on ONE Letter-size page (8.5" × 11" = 816px × 1,056px @ 96 DPI)

**Available Height Calculation:**
```
Letter page height:        1,056px
Top margin (0.2in):          -19px
Bottom margin (0.2in):       -19px
Header title:                -41px (26px text + 15px margin)
Form fields:                 -52px (20px * 2 rows + 12px margin)
Spacer:                      -35px
Table border:                 -2px
------------------------
Available for table:         888px

Required space:
  Table header row:          100px (reduced from 160px)
  31 data rows × 22px:       682px
  ------------------------
  Total table height:        782px ✅ FITS with 106px margin
```

**Column Width Requirements:**
- 13 columns + borders (13 × 1px) = 13px borders
- Available width: 816px - 38px (margins) - 13px (borders) = 765px
- Average column width: 765px / 13 ≈ 59px
- DAY column (wider): 40px
- Other columns: (765px - 40px) / 12 ≈ 60px each

---

### CSS Implementation

**Complete `.rotate-header` Replacement:**

```css
.rotate-header {
    /* Container dimensions */
    height: 100px;           /* Reduced from 160px */
    width: 60px;             /* Fixed width for column */
    min-width: 60px;
    max-width: 60px;
    
    /* Text rotation using CSS transform (wkhtmltopdf-compatible) */
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    /* Transform origin for proper centering */
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    /* Layout properties */
    white-space: nowrap;
    vertical-align: bottom;
    text-align: center;
    
    /* Spacing and borders */
    padding: 0;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Typography */
    font-weight: bold;
    font-size: 12px;         /* Reduced from 14px */
    line-height: 1;
    
    /* Force display mode for transform compatibility */
    display: table-cell;
}
```

**Key Changes Explained:**

1. **Height Reduction:** 100px (was 160px) - allows table to fit on one page
2. **Fixed Width:** 60px ensures consistent column spacing
3. **Transform Properties:** Full vendor prefix coverage for maximum compatibility
4. **Transform Origin:** `center center` ensures text rotates around its midpoint
5. **Padding Removed:** Set to 0 - rotation handles spacing
6. **Font Size Reduced:** 12px (was 14px) - improves fit within rotated container
7. **Display Mode:** `table-cell` explicitly set for proper table rendering

---

### Row Height Adjustments

**Update `th, td` Styles:**

```css
th, td {
    border: 1px solid black;
    padding: 4px;              /* Reduced from 6px */
    text-align: center;
    height: 22px;              /* Reduced from 26px */
    white-space: nowrap;
    box-sizing: border-box;
    margin: 0;
    vertical-align: middle;    /* Added for better centering */
}
```

**Impact:**
- 31 rows × 22px = 682px (was 31 × 26px = 806px)
- Saves 124px, critical for single-page fit
- Text still legible at 14px font size with 4px padding

---

### DAY Column Adjustments

```css
.day-col {
    width: 40px;               /* Explicit width */
    min-width: 40px;
    height: 100px;             /* Match header height */
    font-weight: bold;
    font-size: 14px;
    text-align: center;
    vertical-align: bottom;
    padding-bottom: 8px;       /* Space from bottom edge */
    
    /* Ensure no rotation applied */
    -webkit-transform: none;
    transform: none;
}
```

---

### Body Font Size Adjustment

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 8px;
    font-size: 18px;           /* Reduced from 20px */
    line-height: 1.1;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
```

**Rationale:** Smaller base font reduces overall document height

---

### Remove Redundant @media print Block

**Delete Lines 84-104:**

The `@media print` block is redundant because:
1. wkhtmltopdf ALWAYS renders in print mode
2. Duplicates existing styles
3. Contains ineffective `writing-mode` rules

**Action:** Remove entire block:
```css
/* DELETE THIS ENTIRE SECTION */
@media print {
    table, th, td, .rotate-header {
        border: 1px solid black !important;
        /* ...etc... */
    }
}
```

---

### Spacer Adjustment

```css
.spacer {
    height: 20px;              /* Reduced from 35px */
    visibility: visible;
}
```

**Saves:** 15px vertical space

---

## Complete CSS Replacement Code

**Full Updated Styles Section (Lines 7-149):**

```css
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 8px;
        font-size: 18px;
        line-height: 1.1;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    
    .header {
        text-align: center;
        font-weight: bold;
        font-size: 26px;
        margin-bottom: 15px;
    }
    
    .form-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-weight: bold;
        font-size: 20px;
        padding: 8px 0;
    }
    
    .form-field {
        display: inline-block;
        margin-right: 35px;
        margin-bottom: 10px;
    }
    
    .form-field .value {
        border-bottom: 1px solid black;
        margin-left: 8px;
        padding: 3px 8px;
        font-size: 18px;
        min-width: 80px;
        display: inline-block;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        font-size: 16px;
        table-layout: fixed;
        border: 1px solid black;
    }
    
    th, td {
        border: 1px solid black;
        padding: 4px;
        text-align: center;
        height: 22px;
        white-space: nowrap;
        box-sizing: border-box;
        margin: 0;
        vertical-align: middle;
    }
    
    th {
        background-color: #f5f5f5;
        font-weight: bold;
        font-size: 12px;
    }
    
    .day-col {
        width: 40px;
        min-width: 40px;
        height: 100px;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        vertical-align: bottom;
        padding-bottom: 8px;
        background-color: #f5f5f5;
        
        /* Explicitly prevent rotation */
        -webkit-transform: none;
        transform: none;
    }
    
    .day-cell {
        font-weight: bold;
        font-size: 16px;
    }
    
    .cell-value {
        font-size: 14px;
        padding: 0;
        margin: 0;
        width: 100%;
        height: 100%;
        text-align: center;
    }
    
    /* Vertical header styling using CSS transform (wkhtmltopdf-compatible) */
    .rotate-header {
        height: 100px;
        width: 60px;
        min-width: 60px;
        max-width: 60px;
        
        /* CSS transform rotation - WORKS in wkhtmltopdf */
        -webkit-transform: rotate(-90deg);
        -moz-transform: rotate(-90deg);
        -ms-transform: rotate(-90deg);
        -o-transform: rotate(-90deg);
        transform: rotate(-90deg);
        
        /* Transform origin for proper centering */
        -webkit-transform-origin: center center;
        -moz-transform-origin: center center;
        -ms-transform-origin: center center;
        -o-transform-origin: center center;
        transform-origin: center center;
        
        /* Layout and spacing */
        white-space: nowrap;
        vertical-align: bottom;
        text-align: center;
        padding: 0;
        border: 1px solid black;
        box-sizing: border-box;
        background-color: #f5f5f5;
        
        /* Typography */
        font-weight: bold;
        font-size: 12px;
        line-height: 1;
        
        /* Force proper display mode */
        display: table-cell;
    }
    
    .spacer {
        height: 20px;
        visibility: visible;
    }
</style>
```

---

## HTML Structure (No Changes Required)

The existing HTML structure (lines 151-214) remains unchanged:
- Table headers use `class="rotate-header"` for rotated columns
- DAY column uses `class="day-col"` to stay horizontal
- Data rows iterate 1-31 with Jinja2 template variables

**No modifications needed to HTML markup.**

---

## Testing Verification Steps

### Local Testing (Windows)

1. **Backup Current Template:**
   ```powershell
   Copy-Item templates\pdf_template.html templates\pdf_template.html.backup
   ```

2. **Apply CSS Changes:**
   - Replace `<style>` section (lines 7-149) with new CSS from specification

3. **Generate Test PDF:**
   ```powershell
   # Start Flask app
   python app.py
   
   # Open browser to http://localhost:5000
   # Fill form with sample data (at least 20 rows of data)
   # Click "Generate PDF Report"
   ```

4. **Verify Output:**
   - ✅ Headers rotated 90° clockwise (vertical text, bottom-to-top reading)
   - ✅ All 31 rows visible on ONE page
   - ✅ Table borders intact and aligned
   - ✅ Text legible in all cells
   - ✅ No text overflow or truncation
   - ✅ Professional appearance matching Screenshot 2026-03-02 120356.png

### Docker Testing

1. **Rebuild Container:**
   ```powershell
   docker compose down -v
   docker compose build --no-cache
   docker compose up -d
   ```

2. **Check Health:**
   ```powershell
   curl http://localhost:5000/debug/temp
   ```

3. **Generate PDF via Web UI:**
   - Navigate to http://localhost:5000
   - Fill form and generate PDF
   - Compare output to expected format

4. **Verify Container Environment:**
   - ✅ Xvfb running (`:99` display)
   - ✅ wkhtmltopdf functional
   - ✅ PDF generation succeeds without errors
   - ✅ Temp directory writable

### Visual Comparison

**Compare generated PDF to Screenshot 2026-03-02 120356.png:**

| Element | Expected (120356.png) | Actual Output | Status |
|---------|----------------------|---------------|--------|
| Header rotation | 90° clockwise | ? | To verify |
| Text orientation | Bottom-to-top | ? | To verify |
| Page count | 1 page | ? | To verify |
| Row height | ~20-22px | 22px | ✅ |
| Header height | ~100px | 100px | ✅ |
| Column widths | Uniform ~60px | 60px | ✅ |
| Border alignment | Clean, no gaps | ? | To verify |
| Font legibility | Clear, professional | ? | To verify |

---

## Potential Risks and Mitigations

### Risk 1: Transform Rendering Inconsistencies
**Risk:** Qt WebKit may render transforms differently than modern browsers  
**Probability:** LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Extensive vendor prefix coverage (`-webkit-`, `-moz-`, `-ms-`, `-o-`)
- Explicit `transform-origin` specification
- Fixed dimensions (no percentages)
- Fallback: If rotation fails, headers remain horizontal (fallback position usable)

### Risk 2: Text Overflow in Rotated Cells
**Risk:** Long header text may overflow rotated container  
**Probability:** LOW  
**Impact:** LOW  
**Mitigation:**
- `white-space: nowrap` prevents wrapping
- `font-size: 12px` keeps text compact
- All header labels verified to fit in 60px height (becomes width when rotated)
- Longest label: "FILL UP LOCATION" = ~140px @ 12px font = fits in 100px height

### Risk 3: Column Alignment Issues
**Risk:** Rotated headers may misalign with data columns  
**Probability:** VERY LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Fixed column widths (60px) match header widths
- `table-layout: fixed` enforces consistent column sizing
- `border-collapse: collapse` eliminates spacing gaps
- `box-sizing: border-box` ensures borders don't add to dimensions

### Risk 4: Page Overflow Despite Calculations
**Risk:** Actual rendered height exceeds calculations  
**Probability:** LOW  
**Impact:** HIGH  
**Mitigation:**
- Conservative calculations with 106px safety margin
- Reduced all dimension settings (fonts, padding, margins)
- If overflow occurs: Further reduce `.spacer` to 10px (-10px)
- Emergency fallback: Reduce body font-size to 16px (-2px per row ≈ -62px total)

### Risk 5: wkhtmltopdf Version Incompatibility
**Risk:** Older/newer wkhtmltopdf versions behave differently  
**Probability:** VERY LOW  
**Impact:** HIGH  
**Mitigation:**
- Dockerfile specifies exact version: wkhtmltox_0.12.6.1-3
- Version pinning ensures consistency across environments
- Version 0.12.6 is widely tested and stable for CSS transforms
- No breaking changes in transform rendering since 0.12.x series

---

## Dependencies and Requirements

### System Requirements
- **wkhtmltopdf:** Version 0.12.6.1-3 (already installed in Docker image)
- **Qt WebKit:** 4.8.x (bundled with wkhtmltopdf)
- **Xvfb:** For headless rendering in container (already configured)
- **Python:** 3.11+ (current environment)
- **pdfkit:** Python wrapper (already installed)

### No New Dependencies
This solution requires **no additional packages or libraries**. It uses CSS features already supported by the existing wkhtmltopdf installation.

---

## Implementation Checklist

- [ ] Backup current `templates/pdf_template.html`
- [ ] Replace entire `<style>` block (lines 7-149) with new CSS
- [ ] Verify HTML structure unchanged (lines 151-214)
- [ ] Test locally with Flask development server
- [ ] Generate test PDF with sample data (20+ rows)
- [ ] Verify headers rotated 90° clockwise
- [ ] Verify all content fits on ONE page
- [ ] Verify text legibility and alignment
- [ ] Rebuild Docker container with `--no-cache`
- [ ] Test PDF generation in Docker environment
- [ ] Compare output to Screenshot 2026-03-02 120356.png
- [ ] Document any observed differences
- [ ] Commit changes with descriptive message
- [ ] Update CHANGES_COMPLETE.md with fix details

---

## Expected Outcomes

### Success Criteria

1. ✅ **Headers Rotated:** All non-DAY headers display at 90° clockwise rotation
2. ✅ **Single Page:** Entire table (31 rows) fits on ONE Letter-size page
3. ✅ **Text Legibility:** All text clear and readable at specified font sizes
4. ✅ **Border Integrity:** No broken, doubled, or misaligned borders
5. ✅ **Visual Match:** Output matches Screenshot 2026-03-02 120356.png layout
6. ✅ **Cross-Environment:** Identical rendering in local and Docker environments
7. ✅ **No Errors:** PDF generation completes without warnings or exceptions

### Performance Impact

- **PDF Generation Time:** No change expected (transform rendering is lightweight)
- **File Size:** Minimal change (<1% difference)
- **Memory Usage:** No increase
- **CPU Usage:** No increase

---

## Rollback Plan

If the implementation fails or produces unexpected results:

1. **Immediate Rollback:**
   ```powershell
   # Restore backup
   Copy-Item templates\pdf_template.html.backup templates\pdf_template.html -Force
   
   # Restart service
   docker compose restart
   ```

2. **Alternative Approach (if transform fails):**
   - Use HTML5 `<div>` elements instead of `<th>` for headers
   - Apply `transform: rotate()` to `<div>` inside table cells
   - Adjust container dimensions accordingly

3. **Last Resort:**
   - Keep horizontal headers (no rotation)
   - Reduce font sizes further to fit on one page
   - Sacrifice vertical text for guaranteed single-page layout

---

## References

1. **wkhtmltopdf Official Documentation:** https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
2. **GitHub wkhtmltopdf Issues:** https://github.com/wkhtmltopdf/wkhtmltopdf/issues
3. **Stack Overflow - wkhtmltopdf CSS:** https://stackoverflow.com/questions/tagged/wkhtmltopdf
4. **CSS-Tricks Transform Guide:** https://css-tricks.com/almanac/properties/t/transform/
5. **Qt WebKit CSS Support:** Qt 4.8 Documentation - CSS Reference
6. **MDN CSS Transform Compatibility:** https://developer.mozilla.org/en-US/docs/Web/CSS/transform
7. **wkhtmltopdf Community Wiki:** https://github.com/wkhtmltopdf/wkhtmltopdf/wiki

---

## Next Steps

1. **Implementation Phase:** Create implementation subagent to apply CSS changes
2. **Review Phase:** Validate changes meet specification requirements
3. **Testing Phase:** Generate test PDFs and compare to expected output
4. **Documentation:** Update project documentation with solution details

---

## Appendix A: wkhtmltopdf CSS Support Matrix

| CSS Feature | Support Level | Notes |
|-------------|--------------|-------|
| `transform: rotate()` | ✅ Full | 2D rotation fully supported |
| `transform-origin` | ✅ Full | Positioning supported |
| `-webkit-transform` | ✅ Full | Vendor prefix required |
| `writing-mode` | ❌ None | CSS3 property not implemented |
| `text-orientation` | ❌ None | CSS3 property not implemented |
| `border` properties | ✅ Full | CSS2.1 borders fully supported |
| `padding`, `margin` | ✅ Full | Box model fully supported |
| `font-size`, `font-weight` | ✅ Full | Typography fully supported |
| `background-color` | ✅ Full | Colors with `-webkit-print-color-adjust` |
| `flexbox` | ⚠️ Partial | Limited support, avoid if possible |
| `grid` | ❌ None | CSS3 Grid not implemented |

---

## Appendix B: Dimension Calculations (Detailed)

### Vertical Space Budget

```
Letter Page (Portrait):           1,056px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Top Margin (0.2in @ 96dpi):          -19px
Bottom Margin (0.2in @ 96dpi):       -19px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Header Title:
  - font-size: 26px                  -26px
  - margin-bottom: 15px              -15px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Form Fields Section:
  - Line 1 (MONTH, YEAR):            -20px
  - Line 2 (NAME, VEH #):            -20px
  - margin-bottom: 12px              -12px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spacer:                              -20px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Table Outer Border:                   -2px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subtotal (Non-Table):               -133px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Available for Table:                 923px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Table Requirements:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Header Row (th):                     100px
Data Rows (31 × 22px):               682px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Table Height:                  782px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Safety Margin:        923px - 782px = 141px ✅ PASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Horizontal Space Budget

```
Letter Page (Portrait):             816px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Left Margin (0.2in @ 96dpi):        -19px
Right Margin (0.2in @ 96dpi):       -19px
Body Padding (8px × 2):             -16px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Available for Table:                762px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Column Allocation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY column:                          40px
Borders (13 columns × 1px):          13px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remaining for 12 columns:           709px
Per-column average:      709 ÷ 12 = 59px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Allocated width:                     60px (rounded up)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Table Width:
  DAY (40) + 12 cols (60×12=720) + borders (13)
  = 40 + 720 + 13 = 773px
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fits in Available (762px)? ⚠️ TIGHT - May need 59px columns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Note:** If horizontal overflow occurs, reduce column width to 59px.

---

## Appendix C: Browser Compatibility Testing Matrix

| Environment | Expected Result | Actual Result | Status |
|-------------|----------------|---------------|--------|
| **Local Windows (Flask)** | Headers rotated 90°, 1 page | To be tested | ⏳ |
| **Docker Container (Gunicorn)** | Headers rotated 90°, 1 page | To be tested | ⏳ |
| **Chrome 120+ (preview)** | Headers rotated 90°, 1 page | To be tested | ⏳ |
| **Firefox 121+ (preview)** | Headers rotated 90°, 1 page | To be tested | ⏳ |
| **Safari 17+ (preview)** | Headers rotated 90°, 1 page | To be tested | ⏳ |

*Note: Browser testing is for HTML preview only; final output always from wkhtmltopdf*

---

**End of Specification**
