"""
Gradio UI for Liu Yao Divination System

A web-based interface for the Liu Yao divination system with multiple input methods
and comprehensive result display.
"""

import gradio as gr
from typing import List, Optional, Tuple, Dict
from datetime import datetime

# Import from existing modules
from liu_yao import (
    six_yao_divination,
    HEXAGRAM_MAP,
    format_liu_yao_display,
    bazi_from_date_string,
    display_shen_sha_definitions
)
from ba_zi_base import Pillar, BaZi
from test_liu_yao import format_divination_results


# Constants
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


# Helper functions for hexagram line styling
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
        line_html = "▅▅▅▅▅▅"
        line_class = "yang"
        bg_color = "#e96a6a" if is_changing else "#ef4444"
        border_color = "#d32f2f" if is_changing else "#b71c1c"
        text_color = "#b71c1c" if is_changing else "#8b0000"
        shadow = "0 2px 6px rgba(211, 47, 47, 0.5)" if is_changing else "0 1px 3px rgba(183, 28, 28, 0.4)"
    else:
        line_html = "▅▅  ▅▅"
        line_class = "yin"
        bg_color = "#64db68" if is_changing else "#75cc0d"
        border_color = "#2e7d32" if is_changing else "#1b5e20"
        text_color = "#1b5e20" if is_changing else "#0d4f0d"
        shadow = "0 2px 6px rgba(46, 125, 50, 0.5)" if is_changing else "0 1px 3px rgba(27, 94, 32, 0.4)"
    
    return {
        "line_html": line_html,
        "line_class": line_class,
        "bg_color": bg_color,
        "border_color": border_color,
        "text_color": text_color,
        "shadow": shadow
    }


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
        style["line_html"] = "▅▅     ▅▅"
    
    change_mark = ""
    if is_changing:
        change_mark = " ○" if is_yang else " ×"
    
    cursor_style = "cursor: pointer;" if clickable else ""
    extra_spacing = "  " if clickable else ""
    
    return f"""
    <div class="hexagram-line {style['line_class']}" style="font-size: 26px; color: {style['text_color']}; font-weight: {'600' if is_changing else '400'}; padding: 14px 20px; border: 1.5px solid {style['border_color']}; border-radius: 8px; background: {style['bg_color']}; transition: all 0.3s ease; box-shadow: {style['shadow']}; text-align: center; width: 100%; min-height: 64px; display: flex; align-items: center; justify-content: center; {cursor_style}">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
            <span style="font-family: 'SimSun', '宋体', monospace;">{style['line_html']}</span>
            <span style="font-size: 13px; color: #000000; font-weight: 600; letter-spacing: 0.5px;">{extra_spacing}{line_num}爻 {change_mark}</span>
        </div>
    </div>
    """


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
    
    return f"""
    <div class="hexagram-line {style['line_class']}" style="font-size: 26px; color: {style['text_color']}; font-weight: 400; padding: 14px 20px; border: 1.5px solid {style['border_color']}; border-radius: 8px; background: {style['bg_color']}; transition: all 0.3s ease; box-shadow: {style['shadow']}; text-align: center; width: 100%; min-height: 64px; display: flex; align-items: center; justify-content: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
            <span style="font-family: 'SimSun', '宋体', monospace;">{style['line_html']}</span>
            <span style="font-size: 13px; color: #000000; font-weight: 600; letter-spacing: 0.5px;">  {line_num}爻</span>
        </div>
    </div>
    """


def map_checkboxes_to_changing_lines(yao1, yao2, yao3, yao4, yao5, yao6) -> List[int]:
    """
    Map checkbox values to list of changing line numbers
    
    Args:
        yao1-yao6: Checkbox values (in visual order: 6,5,4,3,2,1 from top to bottom)
    
    Returns:
        List of changing line numbers (1-6)
    """
    changing = []
    checkbox_values = [yao1, yao2, yao3, yao4, yao5, yao6]
    for visual_index, is_changing in enumerate(checkbox_values):
        line_num = 6 - visual_index  # visual_index 0 -> line 6, visual_index 5 -> line 1
        if is_changing:
            changing.append(line_num)
    return changing


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


def search_hexagram_by_name(query: str) -> List[Tuple[str, str]]:
    """
    Search hexagrams by partial name match
    
    Args:
        query: Search query (e.g., "山地", "天風")
    
    Returns:
        List of tuples (hexagram_code, full_name)
    """
    if not query or len(query.strip()) == 0:
        return []
    
    query = query.strip()
    matches = []
    
    for code, info in HEXAGRAM_MAP.items():
        if query in info.name:
            matches.append((code, info.name))
    
    return matches


def process_divination(
    # Date inputs (Western)
    use_western_date: bool,
    year: int, month: int, day: int, hour: int,
    # Date inputs (Gan-Zhi) - now strings like "甲子"
    year_pillar_str: str, year_branch_placeholder: str,
    month_pillar_str: str, month_branch_placeholder: str,
    day_pillar_str: str, day_branch_placeholder: str,
    hour_pillar_str: str, hour_branch_placeholder: str,
    # Yao inputs (Button method)
    use_button_method: bool,
    yao1_type, yao1_changing, yao2_type, yao2_changing,
    yao3_type, yao3_changing, yao4_type, yao4_changing,
    yao5_type, yao5_changing, yao6_type, yao6_changing,
    # Yao inputs (Name method)
    hexagram_name_query: str,
    selected_hexagram_code: str,
    name_yao1_changing, name_yao2_changing, name_yao3_changing,
    name_yao4_changing, name_yao5_changing, name_yao6_changing
) -> str:
    """
    Main processing function for divination
    
    Returns:
        Formatted text output matching test_liu_yao.py format
    """
    try:
        # Step 1: Create BaZi object
        if use_western_date:
            # Use Western calendar
            try:
                # Validate date inputs
                if not (1900 <= year <= 2100):
                    return "錯誤：年份必須在1900-2100之間"
                if not (1 <= month <= 12):
                    return "錯誤：月份必須在1-12之間"
                if not (1 <= day <= 31):
                    return "錯誤：日期必須在1-31之間"
                if not (0 <= hour <= 23):
                    return "錯誤：小時必須在0-23之間"
                
                date_str = f"{year}/{month:02d}/{day:02d} {hour:02d}:00"
                print(f"DEBUG: Creating BaZi from date string: {date_str}")
                bazi = bazi_from_date_string(date_str)
                print(f"DEBUG: BaZi created - Year: {bazi.year.to_string()}, Month: {bazi.month.to_string()}, Day: {bazi.day.to_string()}, Hour: {bazi.hour.to_string()}")
            except ValueError as e:
                return f"錯誤：日期格式錯誤：{str(e)}"
            except NotImplementedError as e:
                return f"錯誤：{str(e)}"
            except Exception as e:
                return f"錯誤：無法創建八字：{str(e)}"
        else:
            # Use Gan-Zhi calendar
            try:
                # year_pillar_str, etc. are now strings like "甲子"
                # Parse them to get stem and branch
                def parse_ganzhi(ganzhi_str):
                    if not ganzhi_str or len(ganzhi_str) != 2:
                        raise ValueError(f"Invalid Gan-Zhi: {ganzhi_str}")
                    return ganzhi_str[0], ganzhi_str[1]
                
                try:
                    year_stem, year_branch = parse_ganzhi(year_pillar_str if year_pillar_str else "甲子")
                    month_stem, month_branch = parse_ganzhi(month_pillar_str if month_pillar_str else "甲子")
                    day_stem, day_branch = parse_ganzhi(day_pillar_str if day_pillar_str else "甲子")
                    hour_stem, hour_branch = parse_ganzhi(hour_pillar_str if hour_pillar_str else "甲子")
                except (ValueError, IndexError) as e:
                    return f"錯誤：無效的干支：{str(e)}。請確保已選擇完整的四柱。"
                
                year_pillar = Pillar(year_stem, year_branch)
                month_pillar = Pillar(month_stem, month_branch)
                day_pillar = Pillar(day_stem, day_branch)
                hour_pillar = Pillar(hour_stem, hour_branch)
                
                # Calculate xun_kong
                xun_kong_1, xun_kong_2 = BaZi.calculate_xun_kong(day_pillar)
                bazi = BaZi(year_pillar, month_pillar, day_pillar, hour_pillar, xun_kong_1, xun_kong_2)
            except ValueError as e:
                return f"錯誤：無效的干支組合：{str(e)}"
            except Exception as e:
                return f"錯誤：無法創建八字：{str(e)}"
        
        # Step 2: Get hexagram code and changing lines
        if use_button_method:
            # From button inputs
            hexagram_code = ""
            changing_lines = []
            
            yao_inputs = [
                (yao1_type, yao1_changing, 1),
                (yao2_type, yao2_changing, 2),
                (yao3_type, yao3_changing, 3),
                (yao4_type, yao4_changing, 4),
                (yao5_type, yao5_changing, 5),
                (yao6_type, yao6_changing, 6),
            ]
            
            for yao_type, yao_changing, line_num in yao_inputs:
                if yao_type == "陽":
                    hexagram_code += "1"
                    if yao_changing:
                        changing_lines.append(line_num)
                elif yao_type == "陰":
                    hexagram_code += "0"
                    if yao_changing:
                        changing_lines.append(line_num)
                else:
                    hexagram_code += "0"  # Default
        else:
            # From name input
            if not selected_hexagram_code or len(selected_hexagram_code) != 6:
                # Try to search by name
                matches = search_hexagram_by_name(hexagram_name_query)
                if not matches:
                    return f"錯誤：無法找到包含 '{hexagram_name_query}' 的卦象"
                elif len(matches) > 1:
                    return f"錯誤：找到多個匹配的卦象，請從下拉列表中選擇：{', '.join([name for _, name in matches])}"
                else:
                    hexagram_code = matches[0][0]
            else:
                hexagram_code = selected_hexagram_code
            
            # Get changing lines from checkboxes
            # Use the passed changing lines (from clickable tab) if they're provided
            # Otherwise use the name tab checkboxes
            changing_lines = []
            # Check if any of the name_yao*_changing values are actually from clickable tab
            # (they will be True/False values, not None)
            changing_checkboxes = [
                name_yao1_changing, name_yao2_changing, name_yao3_changing,
                name_yao4_changing, name_yao5_changing, name_yao6_changing
            ]
            for i, is_changing in enumerate(changing_checkboxes):
                if is_changing:
                    changing_lines.append(i + 1)
            
            print(f"DEBUG process_divination: hexagram_code={hexagram_code}, changing_lines={changing_lines}")
        
        # Step 3: Validate hexagram code
        if hexagram_code not in HEXAGRAM_MAP:
            return f"錯誤：無效的卦象代碼：{hexagram_code}"
        
        # Step 4: Perform divination
        try:
            yao_list, result_json = six_yao_divination(hexagram_code, bazi, changing_lines)
        except KeyError as e:
            return f"錯誤：卦象數據缺失：{str(e)}"
        except Exception as e:
            return f"錯誤：排盤過程中出錯：{str(e)}"
        
        # Step 5: Format results using the shared function from test_liu_yao.py
        # This ensures identical output formatting
        # Pass for_gradio=True to use 5 characters for yang yao instead of 6
        return format_divination_results(bazi, result_json, yao_list, show_shen_sha=True, for_gradio=True)
    
    except Exception as e:
        return f"錯誤：發生錯誤：{str(e)}"


