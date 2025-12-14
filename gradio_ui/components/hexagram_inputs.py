"""
Hexagram input components for the Gradio UI

This module contains reusable components for hexagram input:
- Name search tab with dropdown selection
- Clickable hexagram lines tab with interactive button selection
"""

from dataclasses import dataclass
from typing import List, Tuple, Callable

import gradio as gr

from ..config import DEFAULT_HEXAGRAM_CODE, UI_CONFIG
from ..utils.html_generator import (
    create_line_html,
    create_changed_line_html
)
from ..utils.hexagram_utils import (
    search_hexagram_by_name,
    search_hexagram_by_trigrams,
    get_hexagram_code_from_dropdown,
    calculate_changed_hexagram
)


@dataclass
class NameSearchHexagramInputs:
    """Components for hexagram name search input tab"""
    element_buttons: List[Tuple[str, gr.Button]]
    outer_element_state: gr.State
    inner_element_state: gr.State
    hexagram_dropdown: gr.Dropdown
    selected_hexagram_code_state: gr.State
    changing_checkboxes: List[gr.Checkbox]
    hexagram_line_containers: List[gr.HTML]
    changed_hexagram_line_containers: List[gr.HTML]
    calculate_btn: gr.Button
    compact_view_checkbox: gr.Checkbox


@dataclass
class ClickableHexagramInputs:
    """Components for clickable hexagram input tab"""
    clickable_hexagram_code_state: gr.State
    clickable_changing_state_vars: List[gr.State]  # 6 state variables
    clickable_line_buttons: List[Tuple[int, gr.Button]]  # (line_num, button)
    clickable_changing_checkboxes: List[gr.Checkbox]
    clickable_changed_hexagram_line_containers: List[gr.HTML]
    calculate_btn: gr.Button
    compact_view_checkbox: gr.Checkbox


@dataclass
class CoinTossHexagramInputs:
    """Components for coin toss input tab"""
    coin_toss_hexagram_code_state: gr.State
    coin_toss_changing_state_vars: List[gr.State]  # 6 state variables
    outcome_buttons: List[List[gr.Button]]  # 6 lines × 4 outcome buttons per line
    selected_outcome_states: List[gr.State]  # 6 state variables (0-3 for each line)
    calculate_btn: gr.Button
    compact_view_checkbox: gr.Checkbox


@dataclass
class HexagramInputComponents:
    """Container for all hexagram input components"""
    name_search: NameSearchHexagramInputs
    clickable: ClickableHexagramInputs
    coin_toss: CoinTossHexagramInputs
    hexagram_tabs: gr.Tabs


