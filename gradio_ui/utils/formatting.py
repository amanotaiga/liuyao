"""
Formatting utilities for divination results

This module contains functions for formatting divination results into
human-readable strings. The main function format_divination_results()
is shared between the test script and the Gradio UI to ensure identical
output formatting.
"""

import sys
import io
from typing import List, Dict, Any

from liu_yao import format_liu_yao_display, display_shen_sha_definitions
from ba_zi_base import BaZi


def format_divination_results(
    bazi: BaZi,
    result_json: Dict[str, Any],
    yao_list: List[Any],
    show_shen_sha: bool = True,
    for_gradio: bool = False
) -> str:
    """Format divination results as a string, matching the exact output format.
    
    This function is reused by both test_liu_yao.py and gradio_ui.py to ensure
    identical output formatting.
    
    Args:
        bazi: BaZi object
        result_json: Result dictionary from six_yao_divination
        yao_list: List of YaoDetails from six_yao_divination
        show_shen_sha: Whether to show shen sha markers
        for_gradio: Whether this is for Gradio interface (uses 5 chars for yang) vs terminal (6 chars)
    
    Returns:
        Formatted string output
    """
    output_parts = []
    
    output_parts.append(
        f"天干地支曆: {bazi.year.to_string()}年 "
        f"{bazi.month.to_string()}月 "
        f"{bazi.day.to_string()}日 "
        f"{bazi.hour.to_string()}時\n"
    )
    ben_gua_name = result_json.get('ben_gua_name', 'N/A')
    output_parts.append(f"本卦: {ben_gua_name}\n")
    
    if 'bian_gua_name' in result_json:
        bian_gua_name = result_json.get('bian_gua_name', 'N/A')
        output_parts.append(f"變卦: {bian_gua_name}\n")
    
    # Display xun_kong (旬空) information
    if 'ba_zi' in result_json:
        ba_zi = result_json['ba_zi']
        xun_kong_list = []
        if 'xun_kong_1' in ba_zi and ba_zi['xun_kong_1']:
            xun_kong_list.append(ba_zi['xun_kong_1'])
        if 'xun_kong_2' in ba_zi and ba_zi['xun_kong_2']:
            xun_kong_list.append(ba_zi['xun_kong_2'])
        if xun_kong_list:
            output_parts.append(f"旬空: {''.join(xun_kong_list)}\n")
    
    # Display all shen sha definitions
    if 'shen_sa' in result_json:
        # Capture output from display_shen_sha_definitions
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            display_shen_sha_definitions(result_json['shen_sa'])
            shen_sha_output = buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        output_parts.append(shen_sha_output)
    
    # Display 三合局 if exists
    if 'san_he_ju' in result_json and result_json['san_he_ju']:
        output_parts.append(f"\n三合局: {result_json['san_he_ju']}\n")
    
    # Main table
    output_parts.append("=" * 70 + "\n")
    output_parts.append(
        format_liu_yao_display(yao_list, show_shen_sha=show_shen_sha, for_gradio=for_gradio) + "\n"
    )
    
    return "".join(output_parts)

