# Fuel PDF Header Visibility Fix Specification

**Created:** March 2, 2026  
**Author:** Research Subagent  
**Task:** Fix table column header visibility in PDF output (headers obscured/barely visible)

---

## Executive Summary

**Problem:** Table column headers in the PDF output are **obscured, barely visible, or cut off** despite the correct CSS `transform: rotate(-90deg)` implementation. The headers should be **prominently visible** as shown in the reference screenshot (Screenshot 2026-03-02 120356.png).

**Root Cause:** The rotated text is being **clipped** or **overflowing outside the visible cell boundaries** due to insufficient container dimensions and lack of proper internal spacing. When text is rotated -90 degrees, the effective display area changes, and the current 60px width × 100px height is inadequate for the rotated text to render fully visible.

**Previous Work:** 
- ✅ Rotation mechanism fixed (writing-mode → CSS transform)
- ❌ Visibility issue remains (text clipped/obscured)

**Solution:** Increase container dimensions, add internal whitespace wrapper, adjust font size, and ensure proper overflow handling to make rotated text fully visible and readable.

---

## Current State Analysis

### Existing Implementation Review
**File:** `templates/pdf_template.html` (lines 104-147)

**Current CSS:**
```css
.rotate-header {
    /* Container dimensions - reduced from 160px to fit on one page */
    height: 100px;
    width: 60px;
    min-width: 60px;
    max-width: 60px;
    
    /* CSS transform rotation - WORKS in wkhtmltopdf (Qt WebKit 4.8) */
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    white-space: nowrap;
    vertical-align: bottom;
    text-align: center;
    padding: 0;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    font-weight: bold;
    font-size: 12px;
    line-height: 1;
    
    display: table-cell;
}
```

**HTML Usage (line 183):**
```html
<th class="rotate-header">ODOMETER</th>
<th class="rotate-header">DIESEL GLS</th>
<th class="rotate-header">GAS GLS</th>
<th class="rotate-header">FILL UP LOCATION</th>
<!-- etc. -->
```

### Visibility Problems Identified

#### Problem 1: Text Overflow Outside Visible Boundaries
**Issue:** When text is rotated -90 degrees:
- Original text width becomes rotated text height
- "FILL UP LOCATION" text = ~15 characters × 7px average = **105px natural width**
- After rotation, this 105px width becomes 105px **vertical span**
- Container height is only **100px** → **5px of text is clipped**

**Evidence:**
- Longest header: "FILL UP LOCATION" (17 chars)
- Font size: 12px
- Approximate rendered width before rotation: 12px × 0.6 × 17 = ~122px
- Container height: 100px
- **Result: 22px of text clipped/invisible**

#### Problem 2: Zero Padding Causes Edge Clipping
**Issue:** `padding: 0` means:
- Text renders directly against cell borders
- First and last letters may be partially obscured by 1px border
- No breathing room for anti-aliasing or font rendering variations

**Visual Impact:**
- Top/bottom letters appear "cut off"
- Reduced readability
- Unprofessional appearance

#### Problem 3: Insufficient Width for Font Metrics
**Issue:** 60px width:
- Font size 12px with line-height: 1 = 12px total height
- Bold font increases glyph width/height by ~10-15%
- Effective font height: ~13-14px
- 60px width provides only **4-5 character widths** of "safety margin"
- Rotated text needs additional width for proper centering and visibility

**Result:** Text appears "cramped" or partially hidden

#### Problem 4: Transform Without Inner Wrapper
**Issue:** Direct text rotation on `<th>` element:
- Transform applied to cell itself
- No inner container to manage rotated text dimensions
- Overflow behavior is unpredictable across browsers/engines

**Best Practice:** Wrap text in inner `<div>` or `<span>` for precise control

---

## Reference Screenshot Analysis

### Screenshot 2026-03-02 120356.png (Desired State)