def create_name_search_tab() -> Tuple[NameSearchHexagramInputs, Callable]:
    """
    Create the hexagram name search input tab with all handlers
    
    Returns:
        Tuple of (NameSearchHexagramInputs, setup_handlers function)
    """
    gr.Markdown("### 選擇卦象", elem_classes=["section-header"])
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-top: -6px; margin-bottom: 12px;'>點擊兩次選擇外卦和內卦（例如：點擊兩次「天」為「乾為天」）</p>",
        elem_classes=["text-muted"]
    )
    
    # 8 trigram element buttons
    ELEMENT_NAMES = ["天", "地", "水", "火", "風", "雷", "山", "澤"]
    
    with gr.Row():
        with gr.Column(scale=1):            
            # Create 8 buttons in a grid (2 rows × 4 columns)
            element_buttons = []
            with gr.Column():
                for i in range(0, 8, 4):
                    with gr.Row():
                        for j in range(4):
                            if i + j < 8:
                                element = ELEMENT_NAMES[i + j]
                                btn = gr.Button(
                                    element,
                                    size="lg",
                                    elem_classes=["ganzhi-button"]
                                )
                                element_buttons.append((element, btn))
        
        with gr.Column(scale=1, elem_classes=["column-spacing"]):
            hexagram_dropdown = gr.Dropdown(
                label="選擇卦象",
                choices=[],
                value=None,
                interactive=True
            )
    
    # State variables for tracking selections
    outer_element_state = gr.State(value="")
    inner_element_state = gr.State(value="")
    
    # Store selected hexagram code
    selected_hexagram_code_state = gr.State(value=DEFAULT_HEXAGRAM_CODE)
        
    # Create a container for hexagram lines with checkboxes and changed hexagram
    with gr.Row(elem_classes=["hexagram-display-row"]):
        # Left column: Original hexagram (本卦)
        with gr.Column(scale=3, elem_classes=["column-spacing"]):
            gr.Markdown("### 本卦", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px;'>原始卦象</p>",
                elem_classes=["text-muted"]
            )
            hexagram_line_containers = []
            initial_code = DEFAULT_HEXAGRAM_CODE
            # Create in reverse order for display (6 to 1)
            for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                line_num = i + 1
                initial_html = create_line_html(initial_code, line_num, False, clickable=False)
                line_html = gr.HTML(
                    value=initial_html,
                    elem_classes=["hexagram-line-container"]
                )
                hexagram_line_containers.append(line_html)
        
        # Middle column: Checkboxes for 動爻
        with gr.Column(scale=1, elem_classes=["column-spacing"]):
            gr.Markdown("### 動爻", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px; line-height: 1.6; overflow: visible; white-space: normal; word-wrap: break-word;'>選擇變化的爻</p>",
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
        
        # Right column: Changed hexagram (變卦)
        with gr.Column(scale=3, elem_classes=["column-spacing"]):
            gr.Markdown("### 變卦", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px;'>變化後的卦象</p>",
                elem_classes=["text-muted"]
            )
            changed_hexagram_line_containers = []
            initial_code = DEFAULT_HEXAGRAM_CODE
            # Create in reverse order for display (6 to 1)
            for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                line_num = i + 1
                initial_html = create_line_html(initial_code, line_num, False, clickable=False)
                line_html = gr.HTML(
                    value=initial_html,
                    elem_classes=["hexagram-line-container"]
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
            code = DEFAULT_HEXAGRAM_CODE
        
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
            is_changing_line = line_num in changing
            original_html = create_line_html(code, line_num, is_changing_line, clickable=False)
            original_line_htmls.append(original_html)
            
            # Changed hexagram line
            changed_html = create_changed_line_html(changed_code, line_num)
            changed_line_htmls.append(changed_html)
        
        # Return both in visual order (6 to 1, top to bottom)
        return original_line_htmls, changed_line_htmls
    
    # Handler for element button clicks
    def handle_element_click(clicked_element, current_outer, current_inner, *changing_lines):
        """Handle click on an element button"""
        new_element = clicked_element
        
        if not current_outer:
            # First click - select outer element
            selection_text = f"{new_element}[待選內卦]"
            return (
                new_element,  # outer_element_state
                "",  # inner_element_state
                gr.Dropdown(choices=[selection_text], value=selection_text),  # dropdown - show selection text in choices
                "",  # selected_hexagram_code_state
                *[gr.update(value=False)] * 6,  # checkbox updates
                *[gr.update()] * 6,  # original line updates
                *[gr.update()] * 6   # changed line updates
            )
        
        # Second click - select inner element
        inner_element = new_element
        selection_text = f"{current_outer}{inner_element}"
        
        # Search for hexagrams matching both trigrams
        matches = search_hexagram_by_trigrams(current_outer, inner_element)
        
        if matches:
            choices = [f"{code} - {name}" for code, name in matches]
            selected_code = matches[0][0]
            selected_value = choices[0]
            # Reset all changing checkboxes when new hexagram is selected
            checkbox_updates = [gr.update(value=False)] * 6
            # Update hexagram lines (both original and changed)
            original_updates, changed_updates = update_hexagram_lines(selected_code, *[False] * 6)
            
            # Reset for next selection
            return (
                "",  # outer_element_state (reset)
                "",  # inner_element_state (reset)
                gr.Dropdown(choices=choices, value=selected_value),  # dropdown
                selected_code,  # selected_hexagram_code_state
                *checkbox_updates,  # checkbox updates
                *original_updates,  # original line updates
                *changed_updates    # changed line updates
            )
        else:
            # No matches found
            return (
                "",  # outer_element_state (reset)
                "",  # inner_element_state (reset)
                gr.Dropdown(choices=[], value=None),  # dropdown
                "",  # selected_hexagram_code_state
                *[gr.update(value=False)] * 6,  # checkbox updates
                *[gr.update()] * 6,  # original line updates
                *[gr.update()] * 6   # changed line updates
            )
    
    # Update dropdown when name changes (kept for backward compatibility if needed)
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
    
    # When hexagram is selected from dropdown, update lines and state
    def on_dropdown_select(dropdown_value, *changing_lines):
        code = get_hexagram_code_from_dropdown(dropdown_value)
        if not code or len(code) != 6:
            code = DEFAULT_HEXAGRAM_CODE
        
        original_updates, changed_updates = update_hexagram_lines(code, *changing_lines)
        return [code] + original_updates + changed_updates
    
    # When changing lines checkboxes change, update hexagram lines
    def update_lines_with_changing(code, *changing_lines):
        if not code or len(code) != 6:
            code = DEFAULT_HEXAGRAM_CODE
        
        original_updates, changed_updates = update_hexagram_lines(code, *changing_lines)
        return original_updates + changed_updates
    
    # Setup handlers function
    def setup_handlers():
        # Wire up element buttons
        def make_element_handler(element):
            def handler(current_outer, current_inner, *changing_lines):
                return handle_element_click(element, current_outer, current_inner, *changing_lines)
            return handler
        
        for element, button in element_buttons:
            handler = make_element_handler(element)
            button.click(
                fn=handler,
                inputs=[outer_element_state, inner_element_state] + changing_checkboxes,
                outputs=[
                    outer_element_state,
                    inner_element_state,
                    hexagram_dropdown,
                    selected_hexagram_code_state
                ] + changing_checkboxes + hexagram_line_containers + changed_hexagram_line_containers,
                queue=False  # Immediate UI feedback
            )
        
        # Update lines when dropdown changes
        hexagram_dropdown.change(
            fn=on_dropdown_select,
            inputs=[hexagram_dropdown] + changing_checkboxes,
            outputs=[selected_hexagram_code_state] + hexagram_line_containers + changed_hexagram_line_containers,
            queue=False  # Immediate UI feedback
        )
        
        # Update lines when changing checkboxes change
        for checkbox in changing_checkboxes:
            checkbox.change(
                fn=update_lines_with_changing,
                inputs=[selected_hexagram_code_state] + changing_checkboxes,
                outputs=hexagram_line_containers + changed_hexagram_line_containers,
                queue=False  # Immediate UI feedback
            )
    
    # Calculate button with compact view checkbox
    gr.Markdown("---", elem_classes=["section-divider"])
    with gr.Row():
        calculate_btn = gr.Button("開始排盤", variant="primary", size="lg", scale=4)
        compact_view_checkbox = gr.Checkbox(
            label="簡潔模式",
            value=False,
            scale=1,
            min_width=80
        )
    
    name_search_inputs = NameSearchHexagramInputs(
        element_buttons=element_buttons,
        outer_element_state=outer_element_state,
        inner_element_state=inner_element_state,
        hexagram_dropdown=hexagram_dropdown,
        selected_hexagram_code_state=selected_hexagram_code_state,
        changing_checkboxes=changing_checkboxes,
        hexagram_line_containers=hexagram_line_containers,
        changed_hexagram_line_containers=changed_hexagram_line_containers,
        calculate_btn=calculate_btn,
        compact_view_checkbox=compact_view_checkbox
    )
    
    return name_search_inputs, setup_handlers


def create_clickable_tab() -> Tuple[ClickableHexagramInputs, Callable]:
    """
    Create the clickable hexagram input tab with all handlers
    
    Returns:
        Tuple of (ClickableHexagramInputs, setup_handlers function)
    """
    gr.Markdown("### 點擊爻線輸入卦象", elem_classes=["section-header"])
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-top: -6px; margin-bottom: 12px;'>點擊下方的爻線來切換陽爻（▅▅▅▅▅▅）和陰爻（▅▅  ▅▅）</p>",
        elem_classes=["text-muted"]
    )
    
    # Store hexagram code state
    clickable_hexagram_code_state = gr.State(value=DEFAULT_HEXAGRAM_CODE)
    
    # Store changing lines state (for checkboxes)
    clickable_changing_state_1 = gr.State(value=False)  # 1爻
    clickable_changing_state_2 = gr.State(value=False)  # 2爻
    clickable_changing_state_3 = gr.State(value=False)  # 3爻
    clickable_changing_state_4 = gr.State(value=False)  # 4爻
    clickable_changing_state_5 = gr.State(value=False)  # 5爻
    clickable_changing_state_6 = gr.State(value=False)  # 6爻
    clickable_changing_state_vars = [
        clickable_changing_state_1,
        clickable_changing_state_2,
        clickable_changing_state_3,
        clickable_changing_state_4,
        clickable_changing_state_5,
        clickable_changing_state_6
    ]
    
    # Function to update clickable hexagram displays
    def update_clickable_hexagram_display(code, *changing_lines):
        """Update all hexagram displays when code or changing lines change"""
        if not code or len(code) != 6:
            code = DEFAULT_HEXAGRAM_CODE
        
        # Map checkbox values to line numbers
        # changing_lines[0] = 6爻 (top), changing_lines[5] = 1爻 (bottom)
        changing = []
        for visual_index, is_changing in enumerate(changing_lines):
            line_num = 6 - visual_index
            if is_changing:
                changing.append(line_num)
        
        # Calculate changed hexagram code
        changed_code = calculate_changed_hexagram(code, changing)
        
        # Create HTML for original hexagram lines in visual order (6 to 1, top to bottom)
        original_line_htmls = []
        changed_line_htmls = []
        
        for visual_index in range(6):
            line_num = 6 - visual_index
            is_changing_line = line_num in changing
            original_html = create_line_html(code, line_num, is_changing_line, clickable=True)
            original_line_htmls.append(original_html)
            
            # Changed hexagram line
            changed_html = create_changed_line_html(changed_code, line_num)
            changed_html = changed_html.replace(f">{line_num}爻", f">  {line_num}爻")
            changed_line_htmls.append(changed_html)
        
        return code, original_line_htmls, changed_line_htmls
    
    # Create a container for hexagram lines with checkboxes and changed hexagram
    with gr.Row(elem_classes=["hexagram-display-row"]):
        # Left column: Original hexagram (本卦) with clickable lines
        with gr.Column(scale=3, elem_classes=["column-spacing"]):
            gr.Markdown("### 本卦", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px;'>點擊爻線切換陽陰</p>",
                elem_classes=["text-muted"]
            )
            clickable_line_buttons = []
            initial_code = DEFAULT_HEXAGRAM_CODE
            # Create in reverse order for display (6 to 1)
            for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                line_num = i + 1
                is_yang = initial_code[i] == '1'
                # Format: "SYMBOL line_num爻" - no kanji in button text, CSS will add kanji on mobile via ::before
                button_value = f"{UI_CONFIG.line_symbol_yang if is_yang else UI_CONFIG.line_symbol_yin} {line_num}爻"
                
                button_classes = ["yao-line-button"]
                if is_yang:
                    button_classes.append("yang-button")
                else:
                    button_classes.append("yin-button")
                
                elem_id = f"yao-btn-{line_num}"
                line_button = gr.Button(
                    value=button_value,
                    elem_classes=button_classes,
                    elem_id=elem_id
                )
                clickable_line_buttons.append((line_num, line_button))
        
        # Middle column: Checkboxes for 動爻
        with gr.Column(scale=1, elem_classes=["column-spacing"]):
            gr.Markdown("### 動爻", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px; line-height: 1.6; overflow: visible; white-space: normal; word-wrap: break-word;'>選擇變化的爻</p>",
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
        with gr.Column(scale=3, elem_classes=["column-spacing"]):
            gr.Markdown("### 變卦", elem_classes=["section-header"])
            gr.Markdown(
                "<p style='color: #868e96; font-size: 12px; margin-top: -6px; margin-bottom: 10px;'>變化後的卦象</p>",
                elem_classes=["text-muted"]
            )
            clickable_changed_hexagram_line_containers = []
            initial_code = DEFAULT_HEXAGRAM_CODE
            # Create in reverse order for display (6 to 1)
            for i in range(5, -1, -1):  # 5 to 0, so line 6 to line 1
                line_num = i + 1
                initial_html = create_line_html(initial_code, line_num, False, clickable=True)
                line_html = gr.HTML(
                    value=initial_html,
                    elem_classes=["hexagram-line-container"]
                )
                clickable_changed_hexagram_line_containers.append(line_html)
    
    # Function to handle line button clicks
    def handle_line_click(line_num, current_code, *changing_lines):
        """Handle click on a line button - optimized for speed"""
        if not current_code or len(current_code) != 6:
            current_code = DEFAULT_HEXAGRAM_CODE
        
        # Toggle the line
        code_list = list(current_code)
        index = line_num - 1
        code_list[index] = '1' if code_list[index] == '0' else '0'
        new_code = ''.join(code_list)
        
        # Map checkbox values to line numbers (only once)
        changing_line_nums = []
        for visual_index, is_changing in enumerate(changing_lines):
            line_num_actual = 6 - visual_index
            if is_changing:
                changing_line_nums.append(line_num_actual)
        
        # Calculate changed hexagram code (only once)
        changed_code = calculate_changed_hexagram(new_code, changing_line_nums)
        
        # Only update the clicked button, not all 6
        clicked_button_index = 6 - line_num  # Convert line_num (1-6) to visual index (0-5)
        is_yang = new_code[index] == '1'
        is_changing = line_num in changing_line_nums
        line_symbol = UI_CONFIG.line_symbol_yang if is_yang else UI_CONFIG.line_symbol_yin
        change_mark = UI_CONFIG.change_mark_yang if (is_changing and is_yang) else (UI_CONFIG.change_mark_yin if (is_changing and not is_yang) else "")
        button_text = f"{line_symbol}{line_num}爻 {change_mark}"
        
        button_classes = ["yao-line-button"]
        if is_yang:
            button_classes.append("yang-button")
        else:
            button_classes.append("yin-button")
        if is_changing:
            button_classes.append("changing")
        
        elem_id = f"yao-btn-{line_num}"
        clicked_button_update = gr.update(value=button_text, elem_classes=button_classes, elem_id=elem_id)
        
        # Create updates for all buttons (needed for proper state, but only clicked one changes)
        button_updates = []
        for visual_index in range(6):
            actual_line_num = 6 - visual_index
            if visual_index == clicked_button_index:
                button_updates.append(clicked_button_update)
            else:
                # Keep other buttons unchanged
                button_updates.append(gr.update())
        
        # Generate changed hexagram HTML (only for 變卦)
        changed_line_htmls = []
        for visual_index in range(6):
            actual_line_num = 6 - visual_index
            changed_html = create_changed_line_html(changed_code, actual_line_num)
            changed_html = changed_html.replace(f">{actual_line_num}爻", f">  {actual_line_num}爻")
            changed_line_htmls.append(changed_html)
        
        return [new_code] + button_updates + changed_line_htmls
    
    # Function to update displays when changing checkboxes change
    def update_clickable_with_changing(code, *changing_lines):
        """Update displays when changing lines checkboxes change"""
        if not code or len(code) != 6:
            code = DEFAULT_HEXAGRAM_CODE
        
        # Get changed hexagram updates
        _, changed_updates = update_clickable_hexagram_display(code, *changing_lines)[1:]
        
        # Map checkbox values to line numbers
        changing_line_nums = []
        for visual_index, is_changing in enumerate(changing_lines):
            line_num = 6 - visual_index
            if is_changing:
                changing_line_nums.append(line_num)
        
        # Update button styling based on changing lines
        button_updates = []
        for visual_index in range(6):
            actual_line_num = 6 - visual_index
            code_index = actual_line_num - 1
            is_yang = code[code_index] == '1'
            is_changing = actual_line_num in changing_line_nums
            line_symbol = UI_CONFIG.line_symbol_yang if is_yang else UI_CONFIG.line_symbol_yin
            change_mark = UI_CONFIG.change_mark_yang if (is_changing and is_yang) else (UI_CONFIG.change_mark_yin if (is_changing and not is_yang) else "")
            # Format: "SYMBOL line_num爻 change_mark" - no kanji in button text, CSS will add kanji on mobile via ::before
            button_text = f"{line_symbol}{actual_line_num}爻 {change_mark}"
            
            button_classes = ["yao-line-button"]
            if is_yang:
                button_classes.append("yang-button")
            else:
                button_classes.append("yin-button")
            if is_changing:
                button_classes.append("changing")
            
            elem_id = f"yao-btn-{actual_line_num}"
            button_updates.append(gr.update(value=button_text, elem_classes=button_classes, elem_id=elem_id))
        
        return button_updates + changed_updates
    
    # Setup handlers function
    def setup_handlers():
        # Wire up line button clicks
        def make_line_click_handler(ln):
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
                outputs=[clickable_hexagram_code_state] + [btn for _, btn in clickable_line_buttons] + clickable_changed_hexagram_line_containers,
                queue=False  # Make updates immediate, no queue delay
            )
        
        # Wire up each checkbox to update its corresponding state variable
        checkbox_to_state_map = [
            (clickable_changing_checkboxes[0], clickable_changing_state_1, 1),  # 1爻
            (clickable_changing_checkboxes[1], clickable_changing_state_2, 2),  # 2爻
            (clickable_changing_checkboxes[2], clickable_changing_state_3, 3),  # 3爻
            (clickable_changing_checkboxes[3], clickable_changing_state_4, 4),  # 4爻
            (clickable_changing_checkboxes[4], clickable_changing_state_5, 5),  # 5爻
            (clickable_changing_checkboxes[5], clickable_changing_state_6, 6),  # 6爻
        ]
        
        def create_simple_checkbox_handler(line_num):
            def handler(checkbox_val):
                return checkbox_val
            return handler
        
        for checkbox, state_var, line_num in checkbox_to_state_map:
            handler = create_simple_checkbox_handler(line_num)
            checkbox.change(
                fn=handler,
                inputs=[checkbox],
                outputs=[state_var],
                queue=False  # Immediate UI feedback
            )
        
        # Wire all checkboxes to update display
        def update_display_when_checkbox_changes(code, cb1, cb2, cb3, cb4, cb5, cb6):
            return update_clickable_with_changing(code, cb1, cb2, cb3, cb4, cb5, cb6)
        
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
                outputs=[btn for _, btn in clickable_line_buttons] + clickable_changed_hexagram_line_containers,
                queue=False  # Immediate UI feedback
            )
    
    # Calculate button with compact view checkbox
    gr.Markdown("---", elem_classes=["section-divider"])
    with gr.Row():
        calculate_btn = gr.Button("開始排盤", variant="primary", size="lg", scale=4)
        compact_view_checkbox = gr.Checkbox(
            label="簡潔模式",
            value=False,
            scale=1,
            min_width=80
        )
    
    clickable_inputs = ClickableHexagramInputs(
        clickable_hexagram_code_state=clickable_hexagram_code_state,
        clickable_changing_state_vars=clickable_changing_state_vars,
        clickable_line_buttons=clickable_line_buttons,
        clickable_changing_checkboxes=clickable_changing_checkboxes,
        clickable_changed_hexagram_line_containers=clickable_changed_hexagram_line_containers,
        calculate_btn=calculate_btn,
        compact_view_checkbox=compact_view_checkbox
    )
    
    return clickable_inputs, setup_handlers


