"""
UI Builder for Gradio Interface

This module orchestrates all UI components to create the complete Gradio interface.
It uses the extracted components, handlers, and utilities to build a maintainable UI.
"""

import gradio as gr
from liu_yao import HEXAGRAM_MAP

from .config import UI_CONFIG
from .utils.static_loader import load_static_assets
from .components.date_inputs import create_date_inputs
from .components.hexagram_inputs import create_hexagram_inputs
from .components.result_display import create_result_display
from .handlers.divination_handlers import process_divination, process_divination_for_ui
from .handlers.hexagram_handlers import get_hexagram_code_from_state_or_dropdown


def create_process_regular_tab_handler(
    date_inputs,
    hexagram_inputs,
    result_display
):
    """
    Create handler function for regular tab (name search) calculation button
    
    Args:
        date_inputs: DateInputComponents instance
        hexagram_inputs: HexagramInputComponents instance  
        result_display: ResultDisplay instance
        
    Returns:
        Handler function for process_regular_tab
    """
    def process_regular_tab(
        year, month, day, hour,
        year_pillar_str, month_pillar_str, day_pillar_str, hour_pillar_str,
        active_date_tab,
        hexagram_dropdown_value, hexagram_code_state,
        yao1_changing, yao2_changing, yao3_changing,
        yao4_changing, yao5_changing, yao6_changing,
        compact_view
    ):
        """Process divination for regular tab (name search method)"""
        # Determine which date method to use based on active tab
        # Use ganzhi if active tab is "ganzhi" AND all pillars are filled
        if active_date_tab == "ganzhi" and year_pillar_str and month_pillar_str and day_pillar_str and hour_pillar_str:
            use_western = False
        else:
            use_western = True
        
        # Get hexagram code from dropdown or state
        code = get_hexagram_code_from_state_or_dropdown(
            hexagram_code_state,
            hexagram_dropdown_value
        )
        
        # Map checkboxes to changing lines (checkboxes are in visual order: 6,5,4,3,2,1)
        # yao1_changing is for line 6, yao6_changing is for line 1
        checkbox_values = [
            yao6_changing,  # line 1
            yao5_changing,  # line 2
            yao4_changing,  # line 3
            yao3_changing,  # line 4
            yao2_changing,  # line 5
            yao1_changing,  # line 6
        ]
        changing_1 = bool(checkbox_values[0]) if checkbox_values[0] is not None else False
        changing_2 = bool(checkbox_values[1]) if checkbox_values[1] is not None else False
        changing_3 = bool(checkbox_values[2]) if checkbox_values[2] is not None else False
        changing_4 = bool(checkbox_values[3]) if checkbox_values[3] is not None else False
        changing_5 = bool(checkbox_values[4]) if checkbox_values[4] is not None else False
        changing_6 = bool(checkbox_values[5]) if checkbox_values[5] is not None else False
        
        with_prompt, without_prompt = process_divination_for_ui(
            use_western,
            year, month, day, hour,
            year_pillar_str, "", month_pillar_str, "",
            day_pillar_str, "", hour_pillar_str, "",
            False,  # use_button_method
            "陽", False, "陽", False, "陽", False,
            "陽", False, "陽", False, "陽", False,
            "", code,
            changing_1, changing_2, changing_3, changing_4, changing_5, changing_6,
            is_mobile=bool(compact_view)
        )
        # Return with_prompt for display, without_prompt for copy
        return with_prompt, without_prompt
    
    return process_regular_tab


def create_process_clickable_tab_handler(
    date_inputs,
    hexagram_inputs,
    result_display
):
    """
    Create handler function for clickable tab calculation button
    
    Args:
        date_inputs: DateInputComponents instance
        hexagram_inputs: HexagramInputComponents instance
        result_display: ResultDisplay instance
        
    Returns:
        Handler function for process_clickable_tab
    """
    def process_clickable_tab(
        year, month, day, hour,
        year_pillar_str, month_pillar_str, day_pillar_str, hour_pillar_str,
        active_date_tab,
        clickable_hexagram_code,
        clickable_yao1_changing, clickable_yao2_changing, clickable_yao3_changing,
        clickable_yao4_changing, clickable_yao5_changing, clickable_yao6_changing,
        compact_view
    ):
        """Process divination for clickable tab"""
        # Determine which date method to use based on active tab
        # Use ganzhi if active tab is "ganzhi" AND all pillars are filled
        if active_date_tab == "ganzhi" and year_pillar_str and month_pillar_str and day_pillar_str and hour_pillar_str:
            use_western = False
        else:
            use_western = True
        
        # Get hexagram code from clickable tab
        code = clickable_hexagram_code if (
            clickable_hexagram_code and 
            len(clickable_hexagram_code) == 6 and 
            clickable_hexagram_code in HEXAGRAM_MAP
        ) else "111111"
        
        # Map checkboxes to changing lines
        changing_1 = bool(clickable_yao1_changing) if clickable_yao1_changing is not None else False
        changing_2 = bool(clickable_yao2_changing) if clickable_yao2_changing is not None else False
        changing_3 = bool(clickable_yao3_changing) if clickable_yao3_changing is not None else False
        changing_4 = bool(clickable_yao4_changing) if clickable_yao4_changing is not None else False
        changing_5 = bool(clickable_yao5_changing) if clickable_yao5_changing is not None else False
        changing_6 = bool(clickable_yao6_changing) if clickable_yao6_changing is not None else False
        
        with_prompt, without_prompt = process_divination_for_ui(
            use_western,
            year, month, day, hour,
            year_pillar_str, "", month_pillar_str, "",
            day_pillar_str, "", hour_pillar_str, "",
            False,  # use_button_method
            "陽", False, "陽", False, "陽", False,
            "陽", False, "陽", False, "陽", False,
            "", code,
            changing_1, changing_2, changing_3, changing_4, changing_5, changing_6,
            is_mobile=bool(compact_view)
        )
        # Return with_prompt for display, without_prompt for copy
        return with_prompt, without_prompt
    
    return process_clickable_tab