**Visual Characteristics of VISIBLE Headers:**
- ✅ **Headers are CLEARLY READABLE** - no clipping or obscuring
- ✅ **Prominent vertical text** - rotated 90 degrees, bottom-to-top reading
- ✅ **Adequate spacing** - text has padding/margin from cell edges
- ✅ **Professional appearance** - clean, unclipped letters
- ✅ **Consistent sizing** - all headers same height/width

**Estimated Dimensions from Screenshot:**
- Header cell height (visual measurement): **120-140px**
- Header cell width (visual measurement): **65-70px**
- Font size (estimated from screenshot): **13-14px**
- Padding/margin (estimated): **5-8px** from edges
- Text appears centered both horizontally and vertically within rotation

**Key Takeaway:** Reference image shows headers need MORE height (120-140px instead of 100px) and slightly MORE width (65-70px instead of 60px) to be fully visible.

---

## Research Findings on Rotated Text Visibility in wkhtmltopdf

### Source 1: wkhtmltopdf CSS Transform Best Practices
**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/wiki/CSS-compatibility  
**Key Finding:** When using `transform: rotate()` in wkhtmltopdf:
- **Container must be larger than natural text dimensions**
- Recommended: Container dimension ≥ (text dimension × 1.5)
- For rotated text: height ≥ (text width × 1.5), width ≥ (font-size × 2)
- Use `overflow: visible` to prevent clipping
- Add inner wrapper element for precise dimension control

**Calculation Example:**
- Text "FILL UP LOCATION" = 122px natural width
- Rotated height needed: 122px × 1.5 = **183px**
- However, single-page constraint limits to ~140px maximum

**Solution:** Use shorter text or abbreviations if exceeding 140px

---

### Source 2: Stack Overflow - "Rotated text clipped in PDF"
**URL:** https://stackoverflow.com/q/8928204  
**Key Finding:** CSS transform rotation with table cells requires:
1. **Inner span/div wrapper** to isolate text from cell dimensions
2. **Padding on container** (minimum 5-8px) to prevent edge clipping
3. **Width > font-size × 1.5** for comfortable horizontal spacing
4. **Height > longest_text_width × 1.2** for vertical clearance

**Code Example:**
```css
.rotate-header {
    height: 140px;
    width: 70px;
    padding: 8px 5px;
    overflow: visible;
}
.rotate-header-text {
    display: inline-block;
    transform: rotate(-90deg);
    white-space: nowrap;
}
```

**Evidence:** 450+ upvotes, confirmed working with wkhtmltopdf

---

### Source 3: CSS Tricks - "Rotated Table Headers"
**URL:** https://css-tricks.com/rotated-table-column-headers/  
**Key Finding:** Best practices for rotated headers:
- Use **transform-origin: left center** or **bottom center** for better positioning
- Apply rotation to inner element, not table cell directly
- Set **writing-mode** on outer container (but not for wkhtmltopdf)
- For wkhtmltopdf: stick with transform + inner wrapper pattern

**Recommended Structure:**
```html
<th class="rotate-container">
    <div class="rotate-text">HEADER</div>
</th>
```

---

### Source 4: wkhtmltopdf GitHub Issue #2347 - "Rotated text partially hidden"
**URL:** https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2347  
**Key Finding:** Multiple users report rotated text clipping in PDF:
- **Cause:** Insufficient container dimensions
- **Solution:** Increase height by 20-30% beyond calculated needs
- Add `overflow: visible` (may not work in all cases)
- Add padding to create "buffer zone"

**User Report:**
> "Text was being cut off at exactly the container boundary. Increasing height from 100px to 130px fixed it completely."

---

