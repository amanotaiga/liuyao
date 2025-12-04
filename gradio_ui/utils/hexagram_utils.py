"""
Hexagram utility functions

Functions for searching, calculating, and manipulating hexagrams.
"""

from typing import List, Tuple, Optional
from functools import lru_cache

from liu_yao import HEXAGRAM_MAP
from ..config import DEFAULT_HEXAGRAM_CODE


@lru_cache(maxsize=100)
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


def get_hexagram_code_from_dropdown(dropdown_value: str) -> str:
    """Extract hexagram code from dropdown value
    
    Args:
        dropdown_value: Dropdown value in format "code - name" or just "code"
    
    Returns:
        Hexagram code string
    """
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
        return DEFAULT_HEXAGRAM_CODE
    
    changed_code = list(original_code)
    for line_num in changing_line_nums:
        if 1 <= line_num <= 6:
            index = line_num - 1  # Convert to 0-based index
            # Flip: 0 -> 1, 1 -> 0
            changed_code[index] = '1' if changed_code[index] == '0' else '0'
    
    return ''.join(changed_code)


def validate_hexagram_code(code: str) -> bool:
    """Validate hexagram code format
    
    Args:
        code: Hexagram code to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not code or len(code) != 6:
        return False
    if not all(c in ('0', '1') for c in code):
        return False
    return code in HEXAGRAM_MAP


def get_hexagram_name(code: str) -> Optional[str]:
    """Get hexagram name from code
    
    Args:
        code: Hexagram code
    
    Returns:
        Hexagram name or None if not found
    """
    if code in HEXAGRAM_MAP:
        return HEXAGRAM_MAP[code].name
    return None