def update_hexagram_dropdown(query: str) -> gr.Dropdown:
    """Update hexagram dropdown based on search query"""
    matches = search_hexagram_by_name(query)
    if matches:
        choices = [f"{code} - {name}" for code, name in matches]
        return gr.Dropdown(choices=choices, value=choices[0] if choices else None)
    return gr.Dropdown(choices=[], value=None)


def get_hexagram_code_from_dropdown(dropdown_value: str) -> str:
    """Extract hexagram code from dropdown value"""
    if dropdown_value and " - " in dropdown_value:
        return dropdown_value.split(" - ")[0]
    return dropdown_value if dropdown_value else ""


def calculate_changed_hexagram(original_code: str, changing_line_nums: List[int]) -> str:
    """Calculate the changed hexagram code by flipping changing lines
    
    Args:
        original_code: Original hexagram code (6 digits)
        changing_line_nums: List of line numbers (1-6) that are changing
    
    Returns:
        Changed hexagram code
    """
    if not original_code or len(original_code) != 6:
        return "111111"
    
    changed_code = list(original_code)
    for line_num in changing_line_nums:
        if 1 <= line_num <= 6:
            index = line_num - 1  # Convert to 0-based index
            # Flip: 0 -> 1, 1 -> 0
            changed_code[index] = '1' if changed_code[index] == '0' else '0'
    
    return ''.join(changed_code)