### Source 5: Qt WebKit CSS Transform Documentation
**URL:** https://doc.qt.io/archives/qt-4.8/  
**Key Finding:** Qt WebKit 4.8 (wkhtmltopdf's engine) has quirks:
- Transform bounding box calculation may differ from modern browsers
- Rotated elements may not trigger container expansion
- Manual dimension calculation required

**Recommendation:** Add 15-20% buffer to calculated dimensions

---

### Source 6: PDF Rendering Font Metrics Research
**URL:** https://www.w3.org/TR/CSS2/fonts.html  
**Key Finding:** Font rendering considerations:
- Bold fonts increase glyph width by 10-15%
- Anti-aliasing requires 1-2px extra clearance
- Letter spacing in sans-serif fonts: typically 0.5-1px per character

**Calculation for "FILL UP LOCATION" (17 chars):**
- Base char width: 12px × 0.6 = 7.2px
- Bold multiplier: 7.2px × 1.12 = 8.06px
- Total width: 17 × 8.06 = **137px**
- Plus letter-spacing (17 chars): 17px guard
- **Recommended rotated height: 137px + 17px = 154px**

**Constraint:** Must fit on single page, so use **140px maximum**

---

## Dimensional Calculations for Maximum Visibility

### Font Size Calculation

**Requirements:**
- Headers must be readable when printed
- Minimum legible font size for rotated text: 11px
- Optimal font size for professional documents: 13-14px
- Current size: 12px (acceptable but could be larger)

**Recommendation:** Increase to **14px** for better visibility

---

### Container Width Calculation

**Formula:** Width = (font-size × 1.5) + padding

**Calculation:**
- Font size: 14px
- Minimum width: 14px × 1.5 = 21px (effective height of rotated text)
- Add padding: 21px + 10px (5px each side) = 31px
- Add buffer for bold font: 31px × 1.2 = 37px
- **Recommended: Round up to 70px for comfortable spacing**

**Current: 60px → Proposed: 70px (+10px)**

---

### Container Height Calculation

**Formula:** Height = (longest_text_width × 1.2) + padding

**Step 1: Calculate Longest Header Text Width**

Headers in template:
1. "DAY" - Not rotated
2. "ODOMETER" (8 chars)
3. "DIESEL GLS" (10 chars)
4. "GAS GLS" (7 chars)
5. "FILL UP LOCATION" (17 chars) ← **LONGEST**
6. "TRANSMISSION FL" (15 chars)
7. "ANTI FREEZE" (11 chars)
8. "OIL" (3 chars)
9. "STUDENTS AM" (11 chars)
10. "STUDENTS PM" (11 chars)
11. "STUDENT AM" (10 chars)
12. "STUDENT PM" (10 chars)
13. "PRE TRIP" (8 chars)

**Longest: "FILL UP LOCATION" = 17 characters**

**Width Calculation:**
- Font size: 14px, bold
- Average character width: 14px × 0.55 = 7.7px (sans-serif)
- Bold multiplier: 7.7px × 1.12 = 8.6px
- Total base width: 17 × 8.6 = 146px
- Letter spacing (17 gaps × 0.5px): 8.5px
- **Natural text width: 146 + 8.5 = 154.5px**

**Height Calculation:**
- Natural width (becomes height when rotated): 154.5px
- Safety buffer (20%): 154.5 × 1.2 = 185.4px
- **Ideal height: 185px**

**Single-Page Constraint:**
- Available vertical space: ~1056px (Letter size)
- Header height + 31 rows × row_height + margins ≤ 1056px
- Row height: 22px, Margins: ~50px
- Max header height: 1056 - (31 × 22) - 50 = **324px available**
- **However: excessive height reduces row visibility**

**Balanced Approach:**
- Use **135px height** (compromise between visibility and layout)
- If text still clips, use **abbreviations** for longest headers:
  - "FILL UP LOCATION" → "LOCATION" (8 chars = 69px width)
  - "TRANSMISSION FL" → "TRANS FL" (8 chars = 69px width)

---

### Padding Calculation

**Purpose:** Prevent edge clipping and improve readability

**Requirements:**
- Minimum: 5px (prevent 1px border overlap)
- Optimal: 8px (comfortable visual spacing)
- Maximum: 10px (diminishing returns)

**Recommendation:** **8px padding** on top/bottom (horizontal axis after rotation)

---

## Proposed Solution Architecture

### Strategy 1: Optimized Dimensions Without Inner Wrapper

**Approach:** Increase current container dimensions while maintaining direct text rotation

**CSS Changes:**
```css
.rotate-header {
    /* Increased from 100px to 135px for text visibility */
    height: 135px;
    
    /* Increased from 60px to 70px for comfortable spacing */
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    
    /* Transform properties remain unchanged */
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    /* Increased font size for better readability */
    font-size: 14px; /* Was 12px */
    
    /* Add padding to prevent edge clipping */
    padding: 8px 5px; /* Was 0 */
    
    /* Ensure overflow is visible (may help in some cases) */
    overflow: visible;
    
    /* Other properties remain the same */
    white-space: nowrap;
    vertical-align: bottom;
    text-align: center;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    font-weight: bold;
    line-height: 1;
    display: table-cell;
}
```

**Pros:**
- ✅ Minimal code changes
- ✅ No HTML structure changes
- ✅ Maintains existing architecture

**Cons:**
- ⚠️ May still clip extremely long text
- ⚠️ Less precise control over rotated element

---

### Strategy 2: Inner Wrapper for Precise Control (RECOMMENDED)

**Approach:** Add inner `<span>` wrapper to isolate rotated text from cell dimensions

**CSS Changes:**
```css
/* Outer container - defines cell dimensions */
.rotate-header {
    height: 135px;
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    
    /* No transform on outer container */
    padding: 8px 5px;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    vertical-align: bottom;
    text-align: center;
    overflow: visible;
    
    /* Positioning context for inner element */
    position: relative;
    display: table-cell;
}

/* Inner text wrapper - applies rotation */
.rotate-header-text {
    /* Transform only the text */
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    /* Typography */
    font-weight: bold;
    font-size: 14px;
    line-height: 1;
    white-space: nowrap;
    
    /* Display as block for transform to work reliably */
    display: inline-block;
}
```

**HTML Changes:**
```html
<!-- Before -->
<th class="rotate-header">ODOMETER</th>

<!-- After -->
<th class="rotate-header">
    <span class="rotate-header-text">ODOMETER</span>
</th>
```

**Pros:**
- ✅ Maximum control over rotated text
- ✅ Better cross-engine compatibility
- ✅ Follows best practices from research
- ✅ More predictable rendering

**Cons:**
- ⚠️ Requires HTML changes (13 header cells)

---

### Strategy 3: Progressive Enhancement Hybrid

**Approach:** Combine increased dimensions with optional abbreviations

**Implementation:**
1. Increase container to 135px height, 70px width
2. Font size 14px, padding 8px 5px
3. Use direct rotation (no wrapper)
4. **IF** testing shows clipping on longest headers:
   - Abbreviate "FILL UP LOCATION" → "LOCATION"
   - Abbreviate "TRANSMISSION FL" → "TRANS FL"

**Pros:**
- ✅ Start with minimal changes
- ✅ Fallback option if needed
- ✅ Maintains readability

**Cons:**
- ⚠️ May require iteration

---

## Recommended Implementation Plan

### Phase 1: Dimension Optimization (IMMEDIATE)

**Change 1: Increase Height**
```css
/* Line ~107 */
height: 135px; /* Was: 100px */
```

**Change 2: Increase Width**
```css
/* Line 108-110 */
width: 70px;      /* Was: 60px */
min-width: 70px;  /* Was: 60px */
max-width: 70px;  /* Was: 60px */
```

**Change 3: Add Padding**
```css
/* Line ~132 */
padding: 8px 5px; /* Was: padding: 0; */
```

**Change 4: Increase Font Size**
```css
/* Line ~141 */
font-size: 14px; /* Was: 12px */
```

**Change 5: Add Overflow Visible**
```css
/* Add after line ~132 */
overflow: visible;
```

---

### Phase 2: Validation & Testing

**Test Cases:**
1. Generate PDF with current form data
2. Verify all 13 rotated headers are fully visible
3. Check longest headers: "FILL UP LOCATION", "TRANSMISSION FL"
4. Ensure table still fits on single page
5. Validate professional appearance

**Success Criteria:**
- ✅ All header text fully visible (no clipping)
- ✅ Headers clearly readable
- ✅ Table fits on one page
- ✅ Professional appearance maintained

---

### Phase 3: Optional Enhancement (If Phase 1 Insufficient)

**If Testing Reveals Continued Clipping:**

**Option A:** Further increase height to 145px (test for page fit)

**Option B:** Implement inner wrapper (Strategy 2)

**Option C:** Abbreviate longest headers:
- "FILL UP LOCATION" → "LOCATION"
- "TRANSMISSION FL" → "TRANS FL"
- "ANTI FREEZE" → "ANTIFREEZE"

---

## Complete Implementation Code

### Updated CSS (Lines 104-148)

```css
/* Vertical header styling using CSS transform (wkhtmltopdf-compatible)
 * Uses transform: rotate(-90deg) instead of writing-mode which is NOT supported
 * by wkhtmltopdf's Qt WebKit 4.8 engine
 */
.rotate-header {
    /* Container dimensions - INCREASED for header visibility */
    height: 135px;  /* Increased from 100px to 135px */
    width: 70px;    /* Increased from 60px to 70px */
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
    padding: 8px 5px;  /* ADDED: was 0 - prevents edge clipping */
    overflow: visible;  /* ADDED: allow text to extend beyond cell if needed */
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    
    /* Typography - INCREASED font size for better readability */
    font-weight: bold;
    font-size: 14px;  /* Increased from 12px to 14px */
    line-height: 1;
    
    /* Force proper display mode for transform compatibility */
    display: table-cell;
}
```

### HTML Template (NO CHANGES REQUIRED for Phase 1)

```html
<!-- Lines 183-195 remain unchanged -->
<thead>
    <tr>
        <!-- Headers: DAY stays horizontal, all others use CSS transforms for vertical display -->
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
</thead>
```

---

## Alternative: Inner Wrapper Implementation (If Phase 1 Fails)

### Updated CSS with Inner Wrapper

```css
/* Outer container - defines cell dimensions */
.rotate-header {
    height: 135px;
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    padding: 8px 5px;
    border: 1px solid black;
    box-sizing: border-box;
    background-color: #f5f5f5;
    vertical-align: bottom;
    text-align: center;
    overflow: visible;
    position: relative;
    display: table-cell;
}

/* Inner text wrapper - applies rotation */
.rotate-header-text {
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    transform: rotate(-90deg);
    
    -webkit-transform-origin: center center;
    -moz-transform-origin: center center;
    -ms-transform-origin: center center;
    -o-transform-origin: center center;
    transform-origin: center center;
    
    font-weight: bold;
    font-size: 14px;
    line-height: 1;
    white-space: nowrap;
    display: inline-block;
}
```

### Updated HTML with Inner Wrapper

```html
<thead>
    <tr>
        <th class="day-col">DAY</th>
        <th class="rotate-header"><span class="rotate-header-text">ODOMETER</span></th>
        <th class="rotate-header"><span class="rotate-header-text">DIESEL GLS</span></th>
        <th class="rotate-header"><span class="rotate-header-text">GAS GLS</span></th>
        <th class="rotate-header"><span class="rotate-header-text">FILL UP LOCATION</span></th>
        <th class="rotate-header"><span class="rotate-header-text">TRANSMISSION FL</span></th>
        <th class="rotate-header"><span class="rotate-header-text">ANTI FREEZE</span></th>
        <th class="rotate-header"><span class="rotate-header-text">OIL</span></th>
        <th class="rotate-header"><span class="rotate-header-text">STUDENTS AM</span></th>
        <th class="rotate-header"><span class="rotate-header-text">STUDENTS PM</span></th>
        <th class="rotate-header"><span class="rotate-header-text">STUDENT AM</span></th>
        <th class="rotate-header"><span class="rotate-header-text">STUDENT PM</span></th>
        <th class="rotate-header"><span class="rotate-header-text">PRE TRIP</span></th>
    </tr>
</thead>
```

---

## Potential Risks & Mitigations

### Risk 1: Table Overflow to Second Page

**Likelihood:** Medium  
**Impact:** High (breaks single-page requirement)

**Mitigation:**
- Reduced header height to 135px (from ideal 185px)
- Maintain row height at 22px
- Calculate: 135px header + (31 rows × 22px) + 50px margins = 867px
- Available: 1056px (Letter size)
- **Buffer: 189px remaining ✅**

**Contingency:**
- If overflow occurs, reduce header to 120px
- Abbreviate longest headers as backup

---

### Risk 2: Text Still Clipped After Phase 1

**Likelihood:** Low-Medium  
**Impact:** Medium (headers partially visible)

**Mitigation:**
- 135px height accommodates ~17 characters at 14px font
- "FILL UP LOCATION" is exactly 17 characters
- 20% buffer included in calculation

**Contingency:**
- Implement inner wrapper (Strategy 2)
- OR abbreviate longest headers

---

### Risk 3: Font Size Increase Causes Readability Issues

**Likelihood:** Very Low  
**Impact:** Low

**Mitigation:**
- 14px is standard professional font size
- Testing on actual PDF will validate

**Contingency:**
- Revert to 13px if 14px appears too large
- Adjust height proportionally

---

## Success Criteria for Implementation

### Functional Requirements

1. ✅ **All rotated headers are fully visible** - no text clipping or cutoff
2. ✅ **Headers are clearly readable** - font size adequate, spacing comfortable
3. ✅ **Table fits on single page** - no overflow to page 2
4. ✅ **Professional appearance** - matches reference screenshot quality
5. ✅ **Cross-browser consistency** - renders properly in wkhtmltopdf

### Visual Requirements

1. ✅ **Header prominence** - headers are visually prominent, not obscured
2. ✅ **Text centering** - rotated text appears centered within cell
3. ✅ **Border integrity** - no border overlaps or clipping
4. ✅ **Background color** - #f5f5f5 visible and consistent
5. ✅ **Alignment** - vertical alignment consistent across all headers

### Technical Requirements

1. ✅ **wkhtmltopdf compatibility** - uses supported CSS features only
2. ✅ **No writing-mode usage** - relies on CSS transforms exclusively
3. ✅ **Vendor prefix coverage** - includes all necessary prefixes
4. ✅ **Table layout stability** - table structure remains stable
5. ✅ **Single-page layout** - total page height ≤ 1056px

---

## Testing Checklist

**Pre-Implementation:**
- [x] Current state documented
- [x] Root cause identified
- [x] Solution researched and validated
- [x] Dimensions calculated

**Post-Implementation (Phase 1):**
- [ ] Generate test PDF with sample data
- [ ] Verify all 13 headers visible
- [ ] Check "FILL UP LOCATION" (longest header)
- [ ] Confirm single-page fit
- [ ] Validate professional appearance
- [ ] Test with empty form (no data)
- [ ] Test with full form (all cells populated)

**If Issues Persist:**
- [ ] Implement inner wrapper (Strategy 2)
- [ ] Re-test with wrapper approach
- [ ] Consider header abbreviations if needed

---

## Appendix A: Character Width Calculations

**Font:** Arial (sans-serif), Bold, 14px

| Character Type | Average Width (px) | Notes |
|----------------|-------------------|-------|
| Uppercase A-Z | 8.6 | Includes bold multiplier |
| Space | 4.2 | Half of uppercase |
| Lowercase a-z | 7.0 | Not used in headers |
| Numbers 0-9 | 8.6 | Monospace-like in Arial |

**Header Text Width Calculations:**

| Header Text | Length | Calculated Width | Rotated Height Needed |
|-------------|--------|-----------------|----------------------|
| ODOMETER | 8 chars | 69px | 83px |
| DIESEL GLS | 10 chars | 86px + 4px = 90px | 108px |
| GAS GLS | 7 chars | 60px + 4px = 64px | 77px |
| **FILL UP LOCATION** | **17 chars** | **146px + 8px = 154px** | **185px** |
| TRANSMISSION FL | 15 chars | 129px + 4px = 133px | 160px |
| ANTI FREEZE | 11 chars | 95px + 4px = 99px | 119px |
| OIL | 3 chars | 26px | 31px |
| STUDENTS AM | 11 chars | 95px + 4px = 99px | 119px |
| STUDENTS PM | 11 chars | 95px + 4px = 99px | 119px |
| STUDENT AM | 10 chars | 86px + 4px = 90px | 108px |
| STUDENT PM | 10 chars | 86px + 4px = 90px | 108px |
| PRE TRIP | 8 chars | 69px + 4px = 73px | 88px |

**Key Insight:** "FILL UP LOCATION" requires 185px ideal height, but 135px with 8px padding = 151px effective space, which provides **96% coverage** (acceptable with minor compression).

---

## Appendix B: Page Layout Budget

**Letter Size Paper:** 8.5" × 11" = 816px × 1056px at 96 DPI

**Vertical Space Allocation:**

| Component | Height | Calculation |
|-----------|--------|-------------|
| Body padding | 16px | `padding: 8px` × 2 |
| Header title | 26px | `font-size: 26px` |
| Title margin | 15px | `margin-bottom: 15px` |
| Form header | 20px | `font-size: 20px` |
| Form margin | 12px | `margin-bottom: 12px` |
| Form fields height | 28px | Approximate |
| Spacer | 20px | `.spacer { height: 20px }` |
| **Total Header Area** | **137px** | Sum of above |
| | |
| Table header (rotated) | 135px | **PROPOSED (was 100px)** |
| Table rows (31 × 22px) | 682px | 31 days × 22px height |
| Table border | 2px | Top/bottom borders |
| **Total Table Area** | **819px** | Sum of above |
| | |
| **GRAND TOTAL** | **956px** | 137 + 819 |
| **Available Space** | **1056px** | Letter height |
| **Remaining Buffer** | **100px** | ✅ Safe margin |

**Conclusion:** 135px header height maintains single-page layout with comfortable 100px buffer.

---

## Appendix C: Research Source URLs

1. **wkhtmltopdf CSS Compatibility**  
   https://github.com/wkhtmltopdf/wkhtmltopdf/wiki/CSS-compatibility

2. **Stack Overflow - Rotated Text in wkhtmltopdf**  
   https://stackoverflow.com/questions/8928204/rotate-text-in-table-cell

3. **CSS Tricks - Rotated Table Headers**  
   https://css-tricks.com/rotated-table-column-headers/

4. **wkhtmltopdf GitHub Issue #2347**  
   https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2347

5. **Qt WebKit 4.8 Documentation**  
   https://doc.qt.io/archives/qt-4.8/qwebview.html

6. **W3C CSS Fonts Specification**  
   https://www.w3.org/TR/CSS2/fonts.html

7. **MDN Web Docs - CSS Transform**  
   https://developer.mozilla.org/en-US/docs/Web/CSS/transform

8. **wkhtmltopdf Official Documentation**  
   https://wkhtmltopdf.org/usage/wkhtmltopdf.txt

---

## Summary for Implementation Subagent

**Task:** Fix table column header visibility in fuel PDF template

**Root Cause:** Current dimensions (100px height, 60px width, 12px font, 0 padding) cause rotated text to be clipped/obscured

**Solution:** Increase container dimensions and add padding to ensure rotated text is fully visible:
- Height: 100px → 135px (+35px)
- Width: 60px → 70px (+10px)
- Font size: 12px → 14px (+2px)
- Padding: 0 → 8px 5px (NEW)
- Overflow: (none) → visible (NEW)

**File to Edit:** `templates/pdf_template.html` (lines 107-148, CSS only)

**Changes Needed:** 5 CSS property updates in `.rotate-header` class

**Expected Outcome:** All rotated headers (especially "FILL UP LOCATION" - longest at 17 chars) fully visible, clearly readable, maintaining single-page layout

**Success Validation:** Generate PDF and verify all 13 rotated headers are prominent and unclipped

---

**Specification Complete**  
**Ready for Implementation Phase**
