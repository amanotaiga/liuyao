"""
Date input handlers for the Gradio UI

This module contains handler functions for date inputs. Most handlers
are embedded in the component files (date_inputs.py) for better cohesion.
This module serves as documentation and may contain shared date handling utilities.
"""

from typing import Optional

# Note: Most date handlers are embedded in gradio_ui/components/date_inputs.py
# to keep UI logic and handlers together. This module is reserved for:
# - Shared date handling utilities
# - Handler functions that need to be shared across multiple components
# - Future date-related handler extensions


def determine_date_input_method(
    year_pillar: Optional[str],
    month_pillar: Optional[str],
    day_pillar: Optional[str],
    hour_pillar: Optional[str]
) -> bool:
    """
    Determine if Western date input should be used based on Gan-Zhi pillar values
    
    Args:
        year_pillar: Year pillar string (e.g., "甲子")
        month_pillar: Month pillar string
        day_pillar: Day pillar string
        hour_pillar: Hour pillar string
        
    Returns:
        True if Western date method should be used, False if Gan-Zhi method should be used
    """
    # Use Western date if any pillar is missing/empty
    if not (year_pillar and month_pillar and day_pillar and hour_pillar):
        return True
    return False