# Create the Gradio interface
def create_ui():
    """Create and return the Gradio interface"""
    
    # Custom CSS for elegant, refined styling
    custom_css = """
    <style>
        /* Base Typography */
        body {
            font-family: 'Microsoft YaHei', '微软雅黑', 'SimSun', '宋体', sans-serif;
            color: #000000;
            background-color: #ffffff;
        }
        
        /* Main Container */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Hexagram Line Styling */
        .hexagram-line {
            font-family: 'SimSun', '宋体', monospace;
            transition: all 0.3s ease;
        }
        .hexagram-line:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        }
        .hexagram-line.yang {
            color: #d32f2f;
        }
        .hexagram-line.yin {
            color: #2e7d32;
        }
        .hexagram-line.changing {
            font-weight: 600;
        }
        .hexagram-line-container {
            margin: 4px 0;
        }
        
        /* Gan-Zhi Button Styling */
        .ganzhi-button {
            min-width: 50px !important;
            font-family: 'SimSun', '宋体', monospace;
            font-size: 16px;
            padding: 10px 14px;
            margin: 3px;
            border-radius: 8px;
            transition: all 0.25s ease;
            background-color: #ffffff;
            border: 2px solid #000000;
            color: #000000;
            font-weight: 600;
        }
        .ganzhi-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
            border-color: #000000;
            background-color: #f0f0f0;
        }
        .ganzhi-button:active,
        .ganzhi-button.clicked {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-color: #000000 !important;
            transform: translateY(0px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        }
        .ganzhi-button.clicked {
            animation: buttonClick 0.3s ease;
        }
        @keyframes buttonClick {
            0% { transform: scale(1); }
            50% { transform: scale(0.95); }
            100% { transform: scale(1); }
        }
        
        /* Yao Line Button Styling - Match 變卦 styling */
        .yao-line-button {
            font-family: 'SimSun', '宋体', monospace;
            font-size: 26px;
            font-weight: 400;
            padding: 20px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            min-height: 70px;
            text-align: center;
            width: 100%;
            max-width: 350px;
            margin: 4px 0;
            margin-left: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        /* Container for 本卦 buttons - align to right */
        .hexagram-display-row .column-spacing:first-child {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        
        .hexagram-display-row .column-spacing:first-child > * {
            width: 100%;
            max-width: 350px;
        }
        /* Yang line buttons (red) - use multiple selectors for robustness */
        button.yao-line-button.yang-button,
        .yao-line-button.yang-button,
        button.yang-button.yao-line-button {
            background-color: #ef4444 !important;
            border: 1.5px solid #b71c1c !important;
            color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(183, 28, 28, 0.4) !important;
        }
        /* Yin line buttons (green) */
        button.yao-line-button.yin-button,
        .yao-line-button.yin-button,
        button.yin-button.yao-line-button {
            background-color: #75cc0d !important;
            border: 1.5px solid #1b5e20 !important;
            color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(27, 94, 32, 0.4) !important;
        }
        /* Changing yang line buttons */
        button.yao-line-button.yang-button.changing,
        .yao-line-button.yang-button.changing,
        button.yang-button.yao-line-button.changing {
            background-color: #e96a6a !important;
            border: 1.5px solid #d32f2f !important;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(211, 47, 47, 0.5) !important;
            font-weight: 600 !important;
        }
        /* Changing yin line buttons */
        button.yao-line-button.yin-button.changing,
        .yao-line-button.yin-button.changing,
        button.yin-button.yao-line-button.changing {
            background-color: #64db68 !important;
            border: 1.5px solid #2e7d32 !important;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(46, 125, 50, 0.5) !important;
            font-weight: 600 !important;
        }
        
        /* Ensure all text inside buttons is white */
        button.yao-line-button *,
        .yao-line-button * {
            color: #ffffff !important;
        }
        .yao-line-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        }
        
        /* Changing Button Styling */
        .yao-button-changing {
            font-family: 'SimSun', '宋体', monospace;
            font-size: 18px;
            font-weight: 500;
            padding: 14px 26px;
            border-radius: 10px;
            transition: all 0.3s ease;
            min-height: 50px;
            background-color: #ffffff;
            border: 1.5px solid #dee2e6;
        }
        .yao-button-changing:hover {
            background-color: #fff8f0 !important;
            border-color: #d4a574 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(212, 165, 116, 0.2);
        }
        
        /* Line Preview */
        .line-preview {
            font-family: 'SimSun', '宋体', monospace;
            font-size: 24px;
            padding: 12px;
            text-align: center;
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        
        /* Result Table */
        .result-table {
            font-family: 'SimSun', '宋体', monospace;
            font-size: 14px;
            line-height: 1.8;
            white-space: pre;
            background-color: #ffffff;
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 20px;
            color: #000000;
        }
        
        /* Tab Styling */
        .tab-nav {
            border-bottom: 2px solid #e9ecef;
        }
        .tab-nav button {
            font-weight: 500;
            color: #6c757d;
            transition: all 0.2s ease;
        }
        .tab-nav button:hover {
            color: #495057;
        }
        .tab-nav button.selected {
            color: #212529;
            border-bottom: 2px solid #212529;
        }
        
        /* Input Styling */
        input[type="text"], input[type="number"], select, textarea {
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 10px 14px;
            transition: all 0.2s ease;
            background-color: #ffffff;
            color: #000000;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus, textarea:focus {
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.2);
            outline: none;
        }
        
        /* Dropdown Styling */
        select {
            background-color: #ffffff;
            color: #000000;
            font-weight: 500;
        }
        
        /* Checkbox Styling */
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: #000000;
            cursor: pointer;
        }
        label {
            color: #000000;
            font-weight: 500;
        }
        
        /* Changing Yao Checkbox Styling - Large Rectangular */
        .changing-yao-checkbox {
            width: 100% !important;
            min-width: 300px !important;
        }
        .changing-yao-checkbox > div,
        .changing-yao-checkbox > label,
        .changing-yao-checkbox label {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            min-height: 64px !important;
            padding: 14px 20px !important;
            margin: 0 !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
            cursor: pointer !important;
            font-size: 26px !important;
            color: #000000 !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            gap: 12px !important;
            overflow: visible !important;
        }
        .changing-yao-checkbox > div:hover,
        .changing-yao-checkbox > label:hover,
        .changing-yao-checkbox label:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
            border-color: #000000 !important;
            background: #f0f0f0 !important;
        }
        .changing-yao-checkbox input[type="checkbox"] {
            width: 28px !important;
            height: 28px !important;
            cursor: pointer !important;
            accent-color: #000000 !important;
            margin: 0 !important;
            flex-shrink: 0 !important;
        }
        .changing-yao-checkbox input[type="checkbox"]:checked ~ span,
        .changing-yao-checkbox:has(input[type="checkbox"]:checked) > div,
        .changing-yao-checkbox:has(input[type="checkbox"]:checked) > label,
        .changing-yao-checkbox:has(input[type="checkbox"]:checked) label {
            background: #fff8f0 !important;
            border-color: #d4a574 !important;
            box-shadow: 0 2px 6px rgba(212, 165, 116, 0.25) !important;
        }
        
        /* Button Styling */
        button.primary {
            background-color: #000000;
            color: #ffffff;
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 700;
            transition: all 0.2s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        button.primary:hover {
            background-color: #333333;
            border-color: #333333;
            transform: translateY(-1px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        button.secondary {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 700;
            transition: all 0.2s ease;
        }
        button.secondary:hover {
            background-color: #f0f0f0;
            border-color: #000000;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Markdown Headers */
        h1, h2, h3, h4 {
            color: #000000;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        h1 {
            font-size: 32px;
            margin-bottom: 8px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        .main-title {
            margin-bottom: 12px;
        }
        h2 {
            font-size: 22px;
            margin-bottom: 12px;
            font-weight: 700;
        }
        h3 {
            font-size: 18px;
            margin-bottom: 10px;
            color: #000000;
            font-weight: 700;
        }
        .section-header {
            margin-bottom: 12px;
        }
        
        /* Section Spacing */
        .section-divider {
            margin: 32px 0;
            border-top: 2px solid #000000;
            border-bottom: none;
        }
        
        /* Hexagram Display Row */
        .hexagram-display-row {
            margin-top: 8px;
            gap: 20px;
        }
        
        /* Card-like Containers */
        .card {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Column Spacing */
        .column-spacing {
            padding: 0 12px;
        }
        
        /* Refined Text Colors */
        .text-muted {
            color: #333333;
            line-height: 1.6 !important;
            overflow: visible !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            font-weight: 500 !important;
        }
        .text-primary {
            color: #000000;
            font-weight: 600;
        }
        
        /* Smooth Transitions */
        * {
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        }
        
        /* Dark Theme Support */
        @media (prefers-color-scheme: dark) {
            /* Base Typography - Dark Theme */
            body {
                color: #ffffff;
                background-color: #000000;
            }
            
            /* Main Container - Dark Theme */
            .main-container {
                background-color: #1a1d20;
            }
            
            /* Hexagram Line Styling - Dark Theme */
            .hexagram-line:hover {
                box-shadow: 0 4px 12px rgba(255,255,255,0.3) !important;
            }
            .hexagram-line.yang {
                color: #ff4444;
            }
            .hexagram-line.yin {
                color: #00ff00;
            }
            
            /* Gan-Zhi Button Styling - Dark Theme */
            .ganzhi-button {
                background-color: #1a1a1a;
                border: 2px solid #ffffff;
                color: #ffffff;
                font-weight: 700;
            }
            .ganzhi-button:hover {
                box-shadow: 0 4px 8px rgba(255,255,255,0.3);
                border-color: #ffffff;
                background-color: #333333;
            }
            .ganzhi-button:active,
            .ganzhi-button.clicked {
                background-color: #ffffff !important;
                color: #000000 !important;
                border-color: #ffffff !important;
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(255,255,255,0.4) !important;
            }
            
            /* Yao Line Button Styling - Dark Theme */
            .yao-line-button {
                background-color: #2d3339;
                border: 1.5px solid #495057;
                color: #e9ecef;
            }
            .yao-line-button:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                border-color: #6c757d;
            }
            
            /* Changing Button Styling - Dark Theme */
            .yao-button-changing {
                background-color: #2d3339;
                border: 1.5px solid #495057;
            }
            .yao-button-changing:hover {
                background-color: #3d2f1f !important;
                border-color: #d4a574 !important;
                box-shadow: 0 4px 12px rgba(212, 165, 116, 0.3);
            }
            
            /* Line Preview - Dark Theme */
            .line-preview {
                background-color: #2d3339;
                border: 1px solid #495057;
                color: #e9ecef;
            }
            
            /* Result Table - Dark Theme */
            .result-table {
                background-color: #000000;
                border: 2px solid #ffffff;
                color: #ffffff;
            }
            
            /* Tab Styling - Dark Theme */
            .tab-nav {
                border-bottom: 2px solid #ffffff;
            }
            .tab-nav button {
                color: #cccccc;
                font-weight: 600;
            }
            .tab-nav button:hover {
                color: #ffffff;
            }
            .tab-nav button.selected {
                color: #ffffff;
                border-bottom: 3px solid #ffffff;
                font-weight: 800;
            }
            
            /* Input Styling - Dark Theme */
            input[type="text"], input[type="number"], select, textarea {
                border: 2px solid #ffffff;
                background-color: #000000;
                color: #ffffff;
            }
            input[type="text"]:focus, input[type="number"]:focus, select:focus, textarea:focus {
                border-color: #ffffff;
                box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
            }
            
            /* Dropdown Styling - Dark Theme */
            select {
                background-color: #000000;
                color: #ffffff;
                font-weight: 600;
            }
            
            /* Checkbox Styling - Dark Theme */
            input[type="checkbox"] {
                accent-color: #ffffff;
            }
            label {
                color: #ffffff;
                font-weight: 600;
            }
            
            /* Changing Yao Checkbox - Dark Theme */
            .changing-yao-checkbox > div,
            .changing-yao-checkbox > label,
            .changing-yao-checkbox label {
                border: 2px solid #ffffff !important;
                background: #000000 !important;
                color: #ffffff !important;
                box-shadow: 0 2px 4px rgba(255,255,255,0.2) !important;
                font-weight: 700 !important;
            }
            .changing-yao-checkbox > div:hover,
            .changing-yao-checkbox > label:hover,
            .changing-yao-checkbox label:hover {
                box-shadow: 0 4px 12px rgba(255,255,255,0.3) !important;
                border-color: #ffffff !important;
                background: #1a1a1a !important;
            }
            .changing-yao-checkbox input[type="checkbox"]:checked ~ span,
            .changing-yao-checkbox:has(input[type="checkbox"]:checked) > div,
            .changing-yao-checkbox:has(input[type="checkbox"]:checked) > label,
            .changing-yao-checkbox:has(input[type="checkbox"]:checked) label {
                background: #2a1f0f !important;
                border-color: #ffaa00 !important;
                box-shadow: 0 2px 6px rgba(255, 170, 0, 0.5) !important;
            }
            .changing-yao-checkbox input[type="checkbox"] {
                accent-color: #ffffff !important;
            }
            
            /* Button Styling - Dark Theme */
            button.primary {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #ffffff;
                font-weight: 800;
                box-shadow: 0 4px 8px rgba(255,255,255,0.3);
            }
            button.primary:hover {
                background-color: #cccccc;
                border-color: #cccccc;
                box-shadow: 0 6px 12px rgba(255,255,255,0.4);
            }
            button.secondary {
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #ffffff;
                font-weight: 800;
            }
            button.secondary:hover {
                background-color: #1a1a1a;
                border-color: #ffffff;
                box-shadow: 0 4px 8px rgba(255,255,255,0.2);
            }
            
            /* Markdown Headers - Dark Theme */
            h1, h2, h3, h4 {
                color: #ffffff;
                font-weight: 800;
            }
            h3 {
                color: #ffffff;
                font-weight: 800;
            }
            
            /* Section Divider - Dark Theme */
            .section-divider {
                border-top: 2px solid #ffffff;
            }
            
            /* Card-like Containers - Dark Theme */
            .card {
                background-color: #2d3339;
                border: 1px solid #495057;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            /* Refined Text Colors - Dark Theme */
            .text-muted {
                color: #cccccc;
                line-height: 1.6 !important;
                overflow: visible !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                font-weight: 600 !important;
            }
            .text-primary {
                color: #ffffff;
                font-weight: 700;
            }
            
            /* Hexagram Container - Dark Theme */
            .hexagram-container {
                background-color: #000000 !important;
                border: 2px solid #ffffff !important;
                box-shadow: 0 4px 12px rgba(255,255,255,0.3), 0 2px 6px rgba(255,255,255,0.2) !important;
            }
            .hexagram-title {
                color: #ffffff !important;
                font-weight: 800 !important;
            }
            .hexagram-footer {
                color: #ffffff !important;
                font-weight: 700 !important;
            }
            
            /* Hexagram Line Backgrounds - Dark Theme */
            .hexagram-line {
                /* Note: Inline styles will override, but we adjust what we can */
            }
            .hexagram-line.yang {
                /* Slightly brighter red for dark theme visibility */
            }
            .hexagram-line.yin {
                /* Slightly brighter green for dark theme visibility */
            }
            /* Override hexagram line label colors in dark theme */
            .hexagram-line span {
                color: #ffffff !important;
                font-weight: 700 !important;
            }
            
            /* Gradio Component Overrides - Dark Theme */
            .gradio-container {
                background-color: #1a1d20 !important;
            }
            
            /* Textbox and Input Overrides - Dark Theme */
            .gradio-textbox, .gradio-dropdown, .gradio-checkbox {
                background-color: #2d3339 !important;
                border-color: #495057 !important;
                color: #e9ecef !important;
            }
        }
    </style>
    <script>
        // Function to style yao line buttons by directly applying inline styles
        function styleYaoButtons() {
            // Find all buttons - search more broadly
            const allButtons = document.querySelectorAll('button');
            let styledCount = 0;
            allButtons.forEach(button => {
                // Get button text from various possible locations
                let buttonText = '';
                // Try different ways to get the button text
                if (button.textContent) {
                    buttonText = button.textContent.trim();
                } else if (button.innerText) {
                    buttonText = button.innerText.trim();
                } else if (button.value) {
                    buttonText = button.value.trim();
                }
                
                // Also check the button's label or any child elements
                const label = button.querySelector('label');
                if (label && label.textContent) {
                    buttonText = label.textContent.trim();
                }
                
                // Check for text in nested spans or divs - Gradio might wrap text
                const textElement = button.querySelector('span, div');
                if (textElement && textElement.textContent) {
                    const nestedText = textElement.textContent.trim();
                    if (nestedText.includes('▅▅')) {
                        buttonText = nestedText;
                    }
                }
                
                // Only process buttons that contain hexagram symbols
                if (!buttonText.includes('▅▅')) {
                    return;
                }
                
                styledCount++;
                
                // Add the yao-line-button class if not present
                if (!button.classList.contains('yao-line-button')) {
                    button.classList.add('yao-line-button');
                }
                
                // Determine if it's yang or yin and if it's changing
                const isYang = buttonText.includes('▅▅▅▅▅▅');
                const isYin = buttonText.includes('▅▅  ▅▅');
                const isChanging = buttonText.includes('○') || buttonText.includes('×');
                
                // Apply inline styles directly - this is more reliable than classes
                // Use !important to override any Gradio defaults
                // Set width, height, and alignment
                button.style.setProperty('max-width', '350px', 'important');
                button.style.setProperty('width', '100%', 'important');
                button.style.setProperty('margin-left', 'auto', 'important');
                button.style.setProperty('min-height', '80px', 'important');
                button.style.setProperty('padding', '20px 20px', 'important');
                
                if (isYang) {
                    if (isChanging) {
                        button.style.setProperty('background-color', '#e96a6a', 'important');
                        button.style.setProperty('border', '1.5px solid #d32f2f', 'important');
                        button.style.setProperty('color', '#ffffff', 'important');
                        button.style.setProperty('box-shadow', '0 2px 6px rgba(211, 47, 47, 0.5)', 'important');
                        button.style.setProperty('font-weight', '600', 'important');
                    } else {
                        button.style.setProperty('background-color', '#ef4444', 'important');
                        button.style.setProperty('border', '1.5px solid #b71c1c', 'important');
                        button.style.setProperty('color', '#ffffff', 'important');
                        button.style.setProperty('box-shadow', '0 1px 3px rgba(183, 28, 28, 0.4)', 'important');
                        button.style.setProperty('font-weight', '400', 'important');
                    }
                } else if (isYin) {
                    if (isChanging) {
                        button.style.setProperty('background-color', '#64db68', 'important');
                        button.style.setProperty('border', '1.5px solid #2e7d32', 'important');
                        button.style.setProperty('color', '#ffffff', 'important');
                        button.style.setProperty('box-shadow', '0 2px 6px rgba(46, 125, 50, 0.5)', 'important');
                        button.style.setProperty('font-weight', '600', 'important');
                    } else {
                        button.style.setProperty('background-color', '#75cc0d', 'important');
                        button.style.setProperty('border', '1.5px solid #1b5e20', 'important');
                        button.style.setProperty('color', '#ffffff', 'important');
                        button.style.setProperty('box-shadow', '0 1px 3px rgba(27, 94, 32, 0.4)', 'important');
                        button.style.setProperty('font-weight', '400', 'important');
                    }
                }
                
                // Also ensure all child elements (spans, divs) inherit the white color
                const children = button.querySelectorAll('*');
                children.forEach(child => {
                    child.style.setProperty('color', '#ffffff', 'important');
                });
                
                // Also update classes for CSS fallback
                button.classList.remove('yang-button', 'yin-button', 'changing');
                if (isYang) {
                    button.classList.add('yang-button');
                } else if (isYin) {
                    button.classList.add('yin-button');
                }
                if (isChanging) {
                    button.classList.add('changing');
                }
            });
            
            // Debug: log how many buttons were styled
            if (styledCount > 0) {
                console.log(`Styled ${styledCount} yao buttons`);
            }
        }
        
        // Enhanced function that also checks Gradio's internal structure
        function styleYaoButtonsEnhanced() {
            styleYaoButtons();
            // Also check for Gradio's button structure
            const gradioButtons = document.querySelectorAll('[class*="button"], [data-testid*="button"]');
            gradioButtons.forEach(btn => {
                if (btn.textContent && (btn.textContent.includes('▅▅▅▅▅▅') || btn.textContent.includes('▅▅  ▅▅'))) {
                    if (!btn.classList.contains('yao-line-button')) {
                        btn.classList.add('yao-line-button');
                    }
                    styleYaoButtons();
                }
            });
        }
        
        // Run on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                styleYaoButtonsEnhanced();
                // Run multiple times to catch all buttons
                setTimeout(styleYaoButtonsEnhanced, 100);
                setTimeout(styleYaoButtonsEnhanced, 500);
                setTimeout(styleYaoButtonsEnhanced, 1000);
            });
        } else {
            styleYaoButtonsEnhanced();
            setTimeout(styleYaoButtonsEnhanced, 100);
            setTimeout(styleYaoButtonsEnhanced, 500);
        }
        
        // Also run after Gradio updates (using MutationObserver with debounce)
        let styleTimeout;
        const observer = new MutationObserver(function(mutations) {
            clearTimeout(styleTimeout);
            styleTimeout = setTimeout(styleYaoButtonsEnhanced, 50);
        });
        
        // Start observing when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['class', 'value', 'textContent']
                });
                // Also run periodically to catch any missed updates - more frequent
                setInterval(forceStyleButtons, 100);
                setInterval(styleYaoButtonsEnhanced, 200);
            });
        } else {
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['class', 'value', 'textContent']
            });
            // Also run periodically to catch any missed updates - more frequent
            setInterval(forceStyleButtons, 100);
            setInterval(styleYaoButtonsEnhanced, 200);
        }
        
        // More aggressive styling that runs immediately and repeatedly
        function forceStyleButtons() {
            // Use the main styling function which now applies inline styles
            styleYaoButtons();
            styleYaoButtonsEnhanced();
        }
        
        // Listen for button clicks to immediately update styling
        document.addEventListener('click', function(e) {
            const button = e.target.closest('button');
            if (button && (button.textContent.includes('▅▅') || button.classList.contains('yao-line-button'))) {
                // Immediately style, then restyle after delays
                forceStyleButtons();
                setTimeout(forceStyleButtons, 10);
                setTimeout(forceStyleButtons, 50);
                setTimeout(forceStyleButtons, 100);
                setTimeout(forceStyleButtons, 200);
                setTimeout(forceStyleButtons, 500);
            }
        }, true);
        
        // Also listen for input events which Gradio might use
        document.addEventListener('input', function(e) {
            if (e.target && e.target.tagName === 'BUTTON') {
                setTimeout(forceStyleButtons, 10);
            }
        }, true);
        
        // Hook into Gradio's update mechanism
        if (window.gradio_config) {
            const checkAndStyle = function() {
                setTimeout(forceStyleButtons, 50);
            };
            if (window.addEventListener) {
                window.addEventListener('gradio:update', checkAndStyle);
            }
        }
        
        // Override the styleYaoButtonsEnhanced to use the new function
        const originalStyleYaoButtonsEnhanced = styleYaoButtonsEnhanced;
        styleYaoButtonsEnhanced = function() {
            originalStyleYaoButtonsEnhanced();
            forceStyleButtons();
        };
        
        // Add click effects for ganzhi buttons (天干 and 地支)
        function addGanzhiButtonEffects() {
            const ganzhiButtons = document.querySelectorAll('.ganzhi-button');
            ganzhiButtons.forEach(button => {
                // Remove existing click listeners to avoid duplicates
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);
                
                // Add click effect
                newButton.addEventListener('click', function() {
                    // Add clicked class for visual feedback
                    this.classList.add('clicked');
                    
                    // Remove clicked class after animation
                    setTimeout(() => {
                        this.classList.remove('clicked');
                    }, 300);
                    
                    // Temporarily highlight the button
                    const originalBg = this.style.backgroundColor;
                    const originalColor = this.style.color;
                    this.style.backgroundColor = '#000000';
                    this.style.color = '#ffffff';
                    
                    // Reset after a short delay
                    setTimeout(() => {
                        this.style.backgroundColor = originalBg || '';
                        this.style.color = originalColor || '';
                    }, 200);
                });
            });
        }
        
        // Run ganzhi button effects setup
        function setupGanzhiButtons() {
            addGanzhiButtonEffects();
        }
        
        // Run on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setupGanzhiButtons();
                setTimeout(setupGanzhiButtons, 100);
                setTimeout(setupGanzhiButtons, 500);
            });
        } else {
            setupGanzhiButtons();
            setTimeout(setupGanzhiButtons, 100);
            setTimeout(setupGanzhiButtons, 500);
        }
        
        // Also run after Gradio updates
        const ganzhiObserver = new MutationObserver(function(mutations) {
            setupGanzhiButtons();
        });
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                ganzhiObserver.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        } else {
            ganzhiObserver.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    </script>
    """
    
    with gr.Blocks(title="六爻排盤系統") as demo:
        gr.HTML(custom_css)
        gr.Markdown("# 六爻排盤系統", elem_classes=["main-title"])
        gr.Markdown(
            "<p style='color: #868e96; font-size: 14px; margin-top: -8px; margin-bottom: 24px;'>輸入日期和卦象信息，進行六爻排盤</p>",
            elem_classes=["text-muted"]
        )
        gr.Markdown("---", elem_classes=["section-divider"])
        
        with gr.Tabs() as date_tabs:
            # Western Calendar Tab
            with gr.Tab("西曆日期"):
                gr.Markdown(
                    "<p style='color: #868e96; font-size: 13px; margin-bottom: 20px;'>選擇西曆日期和時間進行排盤</p>",
                    elem_classes=["text-muted"]
                )
                # Get current date/time
                now = datetime.now()
                with gr.Row():
                    year_dropdown = gr.Dropdown(
                        choices=list(range(1900, 2101)),
                        value=now.year,
                        label="年",
                        interactive=True,
                        container=True
                    )
                    month_dropdown = gr.Dropdown(
                        choices=list(range(1, 13)),
                        value=now.month,
                        label="月",
                        interactive=True,
                        container=True
                    )
                    day_dropdown = gr.Dropdown(
                        choices=list(range(1, 32)),
                        value=now.day,
                        label="日",
                        interactive=True,
                        container=True
                    )
                    hour_dropdown = gr.Dropdown(
                        choices=list(range(0, 24)),
                        value=now.hour,
                        label="時",
                        interactive=True,
                        container=True
                    )
                use_western_date = gr.State(value=True)
            
            # Gan-Zhi Calendar Tab
            with gr.Tab("干支曆"):
                gr.Markdown(
                    "<p style='color: #868e96; font-size: 13px; margin-bottom: 20px;'>依次選擇天干和地支組成四柱（年柱、月柱、日柱、時柱）</p>",
                    elem_classes=["text-muted"]
                )
                with gr.Row():
                    # Left panel: 天干 and 地支 (with 地支 below 天干)
                    with gr.Column(scale=1, elem_classes=["column-spacing"]):
                        # Current selection display at the top
                        # 天干 (Heavenly Stems) section
                        gr.Markdown("### 天干", elem_classes=["section-header"])
                        gr.Markdown(
                            "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 12px;'>點擊選擇天干</p>",
                            elem_classes=["text-muted"]
                        )
                        
                        # Create 10 天干 buttons in a grid (2 rows × 5 columns)
                        stem_buttons = []
                        with gr.Column():
                            for i in range(0, 10, 5):
                                with gr.Row():
                                    for j in range(5):
                                        if i + j < 10:
                                            stem = HEAVENLY_STEMS[i + j]
                                            btn = gr.Button(
                                                stem,
                                                size="lg",
                                                min_width=60,
                                                elem_classes=["ganzhi-button"]
                                            )
                                            stem_buttons.append((i + j, btn))
                        
                        gr.Markdown("---", elem_classes=["section-divider"])
                        
                        # 地支 (Earthly Branches) section - below 天干
                        gr.Markdown("### 地支", elem_classes=["section-header"])
                        gr.Markdown(
                            "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 12px;'>點擊選擇地支</p>",
                            elem_classes=["text-muted"]
                        )
                        
                        # Create 12 地支 buttons in a grid (3 rows × 4 columns)
                        branch_buttons = []
                        with gr.Column():
                            for i in range(0, 12, 4):
                                with gr.Row():
                                    for j in range(4):
                                        if i + j < 12:
                                            branch = EARTHLY_BRANCHES[i + j]
                                            btn = gr.Button(
                                                branch,
                                                size="lg",
                                                min_width=60,
                                                elem_classes=["ganzhi-button"]
                                            )
                                            branch_buttons.append((i + j, btn))
                    
                    # Right panel: Display selected pillars
                    with gr.Column(scale=1, elem_classes=["column-spacing"]):
                        current_pillar_label = gr.Markdown("### 當前選擇：年柱", elem_classes=["section-header"])
                        current_selection = gr.Textbox(
                            label="當前選擇",
                            value="",
                            interactive=False,
                            container=True
                        )
                        
                        gr.Markdown("---", elem_classes=["section-divider"])

                        gr.Markdown("### 已選擇的四柱", elem_classes=["section-header"])
                        
                        # Display pillars horizontally
                        with gr.Row():
                            year_display = gr.Textbox(
                                label="年柱",
                                value="",
                                interactive=True,
                                scale=1,
                                container=True
                            )
                            month_display = gr.Textbox(
                                label="月柱",
                                value="",
                                interactive=True,
                                scale=1,
                                container=True
                            )
                            day_display = gr.Textbox(
                                label="日柱",
                                value="",
                                interactive=True,
                                scale=1,
                                container=True
                            )
                            hour_display = gr.Textbox(
                                label="時柱",
                                value="",
                                interactive=True,
                                scale=1,
                                container=True
                            )
                        
                        reset_btn = gr.Button("重置", variant="secondary")
                
                # State to track current pillar and selections
                pillar_index_state = gr.State(value=0)  # 0=year, 1=month, 2=day, 3=hour
                current_stem_state = gr.State(value="")
                current_branch_state = gr.State(value="")
                year_pillar_state = gr.State(value="")
                month_pillar_state = gr.State(value="")
                day_pillar_state = gr.State(value="")
                hour_pillar_state = gr.State(value="")
                
                # Pillar labels
                pillar_labels = ["年柱", "月柱", "日柱", "時柱"]
                
                def handle_stem_click(clicked_stem, current_index, current_stem, current_branch, year, month, day, hour):
                    """Handle click on a 天干 button"""
                    new_stem = clicked_stem
                    if current_branch:
                        selection_text = f"{new_stem}{current_branch}"
                    else:
                        selection_text = f"{new_stem}[待選地支]"
                    
                    return (
                        new_stem,  # current_stem_state
                        current_branch,  # current_branch_state
                        selection_text,  # current_selection
                        year, month, day, hour  # pillar states (unchanged)
                    )
                
                def handle_branch_click(clicked_branch, current_index, current_stem, current_branch, year, month, day, hour):
                    """Handle click on a 地支 button"""
                    new_branch = clicked_branch
                    
                    if not current_stem:
                        # No stem selected yet
                        selection_text = f"[待選天干]{new_branch}"
                        return (
                            "",  # current_stem_state
                            new_branch,  # current_branch_state
                            selection_text,  # current_selection
                            year, month, day, hour  # pillar states
                        )
                    
                    # Both stem and branch selected, set the current pillar
                    ganzhi = f"{current_stem}{new_branch}"
                    next_index = (current_index + 1) % 4
                    next_label = f"**當前選擇：{pillar_labels[next_index]}**"
                    
                    # Set the current pillar
                    if current_index == 0:
                        year = ganzhi
                    elif current_index == 1:
                        month = ganzhi
                    elif current_index == 2:
                        day = ganzhi
                    elif current_index == 3:
                        hour = ganzhi
                    
                    # Reset current stem/branch for next pillar
                    return (
                        "",  # current_stem_state (reset)
                        "",  # current_branch_state (reset)
                        "",  # current_selection (reset)
                        next_index,  # pillar_index_state
                        f"### 當前選擇：{pillar_labels[next_index]}",  # current_pillar_label
                        year, month, day, hour,  # pillar states
                        year, month, day, hour  # displays
                    )
                
                def reset_pillars():
                    """Reset all pillars"""
                    return (
                        0,  # pillar_index_state
                        "", # current_stem_state
                        "", # current_branch_state
                        "### 當前選擇：年柱",  # current_pillar_label
                        "",  # current_selection
                        "", "", "", "",  # pillar states
                        "", "", "", ""  # displays
                    )
                
                # Wire up 天干 buttons
                def make_stem_handler(stem):
                    def handler(current_index, current_stem, current_branch, year, month, day, hour):
                        return handle_stem_click(stem, current_index, current_stem, current_branch, year, month, day, hour)
                    return handler
                
                for idx, btn in stem_buttons:
                    stem = HEAVENLY_STEMS[idx]
                    handler = make_stem_handler(stem)
                    btn.click(
                        fn=handler,
                        inputs=[pillar_index_state, current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state],
                        outputs=[current_stem_state, current_branch_state, current_selection, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state]
                    )
                
                # Wire up 地支 buttons
                def make_branch_handler(branch):
                    def handler(current_index, current_stem, current_branch, year, month, day, hour):
                        result = handle_branch_click(branch, current_index, current_stem, current_branch, year, month, day, hour)
                        if len(result) == 7:
                            # Just stem/branch update
                            return result
                        else:
                            # Full pillar update
                            return result
                    return handler
                
                for idx, btn in branch_buttons:
                    branch = EARTHLY_BRANCHES[idx]
                    handler = make_branch_handler(branch)
                    btn.click(
                        fn=handler,
                        inputs=[pillar_index_state, current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state],
                        outputs=[current_stem_state, current_branch_state, current_selection, pillar_index_state, current_pillar_label, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, year_display, month_display, day_display, hour_display]
                    )
                
                reset_btn.click(
                    fn=reset_pillars,
                    outputs=[pillar_index_state, current_stem_state, current_branch_state, current_pillar_label, current_selection, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, year_display, month_display, day_display, hour_display]
                )
        
        # Hexagram Input Tab
        with gr.Tab("卦象輸入"):
            gr.Markdown("### 輸入卦名", elem_classes=["section-header"])
            
            with gr.Row():
                hexagram_name_input = gr.Textbox(
                    label="卦名搜尋",
                    placeholder="例如：山地、天風、乾為天",
                    interactive=True
                )
                hexagram_dropdown = gr.Dropdown(
                    label="選擇卦象",
                    choices=[],
                    interactive=True
                )
            
            # Store selected hexagram code
            selected_hexagram_code_state = gr.State(value="111111")
            
            # Create hexagram display with checkboxes next to each line
            # gr.Markdown("---", elem_classes=["section-divider"])
            gr.Markdown("### 卦象預覽", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 13px; margin-top: -8px; margin-bottom: 20px; line-height: 1.6; overflow: visible; white-space: normal; word-wrap: break-word;'>勾選右側的複選框標記動爻（從下往上：1爻、2爻、3爻、4爻、5爻、6爻）</p>",
                elem_classes=["text-muted"]
            )
            
            # Changing lines checkboxes - will be placed next to each line
            changing_checkboxes = []
            
            # Use the unified create_line_html function (defined at module level)
            
            # Create a container for hexagram lines with checkboxes and changed hexagram
            with gr.Row(elem_classes=["hexagram-display-row"]):
                # Left column: Original hexagram (本卦)
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 本卦",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px;'>原始卦象</p>",
                        elem_classes=["text-muted"]
                    )
                    hexagram_line_containers = []
                    initial_code = "111111"
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        initial_html = create_line_html(initial_code, line_num, False)
                        line_html = gr.HTML(
                            value=initial_html,
                            elem_classes=["hexagram-line-container"],
                            min_width=300
                        )
                        hexagram_line_containers.append(line_html)
                
                # Middle column: Checkboxes for 動爻
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 動爻",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px; line-height: 1.6; overflow: visible; white-space: normal; word-wrap: break-word;'>選擇變化的爻</p>",
                        elem_classes=["text-muted"]
                    )
                    changing_checkboxes = []
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        checkbox = gr.Checkbox(
                            label=f"{line_num}爻",
                            value=False,
                            interactive=True,
                            elem_classes=["changing-yao-checkbox"],
                            container=True
                        )
                        changing_checkboxes.append(checkbox)
                    # changing_checkboxes.reverse()
                    
                    # Add debug handler to verify checkboxes are working
                    def create_checkbox_debug_handler(line_num):
                        def handler(checkbox_val):
                            print(f"DEBUG: Regular tab checkbox {line_num}爻 changed to {checkbox_val}")
                            # Don't return anything since outputs is empty
                        return handler
                    
                    # Wire up checkboxes to print debug output when changed
                    for idx, checkbox in enumerate(changing_checkboxes):
                        line_num = 6 - idx  # idx 0 = 6爻, idx 5 = 1爻
                        handler = create_checkbox_debug_handler(line_num)
                        checkbox.change(
                            fn=handler,
                            inputs=[checkbox],
                            outputs=[]  # Just for debugging, no outputs needed
                        )
                # Right column: Changed hexagram (變卦)
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 變卦",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px;'>變化後的卦象</p>",
                        elem_classes=["text-muted"]
                    )
                    changed_hexagram_line_containers = []
                    initial_code = "111111"
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        initial_html = create_line_html(initial_code, line_num, False)
                        line_html = gr.HTML(
                            value=initial_html,
                            elem_classes=["hexagram-line-container"],
                            min_width=300
                        )
                        changed_hexagram_line_containers.append(line_html)
            
            # Function to update hexagram line displays
            def update_hexagram_lines(code, *changing_lines):
                """Update all hexagram line displays (both original and changed)
                
                Args:
                    code: Hexagram code (6 digits, index 0 = line 1, index 5 = line 6)
                    *changing_lines: Checkbox values in visual order [6,5,4,3,2,1] (top to bottom)
                
                Returns:
                    Tuple of (original_line_htmls, changed_line_htmls)
                """
                if not code or len(code) != 6:
                    code = "111111"
                
                # Map checkbox values to line numbers
                # changing_lines[0] = line 6 (top), changing_lines[5] = line 1 (bottom)
                changing = []
                for visual_index, is_changing in enumerate(changing_lines):
                    line_num = 6 - visual_index  # visual_index 0 -> line 6, visual_index 5 -> line 1
                    if is_changing:
                        changing.append(line_num)
                
                # Calculate changed hexagram code
                changed_code = calculate_changed_hexagram(code, changing)
                
                # Create HTML for original hexagram lines in visual order (6 to 1, top to bottom)
                original_line_htmls = []
                changed_line_htmls = []
                
                for visual_index in range(6):
                    line_num = 6 - visual_index  # line 6, 5, 4, 3, 2, 1
                    code_index = line_num - 1  # line 6 -> code[5], line 1 -> code[0]
                    
                    # Original hexagram line - use helper function
                    is_changing_line = line_num in changing
                    original_html = create_line_html(code, line_num, is_changing_line, clickable=False)
                    original_line_htmls.append(original_html)
                    
                    # Changed hexagram line - use helper function
                    changed_html = create_changed_line_html(changed_code, line_num)
                    changed_line_htmls.append(changed_html)
                
                # Return both in visual order (6 to 1, top to bottom)
                return original_line_htmls, changed_line_htmls
            
            # Update dropdown when name changes
            def on_name_change(query):
                matches = search_hexagram_by_name(query)
                if matches:
                    choices = [f"{code} - {name}" for code, name in matches]
                    selected_code = matches[0][0] if matches else ""
                    selected_value = choices[0] if choices else None
                    # Reset all changing checkboxes when new hexagram is selected
                    checkbox_updates = [gr.update(value=False)] * 6
                    # Update hexagram lines (both original and changed)
                    original_updates, changed_updates = update_hexagram_lines(selected_code, *[False] * 6)
                    return [gr.Dropdown(choices=choices, value=selected_value), selected_code] + checkbox_updates + original_updates + changed_updates
                # When no matches, clear dropdown and reset to empty
                return [gr.Dropdown(choices=[], value=None), ""] + [gr.update(value=False)] * 6 + [gr.update()] * 6 + [gr.update()] * 6
            
            hexagram_name_input.change(
                fn=on_name_change,
                inputs=[hexagram_name_input],
                outputs=[hexagram_dropdown, selected_hexagram_code_state] + changing_checkboxes + hexagram_line_containers + changed_hexagram_line_containers
            )
            
            # When hexagram is selected from dropdown, update lines and state
            def on_dropdown_select(dropdown_value, *changing_lines):
                code = get_hexagram_code_from_dropdown(dropdown_value)
                if not code or len(code) != 6:
                    code = "111111"
                
                original_updates, changed_updates = update_hexagram_lines(code, *changing_lines)
                # Return code as first value, then all original updates, then all changed updates
                return [code] + original_updates + changed_updates
            
            # When changing lines checkboxes change, update hexagram lines
            def update_lines_with_changing(code, *changing_lines):
                if not code or len(code) != 6:
                    code = "111111"
                
                original_updates, changed_updates = update_hexagram_lines(code, *changing_lines)
                # Return as separate lists, not as a tuple
                return original_updates + changed_updates
            
            # Update lines when dropdown changes
            hexagram_dropdown.change(
                fn=on_dropdown_select,
                inputs=[hexagram_dropdown] + changing_checkboxes,
                outputs=[selected_hexagram_code_state] + hexagram_line_containers + changed_hexagram_line_containers
            )
            
            # Update lines when changing checkboxes change
            for checkbox in changing_checkboxes:
                checkbox.change(
                    fn=update_lines_with_changing,
                    inputs=[selected_hexagram_code_state] + changing_checkboxes,
                    outputs=hexagram_line_containers + changed_hexagram_line_containers
                )
            
            # Calculate button for regular tab
            gr.Markdown("---", elem_classes=["section-divider"])
            regular_calculate_btn = gr.Button("開始排盤", variant="primary", size="lg")
        
        # Clickable Hexagram Input Tab
        with gr.Tab("卦象輸入 (點擊)"):
            gr.Markdown("### 點擊爻線輸入卦象", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 13px; margin-top: -8px; margin-bottom: 20px;'>點擊下方的爻線來切換陽（▅▅▅▅▅▅）和陰（▅▅  ▅▅），從下往上：1爻、2爻、3爻、4爻、5爻、6爻</p>",
                elem_classes=["text-muted"]
            )
            
            # Store hexagram code state
            clickable_hexagram_code_state = gr.State(value="111111")
            
            # Store changing lines state (for checkboxes)
            clickable_changing_state_1 = gr.State(value=False)  # 1爻
            clickable_changing_state_2 = gr.State(value=False)  # 2爻
            clickable_changing_state_3 = gr.State(value=False)  # 3爻
            clickable_changing_state_4 = gr.State(value=False)  # 4爻
            clickable_changing_state_5 = gr.State(value=False)  # 5爻
            clickable_changing_state_6 = gr.State(value=False)  # 6爻
            
            # Use the unified create_line_html function with clickable=True
            
            # Function to update clickable hexagram displays
            def update_clickable_hexagram_display(code, *changing_lines):
                """Update all hexagram displays when code or changing lines change"""
                if not code or len(code) != 6:
                    code = "111111"
                
                # Map checkbox values to line numbers
                # Based on the inputs order in button.click and checkbox.change:
                # clickable_changing_checkboxes[5] -> 1爻 (changing_lines[0])
                # clickable_changing_checkboxes[0] -> 6爻 (changing_lines[5])
                # But visually: 6爻 is at top, 1爻 is at bottom
                # So: changing_lines[0] = 6爻 (top), changing_lines[5] = 1爻 (bottom)
                changing = []
                for visual_index, is_changing in enumerate(changing_lines):
                    line_num = 6 - visual_index  # visual_index 0 -> line 6 (top), visual_index 5 -> line 1 (bottom)
                    if is_changing:
                        changing.append(line_num)
                print(f"DEBUG update_clickable_hexagram_display: code={code}, changing_lines={changing_lines}, changing={changing}")
                
                # Calculate changed hexagram code
                changed_code = calculate_changed_hexagram(code, changing)
                
                # Create HTML for original hexagram lines in visual order (6 to 1, top to bottom)
                original_line_htmls = []
                changed_line_htmls = []
                
                for visual_index in range(6):
                    line_num = 6 - visual_index  # line 6, 5, 4, 3, 2, 1
                    code_index = line_num - 1  # line 6 -> code[5], line 1 -> code[0]
                    
                    # Original hexagram line
                    is_changing_line = line_num in changing
                    original_html = create_line_html(code, line_num, is_changing_line, clickable=True)
                    original_line_htmls.append(original_html)
                    
                    # Changed hexagram line - use helper function
                    changed_html = create_changed_line_html(changed_code, line_num)
                    # Adjust spacing for clickable tab (add extra space before line number)
                    changed_html = changed_html.replace(f">{line_num}爻", f">  {line_num}爻")
                    changed_line_htmls.append(changed_html)
                
                # Return code, original line HTMLs, and changed line HTMLs
                return code, original_line_htmls, changed_line_htmls
            
            # Create a container for hexagram lines with checkboxes and changed hexagram
            with gr.Row(elem_classes=["hexagram-display-row"]):
                # Left column: Original hexagram (本卦) with clickable lines
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 本卦",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px;'>點擊爻線切換陽陰</p>",
                        elem_classes=["text-muted"]
                    )
                    clickable_line_buttons = []
                    initial_code = "111111"
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        is_yang = initial_code[i] == '1'
                        # Create a button styled to look like the hexagram line
                        # Include line number in the button text
                        button_value = f"{'▅▅▅▅▅▅' if is_yang else '▅▅  ▅▅'} {line_num}爻"
                        
                        # Add initial class based on yang/yin
                        button_classes = ["yao-line-button"]
                        if is_yang:
                            button_classes.append("yang-button")
                        else:
                            button_classes.append("yin-button")
                        
                        line_button = gr.Button(
                            value=button_value,
                            elem_classes=button_classes,
                            size="lg",
                            min_width=350
                        )
                        clickable_line_buttons.append((line_num, line_button))
                
                # Middle column: Checkboxes for 動爻
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 動爻",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px; line-height: 1.6; overflow: visible; white-space: normal; word-wrap: break-word;'>選擇變化的爻</p>",
                        elem_classes=["text-muted"]
                    )
                    clickable_changing_checkboxes = []
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        checkbox = gr.Checkbox(
                            label=f"{line_num}爻",
                            value=False,
                            interactive=True,
                            elem_classes=["changing-yao-checkbox"],
                            container=True
                        )
                        clickable_changing_checkboxes.append(checkbox)
                    clickable_changing_checkboxes.reverse()
                # Right column: Changed hexagram (變卦)
                with gr.Column(scale=1, elem_classes=["column-spacing"]):
                    gr.Markdown(
                        "### 變卦",
                        elem_classes=["section-header"]
                    )
                    gr.Markdown(
                        "<p style='color: #868e96; font-size: 12px; margin-top: -8px; margin-bottom: 16px;'>變化後的卦象</p>",
                        elem_classes=["text-muted"]
                    )
                    clickable_changed_hexagram_line_containers = []
                    initial_code = "111111"
                    # Create in reverse order for display (6 to 1)
                    for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                        line_num = i + 1
                        initial_html = create_line_html(initial_code, line_num, False, clickable=True)
                        line_html = gr.HTML(
                            value=initial_html,
                            elem_classes=["hexagram-line-container"],
                            min_width=300
                        )
                        clickable_changed_hexagram_line_containers.append(line_html)
            
            # Function to handle line button clicks
            def handle_line_click(line_num, current_code, *changing_lines):
                """Handle click on a line button"""
                if not current_code or len(current_code) != 6:
                    current_code = "111111"
                
                print(f"DEBUG handle_line_click: line_num={line_num}, current_code={current_code}, changing_lines={changing_lines}")
                
                # Toggle the line
                code_list = list(current_code)
                index = line_num - 1
                code_list[index] = '1' if code_list[index] == '0' else '0'
                new_code = ''.join(code_list)
                
                print(f"DEBUG handle_line_click: new_code={new_code}")
                
                # Get changed hexagram updates
                _, changed_updates = update_clickable_hexagram_display(new_code, *changing_lines)[1:]
                
                # Map checkbox values to line numbers
                # changing_lines[0] = 6爻 (top), changing_lines[5] = 1爻 (bottom)
                changing_line_nums = []
                for visual_index, is_changing in enumerate(changing_lines):
                    line_num = 6 - visual_index  # visual_index 0 -> line 6 (top), visual_index 5 -> line 1 (bottom)
                    if is_changing:
                        changing_line_nums.append(line_num)
                
                # Update button text and styling
                button_updates = []
                for visual_index in range(6):
                    actual_line_num = 6 - visual_index
                    code_index = actual_line_num - 1
                    is_yang = new_code[code_index] == '1'
                    is_changing = actual_line_num in changing_line_nums
                    line_symbol = "▅▅▅▅▅▅" if is_yang else "▅▅  ▅▅"
                    change_mark = " ○" if (is_changing and is_yang) else (" ×" if (is_changing and not is_yang) else "")
                    button_text = f"{line_symbol}{actual_line_num}爻 {change_mark}"
                    # Update classes based on yang/yin and changing status
                    button_classes = ["yao-line-button"]
                    if is_yang:
                        button_classes.append("yang-button")
                    else:
                        button_classes.append("yin-button")
                    if is_changing:
                        button_classes.append("changing")
                    # Add data attribute to help with styling
                    elem_id = f"yao-btn-{actual_line_num}"
                    button_updates.append(gr.update(value=button_text, elem_classes=button_classes, elem_id=elem_id))
                
                return [new_code] + button_updates + changed_updates
            
            # Function to update displays when changing checkboxes change
            def update_clickable_with_changing(code, *changing_lines):
                """Update displays when changing lines checkboxes change"""
                print(f"DEBUG update_clickable_with_changing: code={code}, changing_lines={changing_lines}")
                if not code or len(code) != 6:
                    code = "111111"
                
                # Get changed hexagram updates
                _, changed_updates = update_clickable_hexagram_display(code, *changing_lines)[1:]
                
                # Map checkbox values to line numbers
                # changing_lines[0] = 6爻 (top), changing_lines[5] = 1爻 (bottom)
                changing_line_nums = []
                for visual_index, is_changing in enumerate(changing_lines):
                    line_num = 6 - visual_index  # visual_index 0 -> line 6 (top), visual_index 5 -> line 1 (bottom)
                    if is_changing:
                        changing_line_nums.append(line_num)
                
                # Update button styling based on changing lines
                button_updates = []
                for visual_index in range(6):
                    actual_line_num = 6 - visual_index
                    code_index = actual_line_num - 1
                    is_yang = code[code_index] == '1'
                    is_changing = actual_line_num in changing_line_nums
                    line_symbol = "▅▅▅▅▅▅" if is_yang else "▅▅  ▅▅"
                    change_mark = " ○" if (is_changing and is_yang) else (" ×" if (is_changing and not is_yang) else "")
                    button_text = f"{line_symbol}{actual_line_num}爻 {change_mark}"
                    # Update classes based on yang/yin and changing status
                    button_classes = ["yao-line-button"]
                    if is_yang:
                        button_classes.append("yang-button")
                    else:
                        button_classes.append("yin-button")
                    if is_changing:
                        button_classes.append("changing")
                    # Add data attribute to help with styling
                    elem_id = f"yao-btn-{actual_line_num}"
                    button_updates.append(gr.update(value=button_text, elem_classes=button_classes, elem_id=elem_id))
                
                return button_updates + changed_updates
            
            # Wire up line button clicks
            def make_line_click_handler(ln):
                """Create a click handler for a specific line number"""
                def handler(current_code, *changing_lines):
                    return handle_line_click(ln, current_code, *changing_lines)
                return handler
            
            for line_num, button in clickable_line_buttons:
                handler = make_line_click_handler(line_num)
                button.click(
                    fn=handler,
                    inputs=[
                        clickable_hexagram_code_state,
                        clickable_changing_checkboxes[5],  # 1爻
                        clickable_changing_checkboxes[4],  # 2爻
                        clickable_changing_checkboxes[3],  # 3爻
                        clickable_changing_checkboxes[2],  # 4爻
                        clickable_changing_checkboxes[1],  # 5爻
                        clickable_changing_checkboxes[0],  # 6爻
                    ],
                    outputs=[clickable_hexagram_code_state] + [btn for _, btn in clickable_line_buttons] + clickable_changed_hexagram_line_containers
                )
            
            # Wire up each checkbox to update its corresponding state variable
            # clickable_changing_checkboxes[5] = 1爻 -> state_1
            # clickable_changing_checkboxes[4] = 2爻 -> state_2
            # clickable_changing_checkboxes[3] = 3爻 -> state_3
            # clickable_changing_checkboxes[2] = 4爻 -> state_4
            # clickable_changing_checkboxes[1] = 5爻 -> state_5
            # clickable_changing_checkboxes[0] = 6爻 -> state_6
            checkbox_to_state_map = [
                (clickable_changing_checkboxes[0], clickable_changing_state_1, 1),  # 1爻
                (clickable_changing_checkboxes[1], clickable_changing_state_2, 2),  # 2爻
                (clickable_changing_checkboxes[2], clickable_changing_state_3, 3),  # 3爻
                (clickable_changing_checkboxes[3], clickable_changing_state_4, 4),  # 4爻
                (clickable_changing_checkboxes[4], clickable_changing_state_5, 5),  # 5爻
                (clickable_changing_checkboxes[5], clickable_changing_state_6, 6),  # 6爻
            ]
            
            # Create a simple handler that just updates the state variable
            # This is simpler and more reliable
            def create_simple_checkbox_handler(line_num):
                """Create a simple handler that just updates state"""
                def handler(checkbox_val):
                    """Update state when checkbox changes"""
                    print(f"DEBUG: Checkbox {line_num}爻 changed to {checkbox_val}")
                    return checkbox_val
                return handler
            
            # Wire up each checkbox to update its state variable
            for checkbox, state_var, line_num in checkbox_to_state_map:
                handler = create_simple_checkbox_handler(line_num)
                checkbox.change(
                    fn=handler,
                    inputs=[checkbox],
                    outputs=[state_var]
                )
            
            # Also wire up checkboxes to update display separately
            def update_display_when_checkbox_changes(code, cb1, cb2, cb3, cb4, cb5, cb6):
                """Update display when any checkbox changes"""
                print(f"DEBUG update_display: code={code}, checkboxes={cb1}, {cb2}, {cb3}, {cb4}, {cb5}, {cb6}")
                return update_clickable_with_changing(code, cb1, cb2, cb3, cb4, cb5, cb6)
            
            # Wire all checkboxes to update display (using a single handler for all)
            for checkbox in clickable_changing_checkboxes:
                checkbox.change(
                    fn=update_display_when_checkbox_changes,
                    inputs=[
                        clickable_hexagram_code_state,
                        clickable_changing_checkboxes[5],  # 1爻
                        clickable_changing_checkboxes[4],  # 2爻
                        clickable_changing_checkboxes[3],  # 3爻
                        clickable_changing_checkboxes[2],  # 4爻
                        clickable_changing_checkboxes[1],  # 5爻
                        clickable_changing_checkboxes[0],  # 6爻
                    ],
                    outputs=[btn for _, btn in clickable_line_buttons] + clickable_changed_hexagram_line_containers
                )
            
            # Calculate button for clickable tab
            gr.Markdown("---", elem_classes=["section-divider"])
            clickable_calculate_btn = gr.Button("開始排盤", variant="primary", size="lg")
        # Results section
        gr.Markdown("### 詳細排盤表", elem_classes=["section-header"])
        gr.Markdown(
            "<p style='color: #868e96; font-size: 13px; margin-top: -8px; margin-bottom: 16px;'>排盤結果將顯示在下方</p>",
            elem_classes=["text-muted"]
        )
        result_table = gr.Textbox(
            label="",
            lines=40,
            max_lines=60,
            interactive=True,
            elem_classes=["result-table"],
            container=True
        )
        
        # Simple processing function for regular tab
        def process_regular_tab(
            year, month, day, hour,
            year_pillar_str, month_pillar_str, day_pillar_str, hour_pillar_str,
            hexagram_dropdown_value, hexagram_code_state,
            yao1_changing, yao2_changing, yao3_changing,
            yao4_changing, yao5_changing, yao6_changing
        ):
            # Determine which date method to use
            use_western = not (year_pillar_str and month_pillar_str and day_pillar_str and hour_pillar_str)
            
            # Get hexagram code from regular tab
            code = ""
            if hexagram_dropdown_value:
                try:
                    extracted_code = get_hexagram_code_from_dropdown(hexagram_dropdown_value)
                    if extracted_code and len(extracted_code) == 6 and extracted_code in HEXAGRAM_MAP:
                        code = extracted_code
                except (ValueError, AttributeError, TypeError, KeyError):
                    pass
            
            if not code:
                if hexagram_code_state and len(hexagram_code_state) == 6 and hexagram_code_state in HEXAGRAM_MAP:
                    code = hexagram_code_state
            
            if not code or len(code) != 6 or code not in HEXAGRAM_MAP:
                code = "111111"  # Default
            
            # Map checkboxes to changing lines (checkboxes are in visual order: 6,5,4,3,2,1)
            # yao1_changing is for line 6, yao6_changing is for line 1
            changing_1 = bool(yao6_changing) if yao6_changing is not None else False  # line 1
            changing_2 = bool(yao5_changing) if yao5_changing is not None else False  # line 2
            changing_3 = bool(yao4_changing) if yao4_changing is not None else False  # line 3
            changing_4 = bool(yao3_changing) if yao3_changing is not None else False  # line 4
            changing_5 = bool(yao2_changing) if yao2_changing is not None else False  # line 5
            changing_6 = bool(yao1_changing) if yao1_changing is not None else False  # line 6
            
            return process_divination(
                use_western,
                year, month, day, hour,
                year_pillar_str, "", month_pillar_str, "",
                day_pillar_str, "", hour_pillar_str, "",
                False,  # use_button_method
                "陽", False, "陽", False, "陽", False,
                "陽", False, "陽", False, "陽", False,
                "", code,
                changing_1, changing_2, changing_3, changing_4, changing_5, changing_6
            )
        
        # Simple processing function for clickable tab
        def process_clickable_tab(
            year, month, day, hour,
            year_pillar_str, month_pillar_str, day_pillar_str, hour_pillar_str,
            clickable_hexagram_code, clickable_yao1_changing, clickable_yao2_changing, clickable_yao3_changing,
            clickable_yao4_changing, clickable_yao5_changing, clickable_yao6_changing
        ):
            # Determine which date method to use
            use_western = not (year_pillar_str and month_pillar_str and day_pillar_str and hour_pillar_str)
            
            # Get hexagram code from clickable tab
            code = clickable_hexagram_code if (clickable_hexagram_code and len(clickable_hexagram_code) == 6 and clickable_hexagram_code in HEXAGRAM_MAP) else "111111"
            
            # Map checkboxes to changing lines
            changing_1 = bool(clickable_yao1_changing) if clickable_yao1_changing is not None else False  # line 1
            changing_2 = bool(clickable_yao2_changing) if clickable_yao2_changing is not None else False  # line 2
            changing_3 = bool(clickable_yao3_changing) if clickable_yao3_changing is not None else False  # line 3
            changing_4 = bool(clickable_yao4_changing) if clickable_yao4_changing is not None else False  # line 4
            changing_5 = bool(clickable_yao5_changing) if clickable_yao5_changing is not None else False  # line 5
            changing_6 = bool(clickable_yao6_changing) if clickable_yao6_changing is not None else False  # line 6
            
            return process_divination(
                use_western,
                year, month, day, hour,
                year_pillar_str, "", month_pillar_str, "",
                day_pillar_str, "", hour_pillar_str, "",
                False,  # use_button_method
                "陽", False, "陽", False, "陽", False,
                "陽", False, "陽", False, "陽", False,
                "", code,
                changing_1, changing_2, changing_3, changing_4, changing_5, changing_6
            )
        
        # Wire up regular tab button
        regular_calculate_btn.click(
            fn=process_regular_tab,
            inputs=[
                year_dropdown, month_dropdown, day_dropdown, hour_dropdown,
                year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state,
                hexagram_dropdown, selected_hexagram_code_state,
                changing_checkboxes[0], changing_checkboxes[1], changing_checkboxes[2],
                changing_checkboxes[3], changing_checkboxes[4], changing_checkboxes[5],
            ],
            outputs=[result_table]
        )
        
        # Wire up clickable tab button
        clickable_calculate_btn.click(
            fn=process_clickable_tab,
            inputs=[
                year_dropdown, month_dropdown, day_dropdown, hour_dropdown,
                year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state,
                clickable_hexagram_code_state,
                clickable_changing_state_1, clickable_changing_state_2, clickable_changing_state_3,
                clickable_changing_state_4, clickable_changing_state_5, clickable_changing_state_6,
            ],
            outputs=[result_table]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch()

