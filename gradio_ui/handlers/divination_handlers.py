"""
Divination handlers for processing divination requests

This module contains the main processing logic for divination, refactored
to use data classes and split into smaller, focused functions.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Any, Dict
from ba_zi_base import BaZi, Pillar
from liu_yao import six_yao_divination, HEXAGRAM_MAP
from liu_yao import bazi_from_date_string

from ..config import ERROR_MESSAGES, DEFAULT_HEXAGRAM_CODE, SHOW_TIAN_GAN
from ..utils.validation import (
    validate_date,
    validate_ganzhi,
    validate_hexagram_code
)
from ..utils.hexagram_utils import search_hexagram_by_name
from ..utils.formatting import format_divination_results_pc, format_divination_results_mobile


@dataclass
class WesternDateInput:
    """Input data for Western calendar date"""
    year: int
    month: int
    day: int
    hour: int


@dataclass
class GanzhiDateInput:
    """Input data for Gan-Zhi calendar date"""
    year_pillar: str  # e.g., "甲子"
    month_pillar: str
    day_pillar: str
    hour_pillar: str


@dataclass
class ButtonMethodInput:
    """Input data for button method hexagram input"""
    yao1_type: str
    yao1_changing: bool
    yao2_type: str
    yao2_changing: bool
    yao3_type: str
    yao3_changing: bool
    yao4_type: str
    yao4_changing: bool
    yao5_type: str
    yao5_changing: bool
    yao6_type: str
    yao6_changing: bool


@dataclass
class NameMethodInput:
    """Input data for name search method hexagram input"""
    hexagram_name_query: str
    selected_hexagram_code: str
    changing_lines: List[bool]  # 6 boolean values for lines 1-6


@dataclass
class DivinationRequest:
    """Complete divination request with all inputs"""
    use_western_date: bool
    western_date: Optional[WesternDateInput]
    ganzhi_date: Optional[GanzhiDateInput]
    use_button_method: bool
    button_method: Optional[ButtonMethodInput]
    name_method: Optional[NameMethodInput]


def create_bazi_from_western_date(date: WesternDateInput) -> Tuple[Optional[BaZi], Optional[str]]:
    """
    Create BaZi object from Western calendar date
    
    Args:
        date: Western date input
        
    Returns:
        Tuple of (BaZi object, error_message)
        Returns (None, error_message) if creation fails
        Returns (BaZi, None) if successful
    """
    # Validate date
    error = validate_date(date.year, date.month, date.day, date.hour)
    if error:
        return None, error
    
    try:
        date_str = f"{date.year}/{date.month:02d}/{date.day:02d} {date.hour:02d}:00"
        bazi = bazi_from_date_string(date_str)
        return bazi, None
    except ValueError as e:
        return None, ERROR_MESSAGES["invalid_date_format"].format(error=str(e))
    except NotImplementedError as e:
        return None, str(e)
    except Exception as e:
        return None, ERROR_MESSAGES["bazi_creation_failed"].format(error=str(e))


def create_bazi_from_ganzhi(date: GanzhiDateInput) -> Tuple[Optional[BaZi], Optional[str]]:
    """
    Create BaZi object from Gan-Zhi calendar date
    
    Args:
        date: Gan-Zhi date input
        
    Returns:
        Tuple of (BaZi object, error_message)
        Returns (None, error_message) if creation fails
        Returns (BaZi, None) if successful
    """
    try:
        # Parse and validate all pillars
        pillars = []
        pillar_names = ["year", "month", "day", "hour"]
        pillar_strings = [
            date.year_pillar,
            date.month_pillar,
            date.day_pillar,
            date.hour_pillar
        ]
        
        for pillar_str in pillar_strings:
            if not pillar_str:
                return None, ERROR_MESSAGES["invalid_ganzhi"].format(ganzhi="")
            
            is_valid, error_msg, parsed = validate_ganzhi(pillar_str)
            if not is_valid:
                return None, error_msg
            
            stem, branch = parsed
            pillars.append(Pillar(stem, branch))
        
        # Calculate xun_kong from day pillar
        xun_kong_1, xun_kong_2 = BaZi.calculate_xun_kong(pillars[2])  # day pillar
        
        # Create BaZi object
        bazi = BaZi(
            pillars[0],  # year
            pillars[1],  # month
            pillars[2],  # day
            pillars[3],  # hour
            xun_kong_1,
            xun_kong_2
        )
        
        return bazi, None
        
    except ValueError as e:
        return None, ERROR_MESSAGES["invalid_ganzhi_combination"].format(error=str(e))
    except Exception as e:
        return None, ERROR_MESSAGES["bazi_creation_failed"].format(error=str(e))


def create_bazi_from_inputs(request: DivinationRequest) -> Tuple[Optional[BaZi], Optional[str]]:
    """
    Create BaZi object from divination request
    
    Args:
        request: Divination request containing date inputs
        
    Returns:
        Tuple of (BaZi object, error_message)
        Returns (None, error_message) if creation fails
        Returns (BaZi, None) if successful
    """
    if request.use_western_date:
        if not request.western_date:
            return None, "錯誤：缺少西曆日期輸入"
        return create_bazi_from_western_date(request.western_date)
    else:
        if not request.ganzhi_date:
            return None, "錯誤：缺少干支日期輸入"
        return create_bazi_from_ganzhi(request.ganzhi_date)


def get_hexagram_code_from_button_method(button_input: ButtonMethodInput) -> Tuple[str, List[int]]:
    """
    Get hexagram code and changing lines from button method input
    
    Args:
        button_input: Button method input
        
    Returns:
        Tuple of (hexagram_code, changing_lines)
        hexagram_code is a 6-character string of '0' and '1'
        changing_lines is a list of line numbers (1-6) that are changing
    """
    hexagram_code = ""
    changing_lines = []
    
    yao_inputs = [
        (button_input.yao1_type, button_input.yao1_changing, 1),
        (button_input.yao2_type, button_input.yao2_changing, 2),
        (button_input.yao3_type, button_input.yao3_changing, 3),
        (button_input.yao4_type, button_input.yao4_changing, 4),
        (button_input.yao5_type, button_input.yao5_changing, 5),
        (button_input.yao6_type, button_input.yao6_changing, 6),
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
    
    return hexagram_code, changing_lines


def get_hexagram_code_from_name_method(name_input: NameMethodInput) -> Tuple[str, Optional[str], List[int]]:
    """
    Get hexagram code and changing lines from name method input
    
    Args:
        name_input: Name method input
        
    Returns:
        Tuple of (hexagram_code, error_message, changing_lines)
        If successful, error_message is None
        If failed, hexagram_code is empty and error_message contains the error
        changing_lines is a list of line numbers (1-6) that are changing
    """
    hexagram_code = ""
    changing_lines = []
    
    # Try to get hexagram code from selected code first
    if name_input.selected_hexagram_code and len(name_input.selected_hexagram_code) == 6:
        hexagram_code = name_input.selected_hexagram_code
    else:
        # Try to search by name
        matches = search_hexagram_by_name(name_input.hexagram_name_query)
        if not matches:
            return "", ERROR_MESSAGES["hexagram_not_found"].format(query=name_input.hexagram_name_query), []
        elif len(matches) > 1:
            match_names = ', '.join([name for _, name in matches])
            return "", ERROR_MESSAGES["multiple_hexagram_matches"].format(matches=match_names), []
        else:
            hexagram_code = matches[0][0]
    
    # Extract changing lines from checkboxes
    if name_input.changing_lines and len(name_input.changing_lines) == 6:
        for i, is_changing in enumerate(name_input.changing_lines):
            if is_changing:
                changing_lines.append(i + 1)
    
    return hexagram_code, None, changing_lines


def get_hexagram_code_from_inputs(request: DivinationRequest) -> Tuple[str, Optional[str], List[int]]:
    """
    Get hexagram code and changing lines from divination request
    
    Args:
        request: Divination request containing hexagram inputs
        
    Returns:
        Tuple of (hexagram_code, error_message, changing_lines)
        If successful, error_message is None
        If failed, hexagram_code is empty and error_message contains the error
        changing_lines is a list of line numbers (1-6) that are changing
    """
    if request.use_button_method:
        if not request.button_method:
            return "", "錯誤：缺少按鈕方法輸入", []
        hexagram_code, changing_lines = get_hexagram_code_from_button_method(request.button_method)
        return hexagram_code, None, changing_lines
    else:
        if not request.name_method:
            return "", "錯誤：缺少名稱方法輸入", []
        return get_hexagram_code_from_name_method(request.name_method)


def perform_divination(hexagram_code: str, bazi: BaZi, changing_lines: List[int], is_mobile: bool = False) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], Optional[List[Any]], Optional[str]]:
    """
    Perform the actual divination calculation
    
    Args:
        hexagram_code: 6-character hexagram code
        bazi: BaZi object
        changing_lines: List of changing line numbers (1-6)
        is_mobile: Whether to use mobile-friendly format (default: False)
        
    Returns:
        Tuple of (formatted_result_with_prompt, formatted_result_without_prompt, result_json, yao_list, error_message)
        If successful, error_message is None and formatted results contain the formatted output
        If failed, formatted results are None and error_message contains the error
    """
    # Validate hexagram code
    is_valid, error_msg = validate_hexagram_code(hexagram_code)
    if not is_valid:
        return None, None, None, None, error_msg
    
    # Perform divination
    try:
        yao_list, result_json = six_yao_divination(hexagram_code, bazi, changing_lines)
    except KeyError as e:
        return None, None, None, None, ERROR_MESSAGES["missing_hexagram_data"].format(error=str(e))
    except Exception as e:
        return None, None, None, None, ERROR_MESSAGES["divination_error"].format(error=str(e))
    
    # Format results using appropriate format based on is_mobile flag
    # Both functions now return (with_prompt, without_prompt)
    if is_mobile:
        formatted_result_with_prompt, formatted_result_without_prompt = format_divination_results_mobile(
            bazi,
            result_json,
            yao_list,
            show_shen_sha=True,
            for_gradio=True,
            show_tian_gan=SHOW_TIAN_GAN
        )
    else:
        formatted_result_with_prompt, formatted_result_without_prompt = format_divination_results_pc(
            bazi,
            result_json,
            yao_list,
            show_shen_sha=True,
            for_gradio=True,
            show_tian_gan=SHOW_TIAN_GAN
        )
    
    return formatted_result_with_prompt, formatted_result_without_prompt, result_json, yao_list, None


def process_divination_request(request: DivinationRequest, is_mobile: bool = False) -> str:
    """
    Process a complete divination request
    
    This is the main entry point for processing divination requests.
    It orchestrates all the steps: creating BaZi, getting hexagram code,
    and performing divination.
    
    Args:
        request: Complete divination request
        
    Returns:
        Formatted divination result string, or error message if processing fails
    """
    try:
        # Step 1: Create BaZi object
        bazi, error = create_bazi_from_inputs(request)
        if error:
            return error
        
        # Step 2: Get hexagram code and changing lines
        hexagram_code, error, changing_lines = get_hexagram_code_from_inputs(request)
        if error:
            return error
        
        # Step 3: Perform divination
        result_with_prompt, result_without_prompt, result_json, yao_list, error = perform_divination(hexagram_code, bazi, changing_lines, is_mobile=is_mobile)
        if error:
            return error
        
        return result_with_prompt
        
    except Exception as e:
        return ERROR_MESSAGES["general_error"].format(error=str(e))


# Legacy wrapper function for backward compatibility
# This maintains the same signature as the original process_divination function
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
    name_yao4_changing, name_yao5_changing, name_yao6_changing,
    # Display options
    is_mobile: bool = False
) -> str:
    """
    Main processing function for divination (legacy wrapper)
    
    This function maintains backward compatibility with the original signature
    while using the new refactored internal functions.
    
    Returns:
        Formatted text output matching test_liu_yao.py format
    """
    # Build request object from parameters
    # Convert to int in case Number components return floats
    request = DivinationRequest(
        use_western_date=use_western_date,
        western_date=WesternDateInput(year=int(year), month=int(month), day=int(day), hour=int(hour)) if use_western_date else None,
        ganzhi_date=GanzhiDateInput(
            year_pillar=year_pillar_str or "",
            month_pillar=month_pillar_str or "",
            day_pillar=day_pillar_str or "",
            hour_pillar=hour_pillar_str or ""
        ) if not use_western_date else None,
        use_button_method=use_button_method,
        button_method=ButtonMethodInput(
            yao1_type=yao1_type or "陽",
            yao1_changing=bool(yao1_changing),
            yao2_type=yao2_type or "陽",
            yao2_changing=bool(yao2_changing),
            yao3_type=yao3_type or "陽",
            yao3_changing=bool(yao3_changing),
            yao4_type=yao4_type or "陽",
            yao4_changing=bool(yao4_changing),
            yao5_type=yao5_type or "陽",
            yao5_changing=bool(yao5_changing),
            yao6_type=yao6_type or "陽",
            yao6_changing=bool(yao6_changing),
        ) if use_button_method else None,
        name_method=NameMethodInput(
            hexagram_name_query=hexagram_name_query or "",
            selected_hexagram_code=selected_hexagram_code or "",
            changing_lines=[
                bool(name_yao1_changing),
                bool(name_yao2_changing),
                bool(name_yao3_changing),
                bool(name_yao4_changing),
                bool(name_yao5_changing),
                bool(name_yao6_changing),
            ]
        ) if not use_button_method else None
    )
    
    return process_divination_request(request, is_mobile=is_mobile)


def process_divination_for_ui(
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
    name_yao4_changing, name_yao5_changing, name_yao6_changing,
    # Display options
    is_mobile: bool = False
) -> tuple[str, str]:
    """
    Process divination for UI, returning both versions (with and without prompt)
    
    This function is similar to process_divination but returns both formatted results.
    
    Returns:
        Tuple of (formatted_result_with_prompt, formatted_result_without_prompt)
        If error occurs, both values will be the error message string
    """
    # Build request object from parameters
    # Convert to int in case Number components return floats
    request = DivinationRequest(
        use_western_date=use_western_date,
        western_date=WesternDateInput(year=int(year), month=int(month), day=int(day), hour=int(hour)) if use_western_date else None,
        ganzhi_date=GanzhiDateInput(
            year_pillar=year_pillar_str or "",
            month_pillar=month_pillar_str or "",
            day_pillar=day_pillar_str or "",
            hour_pillar=hour_pillar_str or ""
        ) if not use_western_date else None,
        use_button_method=use_button_method,
        button_method=ButtonMethodInput(
            yao1_type=yao1_type or "陽",
            yao1_changing=bool(yao1_changing),
            yao2_type=yao2_type or "陽",
            yao2_changing=bool(yao2_changing),
            yao3_type=yao3_type or "陽",
            yao3_changing=bool(yao3_changing),
            yao4_type=yao4_type or "陽",
            yao4_changing=bool(yao4_changing),
            yao5_type=yao5_type or "陽",
            yao5_changing=bool(yao5_changing),
            yao6_type=yao6_type or "陽",
            yao6_changing=bool(yao6_changing),
        ) if use_button_method else None,
        name_method=NameMethodInput(
            hexagram_name_query=hexagram_name_query or "",
            selected_hexagram_code=selected_hexagram_code or "",
            changing_lines=[
                bool(name_yao1_changing),
                bool(name_yao2_changing),
                bool(name_yao3_changing),
                bool(name_yao4_changing),
                bool(name_yao5_changing),
                bool(name_yao6_changing),
            ]
        ) if not use_button_method else None
    )
    
    try:
        # Step 1: Create BaZi object
        bazi, error = create_bazi_from_inputs(request)
        if error:
            return error, error
        
        # Step 2: Get hexagram code and changing lines
        hexagram_code, error, changing_lines = get_hexagram_code_from_inputs(request)
        if error:
            return error, error
        
        # Step 3: Perform divination
        result_with_prompt, result_without_prompt, result_json, yao_list, error = perform_divination(hexagram_code, bazi, changing_lines, is_mobile=is_mobile)
        if error:
            return error, error
        
        return result_with_prompt, result_without_prompt
        
    except Exception as e:
        error_msg = ERROR_MESSAGES["general_error"].format(error=str(e))
        return error_msg, error_msg

