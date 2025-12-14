"""
HTML generation utilities for hexagram visualization

Functions for generating HTML representations of hexagrams,
lines, and related UI elements.
"""

from functools import lru_cache
from typing import List, Dict
from ..config import COLOR_CONFIG, UI_CONFIG


def get_line_style(is_yang: bool, is_changing: bool) -> Dict[str, str]:
    """
    Get styling properties for a hexagram line
    
    Args:
        is_yang: True for yang line, False for yin line
        is_changing: True if line is changing
    
    Returns:
        Dictionary with line_html, line_class, bg_color, border_color, text_color, shadow
    """
    if is_yang:
        line_html = UI_CONFIG.line_symbol_yang
        line_class = "yang"
        bg_color = COLOR_CONFIG.yang_bg_changing if is_changing else COLOR_CONFIG.yang_bg
        border_color = COLOR_CONFIG.yang_border_changing if is_changing else COLOR_CONFIG.yang_border
        text_color = COLOR_CONFIG.yang_text_changing if is_changing else COLOR_CONFIG.yang_text
        shadow = COLOR_CONFIG.yang_shadow_changing if is_changing else COLOR_CONFIG.yang_shadow
    else:
        line_html = UI_CONFIG.line_symbol_yin
        line_class = "yin"
        bg_color = COLOR_CONFIG.yin_bg_changing if is_changing else COLOR_CONFIG.yin_bg
        border_color = COLOR_CONFIG.yin_border_changing if is_changing else COLOR_CONFIG.yin_border
        text_color = COLOR_CONFIG.yin_text_changing if is_changing else COLOR_CONFIG.yin_text
        shadow = COLOR_CONFIG.yin_shadow_changing if is_changing else COLOR_CONFIG.yin_shadow
    
    return {
        "line_html": line_html,
        "line_class": line_class,
        "bg_color": bg_color,
        "border_color": border_color,
        "text_color": text_color,
        "shadow": shadow
    }


@lru_cache(maxsize=500)
def create_line_html(code: str, line_num: int, is_changing: bool, clickable: bool = False) -> str:
    """
    Create HTML for a hexagram line (unified function for both regular and clickable)
    
    Args:
        code: Hexagram code (6 digits)
        line_num: Line number (1-6)
        is_changing: Whether the line is changing
        clickable: Whether the line should be clickable (adds cursor pointer)
    
    Returns:
        HTML string for the line
    """
    is_yang = code[line_num - 1] == '1'
    style = get_line_style(is_yang, is_changing)
    
    # Adjust yin line spacing for clickable version
    if not is_yang and clickable:
        style["line_html"] = UI_CONFIG.line_symbol_yin_clickable
    
    change_mark = ""
    if is_changing:
        change_mark = UI_CONFIG.change_mark_yang if is_yang else UI_CONFIG.change_mark_yin
    
    cursor_style = "cursor: pointer;" if clickable else ""
    extra_spacing = "  " if clickable else ""
    
    # Add kanji for mobile display
    kanji = "陽" if is_yang else "陰"
    
    return f"""
    <div class="hexagram-line {style['line_class']}" style="font-size: 26px; color: {style['text_color']}; font-weight: {'600' if is_changing else '400'}; padding: 12px 20px; border: 1.5px solid {style['border_color']}; border-radius: 8px; background: {style['bg_color']}; transition: all 0.3s ease; box-shadow: {style['shadow']}; text-align: center; width: 100%; min-height: 64px; height: 64px; display: flex; align-items: center; justify-content: center; box-sizing: border-box; {cursor_style}">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
            <span class="line-symbol-desktop" style="font-family: 'SimSun', '宋体', monospace;">{style['line_html']}</span>
            <span class="line-symbol-mobile" style="font-family: 'SimSun', '宋体', monospace;">{kanji}</span>
            <span style="font-size: 13px; color: #000000; font-weight: 600; letter-spacing: 0.5px;">{extra_spacing}{line_num}爻 {change_mark}</span>
        </div>
    </div>
    """


@lru_cache(maxsize=500)
def create_changed_line_html(changed_code: str, line_num: int) -> str:
    """
    Create HTML for a changed hexagram line (no changing marks, always static)
    
    Args:
        changed_code: Changed hexagram code (6 digits)
        line_num: Line number (1-6)
    
    Returns:
        HTML string for the changed line
    """
    code_index = line_num - 1
    is_yang = changed_code[code_index] == '1'
    style = get_line_style(is_yang, False)  # Changed lines are never marked as changing
    
    # Add kanji for mobile display
    kanji = "陽" if is_yang else "陰"
    
    return f"""
    <div class="hexagram-line {style['line_class']}" style="font-size: 26px; color: {style['text_color']}; font-weight: 400; padding: 12px 20px; border: 1.5px solid {style['border_color']}; border-radius: 8px; background: {style['bg_color']}; transition: all 0.3s ease; box-shadow: {style['shadow']}; text-align: center; width: 100%; min-height: 64px; height: 64px; display: flex; align-items: center; justify-content: center; box-sizing: border-box;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
            <span class="line-symbol-desktop" style="font-family: 'SimSun', '宋体', monospace;">{style['line_html']}</span>
            <span class="line-symbol-mobile" style="font-family: 'SimSun', '宋体', monospace;">{kanji}</span>
            <span style="font-size: 13px; color: #000000; font-weight: 600; letter-spacing: 0.5px;">  {line_num}爻</span>
        </div>
    </div>
    """


def create_hexagram_html(hexagram_code: str, changing_lines: List[int] = None) -> str:
    """
    Create HTML visualization of hexagram with elegant card-based design
    
    Args:
        hexagram_code: 6-digit string ('1'=yang, '0'=yin, from bottom to top)
        changing_lines: List of line positions (1-6) that are changing
    
    Returns:
        HTML string with styled hexagram
    """
    if changing_lines is None:
        changing_lines = []
    
    if len(hexagram_code) != 6:
        return "<p>Invalid hexagram code</p>"
    
    html = """
    <div class="hexagram-container" style="text-align: center; font-family: 'SimSun', '宋体', monospace; padding: 24px; background: #ffffff; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2), 0 2px 6px rgba(0,0,0,0.15); border: 2px solid #000000;">
        <h3 class="hexagram-title" style="margin-bottom: 20px; color: #000000; font-weight: 800; font-size: 18px; letter-spacing: 0.5px;">卦象</h3>
        <div style="display: flex; flex-direction: column-reverse; align-items: center; gap: 12px;">
    """
    
    # Draw from bottom to top (1 at bottom, 6 at top)
    # hexagram_code[0] is line 1 (bottom), hexagram_code[5] is line 6 (top)
    # Using column-reverse, so we iterate 0 to 5 to get 1 at bottom, 6 at top
    for i in range(6):
        line_num = i + 1  # 1 to 6 from bottom to top
        is_changing = line_num in changing_lines
        line_html = create_line_html(hexagram_code, line_num, is_changing, clickable=False)
        # Adjust padding for this specific display (12px instead of 14px, max-width constraint)
        line_html = line_html.replace("padding: 14px 20px;", "padding: 12px 20px;")
        line_html = line_html.replace("width: 100%; min-height: 64px;", "width: 100%; max-width: 280px;")
        html += line_html
    
    html += """
        </div>
        <p class="hexagram-footer" style="margin-top: 18px; color: #000000; font-size: 12px; font-weight: 600; letter-spacing: 0.3px;">
            從下往上：""" + " → ".join([f"{i+1}爻" for i in range(6)]) + """</p>
    </div>
    """
    
    return html