def create_process_coin_toss_tab_handler(
    date_inputs,
    hexagram_inputs,
    result_display
):
    """
    Create handler function for coin toss tab calculation button
    
    Args:
        date_inputs: DateInputComponents instance
        hexagram_inputs: HexagramInputComponents instance
        result_display: ResultDisplay instance
        
    Returns:
        Handler function for process_coin_toss_tab
    """
    def process_coin_toss_tab(
        year, month, day, hour,
        year_pillar_str, month_pillar_str, day_pillar_str, hour_pillar_str,
        active_date_tab,
        coin_toss_hexagram_code,
        coin_toss_yao1_changing, coin_toss_yao2_changing, coin_toss_yao3_changing,
        coin_toss_yao4_changing, coin_toss_yao5_changing, coin_toss_yao6_changing,
        compact_view
    ):
        """Process divination for coin toss tab"""
        # Determine which date method to use based on active tab
        # Use ganzhi if active tab is "ganzhi" AND all pillars are filled
        if active_date_tab == "ganzhi" and year_pillar_str and month_pillar_str and day_pillar_str and hour_pillar_str:
            use_western = False
        else:
            use_western = True
        
        # Get hexagram code from coin toss tab
        code = coin_toss_hexagram_code if (
            coin_toss_hexagram_code and 
            len(coin_toss_hexagram_code) == 6 and 
            coin_toss_hexagram_code in HEXAGRAM_MAP
        ) else "111111"
        
        # Map checkboxes to changing lines
        changing_1 = bool(coin_toss_yao1_changing) if coin_toss_yao1_changing is not None else False
        changing_2 = bool(coin_toss_yao2_changing) if coin_toss_yao2_changing is not None else False
        changing_3 = bool(coin_toss_yao3_changing) if coin_toss_yao3_changing is not None else False
        changing_4 = bool(coin_toss_yao4_changing) if coin_toss_yao4_changing is not None else False
        changing_5 = bool(coin_toss_yao5_changing) if coin_toss_yao5_changing is not None else False
        changing_6 = bool(coin_toss_yao6_changing) if coin_toss_yao6_changing is not None else False
        
        with_prompt, without_prompt = process_divination_for_ui(
            use_western,
            year, month, day, hour,
            year_pillar_str, "", month_pillar_str, "",
            day_pillar_str, "", hour_pillar_str, "",
            False,  # use_button_method
            "陽", False, "陽", False, "陽", False,
            "陽", False, "陽", False, "陽", False,
            "", code,
            changing_1, changing_2, changing_3, changing_4, changing_5, changing_6,
            is_mobile=bool(compact_view)
        )
        # Return with_prompt for display, without_prompt for copy
        return with_prompt, without_prompt
    
    return process_coin_toss_tab


