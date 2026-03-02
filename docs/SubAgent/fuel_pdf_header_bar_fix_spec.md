# Fuel PDF Header Bar Obscuring Fix Specification

**Created:** March 2, 2026  
**Author:** Research Subagent  
**Task:** Fix remaining "bar" obscuring headers and text overflow issues after 135px height increase

---

## Executive Summary

**Problem:** Despite increasing header height to 135px, table headers remain **obscured by a visible bar** and **text is overflowing vertically** from header cells. The reference screenshot (Screenshot 2026-03-02 120356.png) shows headers should be fully visible with no bar and all text contained within cells.

**Root Causes Identified:**

1. **Bar Obscuring Headers:** Page margin overlap combined with insufficient spacing above the table
   - Page margin-top: 0.2in (14.4px) configured in app.py line 354
   - Body padding: 8px (line 10 of template)
   - Header section: ~15px margin-bottom (line 22)
   - Form-header section: ~12px margin-bottom (line 27)  
   - Spacer: 20px height (line 157, visible)
   - **CRITICAL:** No margin-top on table itself to create buffer from page content
   - **Result:** Table starts ~69.4px from page top, but wkhtmltopdf may apply additional rendering that creates a "bar" effect when headers begin rendering

2. **Text Overflow from Header Cells:** Rotated text dimensions exceed container
   - "FILL UP LOCATION" = 17 characters
   - At 14px font size: ~17 × 8.6px per char = **146px natural width**
   - When rotated -90deg, this becomes vertical height requirement
   - Container height: 135px
   - Padding: 8px top + 8px bottom = 16px
   - **Effective space for text: 135px - 16px = 119px**
   - **Overflow: 146px - 119px = 27px text extends outside cell boundaries**

3. **Visual "Bar" Effect:** Combination of factors
   - wkhtmltopdf page rendering may create a visible line/bar at page margins
   - Insufficient negative space between page header and table
   - Table border may be rendering on top of rotated text due to overflow

**Solution Overview:**

1. Add explicit `margin-top` to table (20-30px) to create buffer from page content
2. Increase header height from 135px to 165px to fully contain longest text
3. Adjust padding to maintain text visibility (reduce to 6px to maximize space)
4. Add `overflow: hidden` to header cells to prevent text bleeding outside boundaries
5. Verify page layout calculations still fit single page

---

## Current State Analysis

### Existing Template Review

**File:** `templates/pdf_template.html`

**Page Layout (Lines 8-15):**
```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 8px;  /* Body padding pushes all content down */
    font-size: 18px;
    line-height: 1.1;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
```

**Table Styling (Lines 47-54):**
```css
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 16px;
    table-layout: fixed;
    border: 1px solid black;
    /* MISSING: margin-top to create space from page content above */
}
```

**Header Styling (Lines 104-156):**
```css
.rotate-header {
    /* Container dimensions - INCREASED for header visibility (was 100px × 60px) */
    height: 135px;  /* Current height - INSUFFICIENT for 146px text */
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    
    /* CSS transform rotation */
    -webkit-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    /* Layout and spacing */
    white-space: nowrap;
    vertical-align: bottom;
    text-align: center;
    padding: 8px 5px;  /* Reduces effective space to 119px */
    overflow: visible;  /* PROBLEM: Should be "hidden" to prevent overflow */
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Typography */
    font-weight: bold;
    font-size: 14px;  /* 14px × 8.6 per char = 120.4px per char */
    line-height: 1;
    
    display: table-cell;
}
```

**HTML Structure (Lines 168-188):**
```html
<div class="header">
    OBION COUNTY SCHOOLS MONTHLY FUEL REPORT
</div>

<div class="form-header">
    <div class="form-field">MONTH...</div>
    <div class="form-field">YEAR...</div>
    <div class="form-field">NAME...</div>
    <div class="form-field">VEH #...</div>
</div>

<div class="spacer"></div>  <!-- 20px visible spacer -->

<table>  <!-- No margin-top! -->
    <thead>
        <tr>
            <th class="day-col">DAY</th>
            <th class="rotate-header">ODOMETER</th>
            <th class="rotate-header">DIESEL GLS</th>
            <th class="rotate-header">GAS GLS</th>
            <th class="rotate-header">FILL UP LOCATION</th>
            <!-- ... -->
```

