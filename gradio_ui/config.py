"""
Configuration and constants for Gradio UI

Contains all constants, default values, and configuration settings
used throughout the Gradio interface.
"""

from typing import List, Dict
from dataclasses import dataclass


# Gan-Zhi (干支) constants
HEAVENLY_STEMS: List[str] = [
    "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"
]

EARTHLY_BRANCHES: List[str] = [
    "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"
]

# Default hexagram code (乾為天 - all yang lines)
DEFAULT_HEXAGRAM_CODE: str = "111111"

# Valid date ranges
MIN_YEAR: int = 1900
MAX_YEAR: int = 2100
MIN_MONTH: int = 1
MAX_MONTH: int = 12
MIN_DAY: int = 1
MAX_DAY: int = 31
MIN_HOUR: int = 0
MAX_HOUR: int = 23


@dataclass
class ColorConfig:
    """Color configuration for hexagram lines"""
    # Yang line colors
    yang_bg: str = "#ef4444"
    yang_bg_changing: str = "#e96a6a"
    yang_border: str = "#b71c1c"
    yang_border_changing: str = "#d32f2f"
    yang_text: str = "#8b0000"
    yang_text_changing: str = "#b71c1c"
    
    # Yin line colors
    yin_bg: str = "#75cc0d"
    yin_bg_changing: str = "#64db68"
    yin_border: str = "#1b5e20"
    yin_border_changing: str = "#2e7d32"
    yin_text: str = "#0d4f0d"
    yin_text_changing: str = "#1b5e20"
    
    # Shadows
    yang_shadow: str = "0 1px 3px rgba(183, 28, 28, 0.4)"
    yang_shadow_changing: str = "0 2px 6px rgba(211, 47, 47, 0.5)"
    yin_shadow: str = "0 1px 3px rgba(27, 94, 32, 0.4)"
    yin_shadow_changing: str = "0 2px 6px rgba(46, 125, 50, 0.5)"


@dataclass
class UIConfig:
    """UI configuration settings"""
    title: str = "六爻排盤系統"
    default_year_range: tuple = (1900, 2101)
    hexagram_search_cache_size: int = 100
    line_symbol_yang: str = "▅▅▅▅▅▅"
    line_symbol_yin: str = "▅▅▅     ▅▅▅"
    line_symbol_yin_clickable: str = "▅▅▅     ▅▅▅"
    change_mark_yang: str = " ○"
    change_mark_yin: str = " ×"


# Global configuration instances
COLOR_CONFIG = ColorConfig()
UI_CONFIG = UIConfig()


# Pillar labels for display
PILLAR_LABELS: List[str] = ["年柱", "月柱", "日柱", "時柱"]


# Error messages
ERROR_MESSAGES: Dict[str, str] = {
    "invalid_year": "錯誤：年份必須在1900-2100之間",
    "invalid_month": "錯誤：月份必須在1-12之間",
    "invalid_day": "錯誤：日期必須在1-31之間",
    "invalid_hour": "錯誤：小時必須在0-23之間",
    "invalid_date_format": "錯誤：日期格式錯誤：{error}",
    "bazi_creation_failed": "錯誤：無法創建八字：{error}",
    "invalid_ganzhi": "錯誤：無效的干支：{ganzhi}。請確保已選擇完整的四柱。",
    "invalid_ganzhi_combination": "錯誤：無效的干支組合：{error}",
    "hexagram_not_found": "錯誤：無法找到包含 '{query}' 的卦象",
    "multiple_hexagram_matches": "錯誤：找到多個匹配的卦象，請從下拉列表中選擇：{matches}",
    "invalid_hexagram_code": "錯誤：無效的卦象代碼：{code}",
    "missing_hexagram_data": "錯誤：卦象數據缺失：{error}",
    "divination_error": "錯誤：排盤過程中出錯：{error}",
    "general_error": "錯誤：發生錯誤：{error}",
}

