"""
Handlers module for Gradio UI

This module contains handler functions for processing user inputs and events.
Most handlers are embedded in component files for better cohesion. This module
provides shared utilities and wrapper functions.
"""

from .divination_handlers import (
    process_divination,
    process_divination_request,
    DivinationRequest,
    WesternDateInput,
    GanzhiDateInput,
    ButtonMethodInput,
    NameMethodInput
)
from .date_handlers import determine_date_input_method
from .hexagram_handlers import (
    extract_changing_lines_from_checkboxes,
    get_hexagram_code_from_state_or_dropdown
)

__all__ = [
    "process_divination",
    "process_divination_request",
    "DivinationRequest",
    "WesternDateInput",
    "GanzhiDateInput",
    "ButtonMethodInput",
    "NameMethodInput",
    "determine_date_input_method",
    "extract_changing_lines_from_checkboxes",
    "get_hexagram_code_from_state_or_dropdown",
]