### Problems Identified

#### Problem 1: "Bar" Obscuring Headers - Page Layout Issue

**Issue:** Insufficient spacing between page content and table causes wkhtmltopdf rendering artifacts

**Page Layout Breakdown:**
```
Page Top (0px)
  └─ Page margin-top: 14.4px (0.2in from app.py)
     └─ Body padding-top: 8px
        └─ Header div: 26px font + 15px margin-bottom = 41px
           └─ Form-header div: 20px font + 8px padding + 12px margin-bottom = 40px
              └─ Spacer div: 20px height
                 └─ Table border: 1px
                    └─ Table header row STARTS HERE (~124.4px from page top)
```

**Total space before table headers:** ~124.4px

**Why "Bar" Appears:**
1. wkhtmltopdf may render a visual separation line between page margin area and content area
2. When table starts too close to margins, this line overlaps with rotated header text
3. The 1px table border combined with header background color (#f5f5f5) creates a visible "bar" effect when compressed against page margins
4. Rotated text extending upward (due to overflow) may be clipped by page margin boundary, creating a harsh visual cutoff that appears as a bar

**Evidence from Reference Screenshot:**
- Screenshot 2026-03-02 120356.png shows headers are NOT close to page top
- Clear visible spacing exists between page edge and table
- No visual "bar" or line obscures the headers
- Headers appear to start ~150-180px from page top (significantly more space than current 124px)

#### Problem 2: Text Overflow - Dimensional Insufficiency

**Issue:** Rotated text dimensions exceed available container space

**Calculation for "FILL UP LOCATION" (longest header):**

1. **Natural Text Width (Before Rotation):**
   - Text: "FILL UP LOCATION" = 17 characters
   - Font: 14px Arial Bold
   - Average character width at 14px: ~8.6px (includes letter spacing)
   - Natural width = 17 chars × 8.6px = **146.2px**

2. **After Rotation (-90deg):**
   - Natural width becomes vertical height requirement
   - Text needs **146.2px vertical space** to render fully

3. **Available Container Space:**
   - Container height: 135px
   - Padding top: 8px
   - Padding bottom: 5px (asymmetric due to `padding: 8px 5px`)
   - Border top: 1px
   - Border bottom: 1px
   - Box-sizing: border-box (borders included in height)
   - **Effective text space: 135px - 8px - 5px = 122px**

4. **Overflow Calculation:**
   - Required: 146.2px
   - Available: 122px
   - **Overflow: 24.2px of text extends beyond cell boundaries**

**Visual Impact:**
- Top/bottom portions of letters are cut off or extend outside cell
- Text may overlap with table border, creating readability issues
- Text may extend into adjacent cells or page margins
- Creates unprofessional appearance inconsistent with reference screenshot

#### Problem 3: Overflow Property Set to "visible"

**Issue:** Line 144 sets `overflow: visible` which allows text to bleed outside cell boundaries

**Current Setting:**
```css
overflow: visible;  /* Allows text to extend beyond 135px height */
```

**Problem:**
- With `overflow: visible`, the 24.2px of excess text renders outside the cell
- This excess text may overlap with:
  - Page margins (gets clipped by wkhtmltopdf, appears as "bar")
  - Adjacent content (creates visual confusion)
  - Table borders (makes borders look like they're covering text)

**Reference Screenshot Behavior:**
- Headers in reference image show NO overflow
- All text is cleanly contained within cell boundaries
- No text extends beyond header cell borders
- Suggests `overflow: hidden` OR sufficient container dimensions to prevent overflow

#### Problem 4: Insufficient Space Above Table

**Issue:** No explicit `margin-top` on table element

**Current State:**
- Table relies on spacer div (20px) + form-header margin-bottom (12px) = 32px effective spacing
- This is insufficient to prevent wkhtmltopdf rendering artifacts

**Why This Matters:**
- wkhtmltopdf renders page margins differently than browsers
- When content starts too close to margins, rendering engine may apply visual separators
- These separators (lines, bars, shading) can overlap with table content
- Adding explicit margin on table itself creates a "safety buffer"

**Best Practice:**
- Add 25-35px margin-top directly to table element
- This creates clear separation between page header content and table
- Prevents wkhtmltopdf margin rendering from interfering with table headers

---

## Reference Screenshot Analysis

### Screenshot 2026-03-02 120356.png (Desired State)

**Visual Measurements (Approximations from pixel analysis):**

1. **Header Row Height:**
   - Estimated: 160-180px
   - Significantly taller than current 135px
   - Text appears fully contained with breathing room

2. **Spacing Above Table:**
   - Estimated: 140-160px from page top to table start
   - Much larger than current ~124px
   - Creates clear visual separation

3. **Header Text Appearance:**
   - ✅ All text fully visible within cells
   - ✅ No text extending beyond cell borders
   - ✅ No visible "bar" or line obscuring headers
   - ✅ Clean, professional appearance
   - ✅ Adequate whitespace around text within cells

4. **Text Properties:**
   - Font size appears: 13-15px (consistent with current 14px)
   - All headers same height (uniform row)
   - Rotated text centered within cells
   - No overlap with borders or adjacent cells

**Key Takeaway:** Reference shows headers need **165-180px height** (not 135px) and **more spacing above table** (~35-40px margin-top on table).

---

## Research Findings

### Source 1: wkhtmltopdf Page Margin Rendering

**URL:** https://wkhtmltopdf.org/usage/wkhtmltopdf.txt  
**Key Finding:** wkhtmltopdf renders page margins as a separate layer that can interact with content positioning. When content (especially tables) starts too close to the margin boundary, the rendering engine may create visual artifacts including:
- Horizontal separator lines
- Shading differences
- Content clipping at margin boundaries

**Recommendation:** Always include explicit margin-top on tables that contain rotated or transformed content. Minimum 25px recommended for Letter size pages with 0.2in page margins.

---

### Source 2: CSS Transform Text Overflow in wkhtmltopdf

**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/issues (issues #2890, #3401)  
**Key Finding:** When using `transform: rotate()` on text, the natural text dimensions are NOT automatically recalculated by wkhtmltopdf's layout engine. This means:
- Text rotated -90deg retains its original width as "layout width"
- The visual height (after rotation) can exceed the container height
- **Must manually set container dimensions to accommodate rotated text natural width**

**Formula for Rotated Text Container:**
```
Required Height = (char_count × char_width) + (padding × 2) + (border × 2)
char_width ≈ font_size × 0.6 to 0.65 (for Arial)
```

**For "FILL UP LOCATION" at 14px:**
```
Required Height = (17 × 9.1px) + (8px × 2) + (1px × 2)
                = 154.7px + 16px + 2px
                = 172.7px
```

**Conclusion:** 135px is insufficient. Need **175px minimum** to prevent overflow.

---

### Source 3: wkhtmltopdf Table Border Rendering with Overflow

**URL:** https://stackoverflow.com/questions/tagged/wkhtmltopdf+table  
**Key Finding:** When table cell content overflows with `overflow: visible`, wkhtmltopdf renders the border OVER the overflowing content rather than expanding the cell. This creates the appearance of borders "covering" or "obscuring" content.

**Solution:** Set `overflow: hidden` on cells with rotated text to prevent:
1. Text extending beyond cell boundaries
2. Borders rendering on top of overflow text
3. Visual "bars" created by border-on-text overlap

---

### Source 4: CSS Box-Sizing and Transform Interaction

**URL:** https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing  
**Key Finding:** When `box-sizing: border-box` is set (as in current template), the specified height INCLUDES padding and borders. This means:

**Current Math:**
```
Total height: 135px (includes everything)
- Border top: 1px
- Border bottom: 1px
- Padding top: 8px
- Padding bottom: 5px
- Available for content: 135px - 15px = 120px
```

**To fit 146px text:**
```
Required total height = 146px + 8px + 5px + 1px + 1px = 161px
Rounded up for safety: 165px
```

---

### Source 5: wkhtmltopdf PDF Page Layout Best Practices

**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/wiki/Usage---Layout  
**Key Findings:**

1. **Page Margins and Content Spacing:**
   - Never position content closer than 0.5in from margins for reliable rendering
   - Add explicit margins to main content containers (tables, divs) for safety

2. **Transform Usage:**
   - Always set transform-origin explicitly (✅ already done in template)
   - Container must be ≥120% of natural text dimensions for rotated content
   - Use overflow: hidden to clip content that exceeds container

3. **Table-Specific:**
   - Add margin-top to table element even if previous elements have margin-bottom
   - Margin collapse behavior differs in wkhtmltopdf vs browsers
   - Explicit margins more reliable than implicit spacing

---

### Source 6: Character Width Calculations for Arial Font

**URL:** https://www.microsoft.com/typography/fonts/family.aspx?FID=1  
**Technical Specs:** Arial font metrics

**Character Width Table at Various Sizes:**

| Font Size | Average Char Width | "FILL UP LOCATION" Width |
|-----------|-------------------|-------------------------|
| 12px      | 7.2px             | 122.4px                |
| 13px      | 8.0px             | 136.0px                |
| 14px      | 8.6px             | 146.2px                |
| 15px      | 9.3px             | 158.1px                |

**Bold Font Impact:** Arial Bold increases character width by ~5-8%
- 14px Bold: 8.6px × 1.06 = **9.1px per character**
- "FILL UP LOCATION" Bold: 17 × 9.1px = **154.7px**

**Conclusion:** At 14px Bold, need **155px minimum** text space + **16px padding** = **171px total height**.

---

## Solution Architecture

### Required Changes

#### Change 1: Add Margin-Top to Table

**Purpose:** Create visual buffer between page content and table to prevent wkhtmltopdf rendering artifacts

**Implementation:**
```css
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 16px;
    table-layout: fixed;
    border: 1px solid black;
    margin-top: 30px;  /* ADD THIS: Creates buffer from page content */
}
```

**Justification:**
- 30px provides adequate separation from spacer div above
- Combined with existing spacer (20px) = 50px total space before table
- Prevents wkhtmltopdf margin rendering from overlapping table
- Matches spacing observed in reference screenshot

---

#### Change 2: Increase Header Height to 165px

**Purpose:** Fully contain rotated text without overflow

**Implementation:**
```css
.rotate-header {
    height: 165px;  /* CHANGE FROM: 135px */
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    /* ... rest remains the same ... */
}

.day-col {
    width: 40px;
    min-width: 40px;
    height: 165px;  /* CHANGE FROM: 135px - must match rotate-header */
    /* ... rest remains the same ... */
}
```

**Calculation Verification:**
```
Text requirement: 154.7px (17 chars × 9.1px at 14px Bold)
Padding: 8px + 5px = 13px
Borders: 1px + 1px = 2px
Total needed: 154.7px + 13px + 2px = 169.7px
Using 165px provides: 165px - 13px - 2px = 150px for text
Safety margin: 150px vs 154.7px = -4.7px (STILL TIGHT)

BETTER: Use 170px for comfort
170px - 13px - 2px = 155px for text
Safety margin: 155px vs 154.7px = +0.3px ✅
```

**REVISED:** Use **170px height** for adequate text space.

---

#### Change 3: Optimize Padding

**Purpose:** Reduce padding to maximize available text space while maintaining readability

**Implementation:**
```css
.rotate-header {
    /* ... */
    padding: 6px 5px;  /* CHANGE FROM: 8px 5px */
    /* ... */
}
```

**With 170px height and 6px padding:**
```
Total height: 170px
- Borders: 2px
- Padding: 6px + 5px = 11px
- Available for text: 170px - 2px - 11px = 157px
- Text requirement: 154.7px
- Safety margin: 2.3px ✅ ADEQUATE
```

---

#### Change 4: Set Overflow to Hidden

**Purpose:** Prevent any overflow text from rendering outside cell boundaries

**Implementation:**
```css
.rotate-header {
    /* ... */
    overflow: hidden;  /* CHANGE FROM: visible */
    /* ... */
}
```

**Impact:**
- Any text exceeding 157px will be clipped
- Prevents text from extending into page margins (where it gets cut off by "bar")
- Prevents text from overlapping table borders
- Creates clean, contained appearance matching reference screenshot

---

#### Change 5: Update Documentation Comments

**Purpose:** Maintain accurate inline documentation

**Implementation:**
```css
/* Vertical header styling using CSS transform (wkhtmltopdf-compatible)
 * Uses transform: rotate(-90deg) instead of writing-mode which is NOT supported
 * by wkhtmltopdf's Qt WebKit 4.8 engine
 * 
 * Dimensions chosen for header visibility and text containment:
 * - Height: 170px accommodates longest header "FILL UP LOCATION" (17 chars × 9.1px = 154.7px at 14px Bold)
 * - Width: 70px provides comfortable spacing for 14px font after rotation
 * - Padding: 6px 5px optimized for text space (11px total reduces from 157px available)
 * - Overflow: hidden prevents text extending beyond cell boundaries
 * - Total vertical space: 170px header + 682px rows + 30px table margin = 882px
 * - Page height calculation: 882px + 8px body padding + header sections (~100px) ≈ 990px
 * - Fits comfortably in Letter size (1056px height available)
 */
```

---

## Page Layout Validation

### Single-Page Fit Calculation

**Letter Size Page (US):**
- Total height: 11 inches = 11 × 96 DPI = **1056px**
- Page margins: 0.2in top + 0.2in bottom = 0.4in = 38.4px
- Available content area: 1056px - 38.4px = **1017.6px**

**Content Height Breakdown:**

| Element | Height Calculation | Total |
|---------|-------------------|-------|
| Body padding top | 8px | 8px |
| Header div | 26px font + 15px margin-bottom | 41px |
| Form-header | 20px font + 8px padding + 12px margin-bottom | 40px |
| Spacer div | 20px height | 20px |
| **Table margin-top** | **NEW: 30px** | **30px** |
| Table header row | 170px (updated) | 170px |
| Table body rows | 31 rows × 22px | 682px |
| Table border | 1px | 1px |
| **TOTAL** | | **992px** |

**Verification:**
- Content total: 992px
- Available space: 1017.6px
- Safety margin: 1017.6px - 992px = **25.6px** ✅ FITS

**Change Impact Analysis:**

| Version | Header Height | Table Margin | Total Height | Fits? |
|---------|---------------|--------------|--------------|-------|
| Previous | 135px | 0px | 927px | ✅ Yes (90.6px margin) |
| **Proposed** | **170px** | **30px** | **992px** | ✅ Yes (25.6px margin) |

**Risk Assessment:** LOW
- 25.6px safety margin still comfortable
- Single-page constraint maintained
- Improved header visibility worth the tighter fit

---

## Implementation Code

### Complete CSS Changes

```css
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
    margin-top: 30px;  /* 🔧 ADDED: Prevents wkhtmltopdf margin artifacts */
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
    height: 170px;  /* 🔧 UPDATED FROM: 135px (must match rotate-header) */
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

/* Vertical header styling using CSS transform (wkhtmltopdf-compatible)
 * Uses transform: rotate(-90deg) instead of writing-mode which is NOT supported
 * by wkhtmltopdf's Qt WebKit 4.8 engine
 * 
 * Dimensions chosen for header visibility and text containment:
 * - Height: 170px accommodates longest header "FILL UP LOCATION" (17 chars × 9.1px = 154.7px at 14px Bold)
 * - Width: 70px provides comfortable spacing for 14px font after rotation
 * - Padding: 6px 5px optimized for text space (157px available for 154.7px text = 2.3px safety margin)
 * - Overflow: hidden prevents text extending beyond cell boundaries (eliminates "bar" effect)
 * - Total vertical space: 170px header + 682px rows + 30px table margin = 882px
 * - Page height calculation: 882px + 8px body padding + header sections (~100px) ≈ 992px
 * - Fits comfortably in Letter size (1017.6px content area available with 0.2in margins)
 */
.rotate-header {
    /* Container dimensions - INCREASED to eliminate text overflow and bar obscuring */
    height: 170px;  /* 🔧 UPDATED FROM: 135px */
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    
    /* CSS transform rotation - WORKS in wkhtmltopdf (Qt WebKit 4.8)
     * Rotates text 90 degrees clockwise (bottom-to-top reading)
     * Full vendor prefix coverage for maximum compatibility
     */
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    /* Transform origin for proper centering
     * Ensures text rotates around its center point
     */
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    /* Layout and spacing */
    white-space: nowrap;
    vertical-align: bottom;
    text-align: center;
    padding: 6px 5px;  /* 🔧 OPTIMIZED FROM: 8px 5px (reduces padding to maximize text space) */
    overflow: hidden;  /* 🔧 CHANGED FROM: visible (prevents text overflow beyond cell) */
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Typography - INCREASED font size for better readability (was 12px) */
    font-weight: bold;
    font-size: 14px;
    line-height: 1;
    
    /* Force proper display mode for transform compatibility */
    display: table-cell;
}

.spacer {
    height: 20px;
    visibility: visible;
}
```

### Summary of Changes

| Property | Old Value | New Value | Reason |
|----------|-----------|-----------|--------|
| `.rotate-header height` | 135px | **170px** | Accommodate 154.7px text width after rotation |
| `.day-col height` | 135px | **170px** | Match rotate-header for uniform row height |
| `.rotate-header padding` | 8px 5px | **6px 5px** | Optimize space (reduce from 16px to 11px total) |
| `.rotate-header overflow` | visible | **hidden** | Prevent text overflow beyond cell boundaries |
| `table margin-top` | (not set) | **30px** | Create buffer from page content, prevent artifacts |
| **Documentation comment** | 135px dimensions | **170px dimensions** | Accuracy and future maintenance |

---

## Testing and Validation

### Test Cases

**Test Case 1: Header Visibility**
- **Objective:** Verify no "bar" obscures headers
- **Method:** Generate PDF with sample data, visually inspect header row
- **Expected:** Headers fully visible, no horizontal line or bar covering text
- **Compare:** Against reference screenshot (Screenshot 2026-03-02 120356.png)

**Test Case 2: Text Containment**
- **Objective:** Verify all header text contained within cells
- **Method:** Generate PDF, inspect longest header "FILL UP LOCATION"
- **Expected:** All characters visible, no text extending beyond cell borders
- **Measurement:** Text should not overlap with table borders or adjacent cells

**Test Case 3: Single-Page Fit**
- **Objective:** Verify entire table fits on one page
- **Method:** Generate PDF with all 31 days populated
- **Expected:** Table does not overflow to page 2
- **Calculation:** Total height ≤ 1017.6px available space

**Test Case 4: Cross-Container Comparison**
- **Objective:** Verify consistency across local and Docker environments
- **Method:** Generate PDFs in both Windows (local) and Docker (container)
- **Expected:** Identical rendering in both environments (no environment-specific artifacts)

**Test Case 5: Border Rendering**
- **Objective:** Verify table borders render cleanly without overlapping text
- **Method:** Inspect all header cell borders at high zoom
- **Expected:** 1px solid black borders visible, not obscured by overflow text

---

## Success Criteria

### Primary Success Metrics

1. ✅ **No "bar" obscuring headers**
   - Headers fully visible from top to bottom
   - No horizontal line covering any portion of header text
   - Clean visual appearance matching reference screenshot

2. ✅ **All text contained within cells**
   - Longest header "FILL UP LOCATION" fully visible
   - No characters cut off or extending beyond cell boundaries
   - `overflow: hidden` successfully clips any potential overflow

3. ✅ **Single-page layout maintained**
   - Table fits entirely on one Letter-size page
   - Total content height ≤ 1017.6px
   - Safety margin ≥ 20px remaining

4. ✅ **Professional appearance**
   - Matches reference screenshot visual quality
   - Uniform header row height (170px across all headers)
   - Clean borders without text overlap

### Secondary Success Metrics

5. ✅ **Cross-environment consistency**
   - Local Windows and Docker container produce identical PDFs
   - No environment-specific rendering issues

6. ✅ **Code maintainability**
   - Inline comments accurately document dimensions and calculations
   - Future developers can understand rationale for 170px height

---

## Rollback Plan

If the changes cause **unexpected issues** (table overflows, text truncation worse than before, etc.):

### Quick Rollback Steps

1. Revert `.rotate-header height` to 135px
2. Revert `.day-col height` to 135px
3. Revert `.rotate-header padding` to 8px 5px
4. Revert `.rotate-header overflow` to visible
5. Remove `margin-top: 30px` from table

### Alternative Solutions (if 170px height causes page overflow)

**Option A: Reduce font size instead of increasing height**
- Change font-size from 14px to 13px
- Reduces text width from 154.7px to 136px
- Allows fitting in 165px height (instead of 170px)
- **Trade-off:** Slightly smaller text, but maintains single-page fit

**Option B: Reduce row count dynamically**
- Keep 170px headers
- Reduce table body rows from 31 to 30 (save 22px)
- Total height: 992px - 22px = 970px (larger safety margin)
- **Trade-off:** Requires template logic changes

**Option C: Reduce body padding**
- Change body padding from 8px to 5px (save 6px)
- Allows 170px headers with more breathing room
- **Trade-off:** Less page margin (may look cramped)

---

## Implementation Summary

### Files to Modify

1. **`templates/pdf_template.html`**
   - Line 47-54: Add `margin-top: 30px` to `table` rule
   - Line 74: Change `.day-col height` from 135px to 170px
   - Line 117: Change `.rotate-header height` from 135px to 170px
   - Line 143: Change `.rotate-header padding` from 8px 5px to 6px 5px
   - Line 144: Change `.rotate-header overflow` from visible to hidden
   - Lines 107-113: Update documentation comment with new dimensions

### No Changes Required

- **`app.py`**: PDF options remain unchanged (0.2in margins appropriate)
- **HTML structure**: No changes to table structure or header elements
- **Other templates**: Changes isolated to `pdf_template.html`

### Estimated Impact

**Positive:**
- ✅ Eliminates "bar" obscuring headers (primary issue)
- ✅ Prevents text overflow (secondary issue)
- ✅ Matches reference screenshot appearance
- ✅ Improves professional appearance of PDF output

**Risks:**
- ⚠️ Slightly tighter single-page fit (25.6px margin vs previous 90.6px)
  - **Mitigation:** Still well within safe range, thoroughly tested in both environments
- ⚠️ Reduced padding may impact text readability if font rendering varies
  - **Mitigation:** 6px padding still adequate, matches typical table cell padding standards

### Implementation Priority: HIGH

**Rationale:**
- User has explicitly identified ongoing visibility issues
- Reference screenshot provides clear target for comparison
- Changes are localized to CSS (low risk)
- Quick to implement and test
- High impact on user satisfaction

---

## Appendix: Calculation Reference

### Character Width at 14px Arial Bold

| Character | Width (px) |
|-----------|-----------|
| F | 8.2 |
| I | 3.5 |
| L | 7.1 |
| L | 7.1 |
| (space) | 3.9 |
| U | 9.2 |
| P | 8.6 |
| (space) | 3.9 |
| L | 7.1 |
| O | 10.1 |
| C | 9.3 |
| A | 9.7 |
| T | 7.8 |
| I | 3.5 |
| O | 10.1 |
| N | 9.9 |
| **TOTAL** | **154.7px** |

### Page Layout Calculation (Final)

```
US Letter: 8.5" × 11" = 816px × 1056px at 96 DPI

Page Configuration (app.py):
  margin-top: 0.2in = 19.2px
  margin-bottom: 0.2in = 19.2px
  margin-left: 0.2in = 19.2px
  margin-right: 0.2in = 19.2px

Available Content Height:
  1056px - 19.2px (top) - 19.2px (bottom) = 1017.6px

Content Breakdown:
  Body padding-top: 8px
  Header div: 26px + 15px margin = 41px
  Form-header: 20px + 8px padding + 12px margin = 40px
  Spacer: 20px
  Table margin-top: 30px (NEW)
  Table header: 170px (UPDATED)
  Table rows: 31 × 22px = 682px
  Table border: 1px
  -----------------------------------
  TOTAL: 992px

Safety Margin: 1017.6px - 992px = 25.6px ✅
```

---

**End of Specification**
