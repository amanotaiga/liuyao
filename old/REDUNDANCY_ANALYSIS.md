# Redundancy Analysis for gradio_ui.py

## Summary of Redundant Code

### 1. **Duplicate Hexagram Line HTML Creation Functions**

**Location 1:** `create_line_html()` (lines 1496-1526)
**Location 2:** `create_clickable_line_html()` (lines 1801-1830)

**Issue:** These two functions are nearly identical. The only differences are:
- Yin line spacing: `"▅▅  ▅▅"` vs `"▅▅     ▅▅"` (extra spaces in clickable version)
- Cursor style: clickable version has `cursor: pointer` in the HTML

**Recommendation:** Merge into a single function with a `clickable` parameter.

---

### 2. **Repeated Hexagram Line Styling Logic**

The same color/styling logic (bg_color, border_color, text_color, shadow) is duplicated in multiple places:

- `create_hexagram_html()` (lines 62-77)
- `create_line_html()` (lines 1498-1513)
- `create_clickable_line_html()` (lines 1804-1817)
- `update_hexagram_lines()` (lines 1653-1668) - inline styling
- `update_clickable_hexagram_display()` (lines 1874) - uses function but also has inline styling

**Recommendation:** Extract styling logic into a helper function like:
```python
def get_line_style(is_yang: bool, is_changing: bool) -> dict:
    """Returns dict with bg_color, border_color, text_color, shadow"""
```

---

### 3. **Duplicate Changed Hexagram HTML Creation**

**Location 1:** `update_hexagram_lines()` (lines 1684-1709)
**Location 2:** `update_clickable_hexagram_display()` (lines 1877-1901)

**Issue:** Both functions contain identical code for creating changed hexagram line HTML. The logic for determining colors and creating the HTML string is exactly the same.

**Recommendation:** Extract into a shared function:
```python
def create_changed_line_html(changed_code: str, line_num: int) -> str:
    """Create HTML for a changed hexagram line"""
```

---

### 4. **Duplicate Processing Functions**

**Location 1:** `process_regular_tab()` (lines 2174-2220)
**Location 2:** `process_clickable_tab()` (lines 2223-2253)

**Issue:** These functions have nearly identical logic:
- Same date method determination
- Same `process_divination()` call structure
- Only difference is how hexagram code is extracted

**Recommendation:** Merge into a single function with a parameter for hexagram code extraction method.

---

### 5. **Unused Function**

**Location:** `toggle_yao_line()` (lines 1833-1845)

**Issue:** This function is defined but never called. The actual toggle logic is implemented directly in `handle_line_click()` (lines 1991-2034).

**Recommendation:** Remove this unused function.

---

### 6. **Unused/Redundant Hexagram Preview**

**Location:** `hexagram_preview` (lines 1716-1720)

**Issue:** This component is created but set to `visible=False` and never used. The comment says "for reference, can be removed if not needed".

**Recommendation:** Remove if not needed, or use it if it was intended to be displayed.

---

### 7. **Duplicate Checkbox Mapping Logic**

**Location 1:** `process_regular_tab()` (lines 2201-2208)
**Location 2:** `process_clickable_tab()` (lines 2235-2241)

**Issue:** Both functions map checkbox values to changing lines with identical logic, just different variable names.

**Recommendation:** Extract into a helper function:
```python
def map_checkboxes_to_changing_lines(yao1, yao2, yao3, yao4, yao5, yao6) -> List[int]:
    """Map checkbox values to list of changing line numbers"""
```

---

### 8. **Repeated Changed Hexagram Code Calculation**

**Location 1:** `update_hexagram_lines()` (lines 1638-1639)
**Location 2:** `update_clickable_hexagram_display()` (lines 1861-1862)

**Issue:** Both functions calculate the changed hexagram code using the same logic.

**Recommendation:** Already using `calculate_changed_hexagram()` function, which is good. No change needed here.

---

## Estimated Code Reduction

If all redundancies are eliminated:
- **~150-200 lines** could be removed or consolidated
- **~5-7 functions** could be merged or extracted
- **Maintainability** would significantly improve

## Priority Recommendations

1. **High Priority:** Merge `create_line_html()` and `create_clickable_line_html()` (saves ~30 lines)
2. **High Priority:** Extract hexagram line styling logic (saves ~50 lines across multiple locations)
3. **Medium Priority:** Extract changed hexagram HTML creation (saves ~30 lines)
4. **Medium Priority:** Merge processing functions (saves ~40 lines)
5. **Low Priority:** Remove unused `toggle_yao_line()` function (saves ~13 lines)
6. **Low Priority:** Remove unused `hexagram_preview` if not needed (saves ~5 lines)

