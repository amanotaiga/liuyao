"""
Validation utilities for input validation

Functions for validating dates, hexagrams, Gan-Zhi combinations, etc.
"""

from typing import Optional, Tuple
from ..config import (
    MIN_YEAR, MAX_YEAR,
    MIN_MONTH, MAX_MONTH,
    MIN_DAY, MAX_DAY,
    MIN_HOUR, MAX_HOUR,
    ERROR_MESSAGES,
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES
)
from liu_yao import HEXAGRAM_MAP


def validate_year(year: int) -> Optional[str]:
    """Validate year range
    
    Args:
        year: Year to validate
    
    Returns:
        Error message if invalid, None if valid
    """
    if not (MIN_YEAR <= year <= MAX_YEAR):
        return ERROR_MESSAGES["invalid_year"]
    return None


def validate_month(month: int) -> Optional[str]:
    """Validate month range
    
    Args:
        month: Month to validate
    
    Returns:
        Error message if invalid, None if valid
    """
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return ERROR_MESSAGES["invalid_month"]
    return None


def validate_day(day: int) -> Optional[str]:
    """Validate day range
    
    Args:
        day: Day to validate
    
    Returns:
        Error message if invalid, None if valid
    """
    if not (MIN_DAY <= day <= MAX_DAY):
        return ERROR_MESSAGES["invalid_day"]
    return None


def validate_hour(hour: int) -> Optional[str]:
    """Validate hour range
    
    Args:
        hour: Hour to validate
    
    Returns:
        Error message if invalid, None if valid
    """
    if not (MIN_HOUR <= hour <= MAX_HOUR):
        return ERROR_MESSAGES["invalid_hour"]
    return None


def validate_date(year: int, month: int, day: int, hour: int) -> Optional[str]:
    """Validate complete date
    
    Args:
        year: Year
        month: Month
        day: Day
        hour: Hour
    
    Returns:
        Error message if invalid, None if valid
    """
    error = validate_year(year)
    if error:
        return error
    
    error = validate_month(month)
    if error:
        return error
    
    error = validate_day(day)
    if error:
        return error
    
    error = validate_hour(hour)
    if error:
        return error
    
    return None


def validate_ganzhi(ganzhi_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate and parse Gan-Zhi string
    
    Args:
        ganzhi_str: Gan-Zhi string like "甲子"
    
    Returns:
        Tuple of (is_valid, error_message, (stem, branch))
        If valid, error_message is None and tuple contains (stem, branch)
        If invalid, tuple contains error message and (None, None)
    """
    if not ganzhi_str or len(ganzhi_str) != 2:
        return (
            False,
            ERROR_MESSAGES["invalid_ganzhi"].format(ganzhi=ganzhi_str),
            None
        )
    
    stem = ganzhi_str[0]
    branch = ganzhi_str[1]
    
    if stem not in HEAVENLY_STEMS:
        return (
            False,
            ERROR_MESSAGES["invalid_ganzhi"].format(ganzhi=ganzhi_str),
            None
        )
    
    if branch not in EARTHLY_BRANCHES:
        return (
            False,
            ERROR_MESSAGES["invalid_ganzhi"].format(ganzhi=ganzhi_str),
            None
        )
    
    return (True, None, (stem, branch))


def validate_hexagram_code(code: str) -> Tuple[bool, Optional[str]]:
    """Validate hexagram code
    
    Args:
        code: Hexagram code to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code or len(code) != 6:
        return (False, ERROR_MESSAGES["invalid_hexagram_code"].format(code=code))
    
    if not all(c in ('0', '1') for c in code):
        return (False, ERROR_MESSAGES["invalid_hexagram_code"].format(code=code))
    
    if code not in HEXAGRAM_MAP:
        return (False, ERROR_MESSAGES["invalid_hexagram_code"].format(code=code))
    
    return (True, None)


def validate_changing_lines(changing_lines: list, max_lines: int = 6) -> bool:
    """Validate changing line numbers
    
    Args:
        changing_lines: List of line numbers
        max_lines: Maximum number of lines (default 6)
    
    Returns:
        True if all lines are valid (1 to max_lines), False otherwise
    """
    if not changing_lines:
        return True
    
    return all(1 <= line <= max_lines for line in changing_lines)