def coin_states_to_hexagram_code(coin_states: List[List[bool]]) -> Tuple[str, List[int]]:
    """
    Convert coin states to hexagram code and changing lines
    
    Args:
        coin_states: List of 6 lines, each containing 3 boolean values (True=heads, False=tails)
        coin_states[0] = line 1 (bottom), coin_states[5] = line 6 (top)
    
    Returns:
        Tuple of (hexagram_code, changing_line_numbers)
        hexagram_code is a 6-character string of '0' and '1'
        changing_line_numbers is a list of line numbers (1-6) that are changing
    """
    hexagram_code = ""
    changing_lines = []
    
    for line_index, coins in enumerate(coin_states):
        line_num = line_index + 1  # 1-6
        heads_count = sum(coins)  # Count True values (heads)
        
        # Determine yin/yang based on coin count
        # 3 heads or 2 heads 1 tail → yang ("1")
        # 1 head 2 tails or 3 tails → yin ("0")
        if heads_count >= 2:
            hexagram_code += "1"  # yang
        else:
            hexagram_code += "0"  # yin
        
        # Determine if changing based on coin count
        # 3 heads or 3 tails → is_changing=True
        if heads_count == 3 or heads_count == 0:
            changing_lines.append(line_num)
    
    return hexagram_code, changing_lines