def create_ui():
    """
    Create and return the Gradio interface
    
    This function orchestrates all components to build the complete UI.
    It uses extracted components, handlers, and utilities for better maintainability.
    
    Returns:
        Gradio Blocks interface
    """
    # Load static assets (CSS and JavaScript)
    custom_css = load_static_assets()
    
    with gr.Blocks(title=UI_CONFIG.title) as demo:
        gr.HTML(custom_css)
        
        # Title and description
        gr.Markdown("# 六爻排盤系統", elem_classes=["main-title"])
        gr.Markdown(
            "<p style='color: #868e96; font-size: 14px; margin-top: -6px; margin-bottom: 16px;'>輸入日期和卦象信息，進行六爻排盤</p>",
            elem_classes=["text-muted"]
        )
        gr.Markdown("---", elem_classes=["section-divider"])
        
        # Create date input components
        date_inputs = create_date_inputs()
        
        gr.Markdown("---", elem_classes=["section-divider"])
        
        # Create hexagram input components
        hexagram_inputs = create_hexagram_inputs()
        
        gr.Markdown("---", elem_classes=["section-divider"])
        
        # Create result display component
        result_display = create_result_display()
        
        # Wire up calculation buttons
        
        # Regular tab (name search) button
        process_regular_tab_fn = create_process_regular_tab_handler(
            date_inputs,
            hexagram_inputs,
            result_display
        )
        
        hexagram_inputs.name_search.calculate_btn.click(
            fn=process_regular_tab_fn,
            inputs=[
                date_inputs.western.year_dropdown,
                date_inputs.western.month_dropdown,
                date_inputs.western.day_dropdown,
                date_inputs.western.hour_dropdown,
                date_inputs.ganzhi.year_pillar_state,
                date_inputs.ganzhi.month_pillar_state,
                date_inputs.ganzhi.day_pillar_state,
                date_inputs.ganzhi.hour_pillar_state,
                date_inputs.active_date_tab_state,
                hexagram_inputs.name_search.hexagram_dropdown,
                hexagram_inputs.name_search.selected_hexagram_code_state,
                # Checkboxes in visual order: 6,5,4,3,2,1
                hexagram_inputs.name_search.changing_checkboxes[0],  # 6爻
                hexagram_inputs.name_search.changing_checkboxes[1],  # 5爻
                hexagram_inputs.name_search.changing_checkboxes[2],  # 4爻
                hexagram_inputs.name_search.changing_checkboxes[3],  # 3爻
                hexagram_inputs.name_search.changing_checkboxes[4],  # 2爻
                hexagram_inputs.name_search.changing_checkboxes[5],  # 1爻
                hexagram_inputs.name_search.compact_view_checkbox,
            ],
            outputs=[result_display.result_table, result_display.result_table_without_prompt]
        )
        
        # Clickable tab button
        process_clickable_tab_fn = create_process_clickable_tab_handler(
            date_inputs,
            hexagram_inputs,
            result_display
        )
        
        hexagram_inputs.clickable.calculate_btn.click(
            fn=process_clickable_tab_fn,
            inputs=[
                date_inputs.western.year_dropdown,
                date_inputs.western.month_dropdown,
                date_inputs.western.day_dropdown,
                date_inputs.western.hour_dropdown,
                date_inputs.ganzhi.year_pillar_state,
                date_inputs.ganzhi.month_pillar_state,
                date_inputs.ganzhi.day_pillar_state,
                date_inputs.ganzhi.hour_pillar_state,
                date_inputs.active_date_tab_state,
                hexagram_inputs.clickable.clickable_hexagram_code_state,
                hexagram_inputs.clickable.clickable_changing_state_vars[0],  # 1爻
                hexagram_inputs.clickable.clickable_changing_state_vars[1],  # 2爻
                hexagram_inputs.clickable.clickable_changing_state_vars[2],  # 3爻
                hexagram_inputs.clickable.clickable_changing_state_vars[3],  # 4爻
                hexagram_inputs.clickable.clickable_changing_state_vars[4],  # 5爻
                hexagram_inputs.clickable.clickable_changing_state_vars[5],  # 6爻
                hexagram_inputs.clickable.compact_view_checkbox,
            ],
            outputs=[result_display.result_table, result_display.result_table_without_prompt]
        )
        
        # Coin toss tab button
        process_coin_toss_tab_fn = create_process_coin_toss_tab_handler(
            date_inputs,
            hexagram_inputs,
            result_display
        )
        
        hexagram_inputs.coin_toss.calculate_btn.click(
            fn=process_coin_toss_tab_fn,
            inputs=[
                date_inputs.western.year_dropdown,
                date_inputs.western.month_dropdown,
                date_inputs.western.day_dropdown,
                date_inputs.western.hour_dropdown,
                date_inputs.ganzhi.year_pillar_state,
                date_inputs.ganzhi.month_pillar_state,
                date_inputs.ganzhi.day_pillar_state,
                date_inputs.ganzhi.hour_pillar_state,
                date_inputs.active_date_tab_state,
                hexagram_inputs.coin_toss.coin_toss_hexagram_code_state,
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[0],  # 1爻
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[1],  # 2爻
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[2],  # 3爻
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[3],  # 4爻
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[4],  # 5爻
                hexagram_inputs.coin_toss.coin_toss_changing_state_vars[5],  # 6爻
                hexagram_inputs.coin_toss.compact_view_checkbox,
            ],
            outputs=[result_display.result_table, result_display.result_table_without_prompt]
        )
    
    return demo

