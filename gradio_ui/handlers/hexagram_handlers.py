"""
Hexagram input handlers for the Gradio UI

This module contains handler functions for hexagram inputs. Most handlers
are embedded in the component files (hexagram_inputs.py) for better cohesion.
This module serves as documentation and may contain shared hexagram handling utilities.
"""

from typing import List, Optional, Tuple
from ..utils.hexagram_utils import (
    search_hexagram_by_name,
    get_hexagram_code_from_dropdown,
    calculate_changed_hexagram
)
from ..config import DEFAULT_HEXAGRAM_CODE
from liu_yao import HEXAGRAM_MAP

# Note: Most hexagram handlers are embedded in gradio_ui/components/hexagram_inputs.py
# to keep UI logic and handlers together. This module is reserved for:
# - Shared hexagram handling utilities
# - Handler functions that need to be shared across multiple components
# - Future hexagram-related handler extensions


def extract_changing_lines_from_checkboxes(
    checkbox_values: List[bool],
    visual_order: bool = False
) -> List[int]:
    """
    Extract changing line numbers from checkbox values
    
    Args:
        checkbox_values: List of 6 boolean values indicating if lines are changing
        visual_order: If True, checkboxes are in visual order (6,5,4,3,2,1)
                     If False, checkboxes are in logical order (1,2,3,4,5,6)
        
    Returns:
        List of line numbers (1-6) that are changing
    """
    changing_lines = []
    
    if visual_order:
        # Checkboxes are in visual order: 6,5,4,3,2,1
        # Index 0 = line 6, index 5 = line 1
        for i, is_changing in enumerate(checkbox_values):
            if is_changing:
                line_num = 6 - i
                changing_lines.append(line_num)
    else:
        # Checkboxes are in logical order: 1,2,3,4,5,6
        for i, is_changing in enumerate(checkbox_values):
            if is_changing:
                changing_lines.append(i + 1)
    
    return sorted(changing_lines)


def get_hexagram_code_from_state_or_dropdown(
    hexagram_code_state: Optional[str],
    hexagram_dropdown_value: Optional[str]
) -> str:
    """
    Get hexagram code from state variable or dropdown value
    
    Args:
        hexagram_code_state: Hexagram code from state variable
        hexagram_dropdown_value: Hexagram code from dropdown selection
        
    Returns:
        Valid hexagram code (defaults to DEFAULT_HEXAGRAM_CODE if invalid)
    """
    code = ""
    
    # Try dropdown first
    if hexagram_dropdown_value:
        try:
            extracted_code = get_hexagram_code_from_dropdown(hexagram_dropdown_value)
            if extracted_code and len(extracted_code) == 6 and extracted_code in HEXAGRAM_MAP:
                code = extracted_code
        except (ValueError, AttributeError, TypeError, KeyError):
            pass
    
    # Try state variable
    if not code:
        if hexagram_code_state and len(hexagram_code_state) == 6 and hexagram_code_state in HEXAGRAM_MAP:
            code = hexagram_code_state
    
    # Default fallback
    if not code or len(code) != 6 or code not in HEXAGRAM_MAP:
        code = DEFAULT_HEXAGRAM_CODE
    
    return code


def extract_changing_lines_from_checkboxes(
    yao1_changing: bool,
    yao2_changing: bool,
    yao3_changing: bool,
    yao4_changing: bool,
    yao5_changing: bool,
    yao6_changing: bool
) -> List[int]:
    """
    Extract changing line numbers from checkbox values
    
    Checkboxes are in visual order (6,5,4,3,2,1 from top to bottom),
    where yao1_changing corresponds to line 6 (top) and yao6_changing corresponds to line 1 (bottom).
    
    Args:
        yao1_changing: Checkbox for line 6 (top)
        yao2_changing: Checkbox for line 5
        yao3_changing: Checkbox for line 4
        yao4_changing: Checkbox for line 3
        yao5_changing: Checkbox for line 2
        yao6_changing: Checkbox for line 1 (bottom)
        
    Returns:
        List of changing line numbers (1-6)
    """
    changing_lines = []
    # Map checkboxes to line numbers (visual order: yao1=line6, yao6=line1)
    checkbox_mapping = [
        (yao6_changing, 1),  # line 1 (bottom)
        (yao5_changing, 2),  # line 2
        (yao4_changing, 3),  # line 3
        (yao3_changing, 4),  # line 4
        (yao2_changing, 5),  # line 5
        (yao1_changing, 6),  # line 6 (top)
    ]
    
    for is_changing, line_num in checkbox_mapping:
        if is_changing:
            changing_lines.append(line_num)
    
    return changing_lines