def create_coin_toss_tab() -> Tuple[CoinTossHexagramInputs, Callable]:
    """
    Create the coin toss input tab with all handlers
    
    Returns:
        Tuple of (CoinTossHexagramInputs, setup_handlers function)
    """
    gr.Markdown("### 新手擲幣", elem_classes=["section-header"])
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-top: -6px; margin-bottom: 12px;'>選擇每爻的擲幣結果：正正正、正正反、正反反、或反反反。數字為正面，圖案為反面。</p>",
        elem_classes=["text-muted"]
    )
    
    # Store hexagram code state
    coin_toss_hexagram_code_state = gr.State(value=DEFAULT_HEXAGRAM_CODE)
    
    # Store changing lines state (for checkboxes)
    coin_toss_changing_state_1 = gr.State(value=False)  # 1爻
    coin_toss_changing_state_2 = gr.State(value=False)  # 2爻
    coin_toss_changing_state_3 = gr.State(value=False)  # 3爻
    coin_toss_changing_state_4 = gr.State(value=False)  # 4爻
    coin_toss_changing_state_5 = gr.State(value=False)  # 5爻
    coin_toss_changing_state_6 = gr.State(value=False)  # 6爻
    coin_toss_changing_state_vars = [
        coin_toss_changing_state_1,
        coin_toss_changing_state_2,
        coin_toss_changing_state_3,
        coin_toss_changing_state_4,
        coin_toss_changing_state_5,
        coin_toss_changing_state_6
    ]
    
    # Store selected outcome for each line (0-3: 正正正, 正正反, 正反反, 反反反)
    # Visual order: line 1, 2, 3, 4, 5, 6 (top to bottom) - reversed for beginners
    selected_outcome_states = []
    for line_num in range(1, 7):  # Visual order: 1 to 6 (reversed)
        outcome_state = gr.State(value=0)  # Default to 正正正 (0)
        selected_outcome_states.append(outcome_state)
    
    # Create outcome buttons section
    # Display order: line 1 at top, line 6 at bottom (reversed for beginners)
    outcome_buttons = []  # List of lists: 6 lines × 4 outcome buttons (visual order: 1 to 6)
    outcome_labels = ["正正正", "正正反", "正反反", "反反反"]
    
    for line_num in range(1, 7):  # Display from 1 to 6 (top to bottom) - reversed for beginners
        with gr.Row(elem_classes=["coin-toss-line"]):
            with gr.Column(scale=0, elem_classes=["coin-line-label"]):
                gr.Markdown(f"**丟第{line_num}次的結果**")
            
            line_outcome_buttons = []
            
            # Create 4 outcome buttons for this line
            with gr.Row(scale=1, elem_classes=["coin-outcome-row"]):
                for outcome_idx in range(4):
                    # Set default selected state for first button (正正正)
                    button_classes = ["coin-outcome-button"]
                    if outcome_idx == 0:  # Default to 正正正
                        button_classes.extend(["coin-outcome-selected", "coin-yang"])
                    
                    outcome_btn = gr.Button(
                        outcome_labels[outcome_idx],
                        size="sm",
                        elem_classes=button_classes,
                        scale=1,
                        min_width=50
                    )
                    line_outcome_buttons.append(outcome_btn)
            
            outcome_buttons.append(line_outcome_buttons)
    
    # Function to convert outcome index to coin states
    def outcome_to_coin_states(outcome_idx):
        """Convert outcome index (0-3) to coin states (3 booleans)
        
        Args:
            outcome_idx: 0=正正正, 1=正正反, 2=正反反, 3=反反反
        
        Returns:
            List of 3 booleans (True=heads/正, False=tails/反)
        """
        if outcome_idx == 0:  # 正正正
            return [True, True, True]
        elif outcome_idx == 1:  # 正正反
            return [True, True, False]
        elif outcome_idx == 2:  # 正反反
            return [True, False, False]
        else:  # outcome_idx == 3: 反反反
            return [False, False, False]
    
    # Function to update hexagram code based on selected outcomes
    def update_coin_toss_display(*outcome_indices):
        """Update hexagram code when outcome selections change
        
        Args:
            *outcome_indices: 6 outcome indices (0-3) in visual order: line1, line2, ..., line6
        
        Returns:
            Updates for hexagram code and changing states
        """
        # Convert outcomes to coin states (in visual order: 1,2,3,4,5,6)
        coin_states_by_line = []
        for outcome_idx in outcome_indices:
            coin_states = outcome_to_coin_states(outcome_idx)
            coin_states_by_line.append(coin_states)
        
        # Convert to hexagram code (visual order is already 1,2,3,4,5,6, so no need to reverse)
        hexagram_code, changing_lines = coin_states_to_hexagram_code(coin_states_by_line)
        
        # Update changing state variables
        changing_state_updates = []
        for line_num in range(1, 7):
            is_changing = line_num in changing_lines
            changing_state_updates.append(is_changing)
        
        return (
            hexagram_code,  # hexagram code state
            *changing_state_updates  # 6 changing state variables
        )
    
    # Function to determine if outcome is yang or yin
    def outcome_is_yang(outcome_idx):
        """Determine if outcome represents yang (陽) or yin (陰)
        
        Args:
            outcome_idx: 0=正正正, 1=正正反, 2=正反反, 3=反反反
        
        Returns:
            True for yang (陽), False for yin (陰)
        """
        # 正正正 (3 heads) or 正正反 (2 heads 1 tail) → yang
        # 正反反 (1 head 2 tails) or 反反反 (3 tails) → yin
        return outcome_idx <= 1
    
    # Function to handle outcome button click
    def handle_outcome_click(visual_line_index, outcome_idx, *all_outcome_indices):
        """Handle click on an outcome button
        
        Args:
            visual_line_index: Visual line index (0=line1, 5=line6) - reversed order
            outcome_idx: Outcome index (0-3): 0=正正正, 1=正正反, 2=正反反, 3=反反反
            *all_outcome_indices: All 6 outcome indices (in visual order: line1, line2, ..., line6)
        
        Returns:
            Updates for the selected outcome state, hexagram code, changing states, and button highlights
        """
        # Convert to list for mutation
        outcome_list = list(all_outcome_indices)
        
        # Update the selected outcome for this line
        outcome_list[visual_line_index] = outcome_idx
        
        # Update hexagram code and changing states
        hexagram_code, *changing_states = update_coin_toss_display(*outcome_list)
        
        # Update button highlights - only compute updates for the clicked line's 4 buttons
        # Get the current outcome for this line to determine yang/yin
        current_outcome = outcome_list[visual_line_index]
        is_yang = outcome_is_yang(current_outcome)
        
        # Create updates for all 24 buttons
        # For the clicked line, compute actual button classes
        # For other lines, use gr.update() to keep current state (Gradio will skip these efficiently)
        button_updates = []
        for vis_idx in range(6):
            for out_idx in range(4):
                if vis_idx == visual_line_index:
                    # For the clicked line, update all 4 buttons with proper classes
                    if out_idx == current_outcome:
                        # Selected button: red for yang, green for yin
                        if is_yang:
                            button_classes = ["coin-outcome-button", "coin-outcome-selected", "coin-yang"]
                        else:
                            button_classes = ["coin-outcome-button", "coin-outcome-selected", "coin-yin"]
                    else:
                        button_classes = ["coin-outcome-button"]
                    button_updates.append(gr.update(elem_classes=button_classes))
                else:
                    # For other lines, use gr.update() to keep current state (no change)
                    button_updates.append(gr.update())
        
        # Return: new outcome state, hexagram code, 6 changing states, 24 button updates (6 lines × 4 buttons)
        return [outcome_idx] + [hexagram_code] + list(changing_states) + button_updates
    
    # Setup handlers function
    def setup_handlers():
        # Wire up outcome button clicks
        # Note: visual_line_index 0 = line 1, visual_line_index 5 = line 6 (reversed order)
        for visual_line_index in range(6):
            for outcome_idx in range(4):
                outcome_btn = outcome_buttons[visual_line_index][outcome_idx]
                outcome_state_var = selected_outcome_states[visual_line_index]
                
                def make_outcome_handler(vis_idx, out_idx):
                    def handler(*all_outcome_indices):
                        return handle_outcome_click(vis_idx, out_idx, *all_outcome_indices)
                    return handler
                
                handler = make_outcome_handler(visual_line_index, outcome_idx)
                outcome_btn.click(
                    fn=handler,
                    inputs=selected_outcome_states,
                    outputs=[
                        selected_outcome_states[visual_line_index],  # Updated outcome state
                        coin_toss_hexagram_code_state,
                        *coin_toss_changing_state_vars,
                        *[btn for line_btns in outcome_buttons for btn in line_btns]
                    ],
                    queue=False  # Immediate UI feedback
                )
    
    # Calculate button with compact view checkbox
    gr.Markdown("---", elem_classes=["section-divider"])
    with gr.Row():
        calculate_btn = gr.Button("開始排盤", variant="primary", size="lg", scale=4)
        compact_view_checkbox = gr.Checkbox(
            label="簡潔模式",
            value=False,
            scale=1,
            min_width=80
        )
    
    coin_toss_inputs = CoinTossHexagramInputs(
        coin_toss_hexagram_code_state=coin_toss_hexagram_code_state,
        coin_toss_changing_state_vars=coin_toss_changing_state_vars,
        outcome_buttons=outcome_buttons,
        selected_outcome_states=selected_outcome_states,
        calculate_btn=calculate_btn,
        compact_view_checkbox=compact_view_checkbox
    )
    
    return coin_toss_inputs, setup_handlers


def create_hexagram_inputs() -> HexagramInputComponents:
    """
    Create all hexagram input components (name search, clickable, and coin toss tabs)
    
    Returns:
        HexagramInputComponents containing all hexagram input components
    """
    with gr.Tabs() as hexagram_tabs:
        # Name Search Tab
        with gr.Tab("八卦組卦"):
            name_search, setup_name_handlers = create_name_search_tab()
            setup_name_handlers()
        
        # Clickable Tab
        with gr.Tab("逐爻起卦"):
            clickable, setup_clickable_handlers = create_clickable_tab()
            setup_clickable_handlers()
        
        # Coin Toss Tab
        with gr.Tab("新手擲幣"):
            coin_toss, setup_coin_toss_handlers = create_coin_toss_tab()
            setup_coin_toss_handlers()
    
    return HexagramInputComponents(
        name_search=name_search,
        clickable=clickable,
        coin_toss=coin_toss,
        hexagram_tabs=hexagram_tabs
    )

