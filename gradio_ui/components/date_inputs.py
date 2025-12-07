"""
Date input components for the Gradio UI

This module contains reusable components for date input:
- Western calendar date selection
- Gan-Zhi (干支) calendar date selection with interactive pillar building
"""

from dataclasses import dataclass
from typing import Tuple, Callable
from datetime import datetime

import gradio as gr

from ..config import HEAVENLY_STEMS, EARTHLY_BRANCHES, MIN_YEAR, MAX_YEAR, PILLAR_LABELS


@dataclass
class WesternDateInputs:
    """Components for Western calendar date input"""
    year_dropdown: gr.Number
    month_dropdown: gr.Number
    day_dropdown: gr.Number
    hour_dropdown: gr.Number
    use_western_date: gr.State


@dataclass
class GanzhiDateInputs:
    """Components for Gan-Zhi calendar date input"""
    # Display components
    year_display: gr.Textbox
    month_display: gr.Textbox
    day_display: gr.Textbox
    hour_display: gr.Textbox
    
    # State components
    pillar_index_state: gr.State
    current_stem_state: gr.State
    current_branch_state: gr.State
    year_pillar_state: gr.State
    month_pillar_state: gr.State
    day_pillar_state: gr.State
    hour_pillar_state: gr.State


@dataclass
class DateInputComponents:
    """Container for all date input components"""
    western: WesternDateInputs
    ganzhi: GanzhiDateInputs
    date_tabs: gr.Tabs
    active_date_tab_state: gr.State  # Track which date tab is active: "western" or "ganzhi"


def create_western_calendar_tab(active_tab_state: gr.State) -> Tuple[WesternDateInputs, Callable]:
    """
    Create the Western calendar date input tab
    
    Args:
        active_tab_state: State variable to track which date tab is active
    
    Returns:
        Tuple of (WesternDateInputs, setup_handlers function)
    """
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-bottom: 12px;'>選擇起掛當下的日期時間進行排盤，分鐘位數不作使用，可以隨意填寫</p>",
        elem_classes=["text-muted"]
    )
    
    # Get current date/time
    now = datetime.now()
    
    # Format date and time for HTML5 inputs
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:00")
    
    # Mobile-friendly HTML5 date and time inputs (shown on mobile, hidden on desktop)
    mobile_date_time_html = gr.HTML(
        value=f"""
        <div class="mobile-date-time-wrapper">
            <div class="mobile-date-time-inputs">
                <div style="margin-bottom: 12px;">
                    <label for="mobile-date-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">日期</label>
                    <input type="date" id="mobile-date-input" value="{date_str}" 
                           style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                </div>
                <div>
                    <label for="mobile-time-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">時間</label>
                    <input type="time" id="mobile-time-input" value="{time_str}" 
                           style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                </div>
            </div>
        </div>
        """,
        elem_classes=["mobile-date-time-wrapper"]
    )
    
    # Desktop number inputs (shown on desktop, hidden on mobile)
    with gr.Row(elem_classes=["desktop-date-inputs"]):
        year_dropdown = gr.Number(
            value=now.year,
            label="年",
            step=1,
            precision=0,
            interactive=True,
            container=True
        )
        month_dropdown = gr.Number(
            value=now.month,
            label="月",
            minimum=1,
            maximum=12,
            step=1,
            precision=0,
            interactive=True,
            container=True
        )
        day_dropdown = gr.Number(
            value=now.day,
            label="日",
            minimum=1,
            maximum=31,
            step=1,
            precision=0,
            interactive=True,
            container=True
        )
        hour_dropdown = gr.Number(
            value=now.hour,
            label="時",
            minimum=0,
            maximum=23,
            step=1,
            precision=0,
            interactive=True,
            container=True
        )
    
    use_western_date = gr.State(value=True)
    
    # Setup handlers to track when Western date tab is used
    def setup_handlers():
        """Set up handlers to track active date tab and sync mobile/desktop inputs"""
        def mark_western_active(*args):
            """Mark Western date tab as active when any input changes"""
            return "western"
        
        def sync_from_numbers(year, month, day, hour):
            """Sync HTML5 inputs when number inputs change"""
            try:
                date_str = f"{int(year)}-{int(month):02d}-{int(day):02d}"
                time_str = f"{int(hour):02d}:00"
                return f"""
                <div class="mobile-date-time-wrapper">
                    <div class="mobile-date-time-inputs">
                        <div style="margin-bottom: 12px;">
                            <label for="mobile-date-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">日期</label>
                            <input type="date" id="mobile-date-input" value="{date_str}" 
                                   style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                        </div>
                        <div>
                            <label for="mobile-time-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">時間</label>
                            <input type="time" id="mobile-time-input" value="{time_str}" 
                                   style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                        </div>
                    </div>
                </div>
                """
            except Exception:
                # Return current date/time on error
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:00")
                return f"""
                <div class="mobile-date-time-wrapper">
                    <div class="mobile-date-time-inputs">
                        <div style="margin-bottom: 12px;">
                            <label for="mobile-date-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">日期</label>
                            <input type="date" id="mobile-date-input" value="{date_str}" 
                                   style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                        </div>
                        <div>
                            <label for="mobile-time-input" style="display: block; margin-bottom: 6px; font-weight: 500; color: var(--body-text-color, #333);">時間</label>
                            <input type="time" id="mobile-time-input" value="{time_str}" 
                                   style="width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid var(--border-color, #ddd); border-radius: 8px; box-sizing: border-box; background: var(--input-background, #fff); color: var(--input-text-color, #333);" />
                        </div>
                    </div>
                </div>
                """
        
        # Track when any Western date input changes
        for input_component in [year_dropdown, month_dropdown, day_dropdown, hour_dropdown]:
            input_component.change(
                fn=mark_western_active,
                inputs=[input_component],
                outputs=[active_tab_state]
            )
        
        # Sync HTML5 inputs when number inputs change
        year_dropdown.change(
            fn=sync_from_numbers,
            inputs=[year_dropdown, month_dropdown, day_dropdown, hour_dropdown],
            outputs=[mobile_date_time_html]
        )
        month_dropdown.change(
            fn=sync_from_numbers,
            inputs=[year_dropdown, month_dropdown, day_dropdown, hour_dropdown],
            outputs=[mobile_date_time_html]
        )
        day_dropdown.change(
            fn=sync_from_numbers,
            inputs=[year_dropdown, month_dropdown, day_dropdown, hour_dropdown],
            outputs=[mobile_date_time_html]
        )
        hour_dropdown.change(
            fn=sync_from_numbers,
            inputs=[year_dropdown, month_dropdown, day_dropdown, hour_dropdown],
            outputs=[mobile_date_time_html]
        )
    
    western_inputs = WesternDateInputs(
        year_dropdown=year_dropdown,
        month_dropdown=month_dropdown,
        day_dropdown=day_dropdown,
        hour_dropdown=hour_dropdown,
        use_western_date=use_western_date
    )
    
    return western_inputs, setup_handlers


def create_ganzhi_calendar_tab(active_tab_state: gr.State) -> Tuple[GanzhiDateInputs, Callable]:
    """
    Create the Gan-Zhi calendar date input tab with all handlers
    
    Args:
        active_tab_state: State variable to track which date tab is active
    
    Returns:
        Tuple of (GanzhiDateInputs, setup_handlers function)
        The setup_handlers function should be called to wire up event handlers
    """
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-bottom: 12px;'>依次選擇天干和地支組成四柱（年柱、月柱、日柱、時柱）</p>",
        elem_classes=["text-muted"]
    )
    
    with gr.Row():
        # Left panel: 天干 and 地支
        with gr.Column(scale=1, elem_classes=["column-spacing"]):
            # 天干 (Heavenly Stems) section
            gr.Markdown("### 天干", elem_classes=["section-header"])

            # Create 10 天干 buttons in a grid (2 rows × 5 columns)
            # Row 1: 甲, 丙, 戊, 庚, 壬 (even indices: 0, 2, 4, 6, 8)
            # Row 2: 乙, 丁, 己, 辛, 癸 (odd indices: 1, 3, 5, 7, 9)
            stem_buttons = []
            with gr.Column():
                # First row: even indices
                with gr.Row(elem_classes=["tiangan-button-row"]):
                    for idx in [0, 2, 4, 6, 8]:
                        stem = HEAVENLY_STEMS[idx]
                        btn = gr.Button(
                            stem,
                            size="lg",
                            elem_classes=["ganzhi-button"]
                        )
                        stem_buttons.append((idx, btn))
                # Second row: odd indices
                with gr.Row(elem_classes=["tiangan-button-row"]):
                    for idx in [1, 3, 5, 7, 9]:
                        stem = HEAVENLY_STEMS[idx]
                        btn = gr.Button(
                            stem,
                            size="lg",
                            elem_classes=["ganzhi-button"]
                        )
                        stem_buttons.append((idx, btn))
            
            gr.Markdown("---", elem_classes=["section-divider"])
            
            # 地支 (Earthly Branches) section
            gr.Markdown("### 地支", elem_classes=["section-header"])
            
            # Create 12 地支 buttons in a grid (2 rows × 6 columns)
            # Row 1: 子, 寅, 辰, 午, 申, 戌 (even indices: 0, 2, 4, 6, 8, 10)
            # Row 2: 丑, 卯, 巳, 未, 酉, 亥 (odd indices: 1, 3, 5, 7, 9, 11)
            branch_buttons = []
            with gr.Column():
                # First row: even indices
                with gr.Row(elem_classes=["dizhi-button-row"]):
                    for idx in [0, 2, 4, 6, 8, 10]:
                        branch = EARTHLY_BRANCHES[idx]
                        btn = gr.Button(
                            branch,
                            size="lg",
                            elem_classes=["ganzhi-button"]
                        )
                        branch_buttons.append((idx, btn))
                # Second row: odd indices
                with gr.Row(elem_classes=["dizhi-button-row"]):
                    for idx in [1, 3, 5, 7, 9, 11]:
                        branch = EARTHLY_BRANCHES[idx]
                        btn = gr.Button(
                            branch,
                            size="lg",
                            elem_classes=["ganzhi-button"]
                        )
                        branch_buttons.append((idx, btn))
        
        # Right panel: Display selected pillars
        with gr.Column(scale=1, elem_classes=["column-spacing"]):
                        
            gr.Markdown("### 已選擇的四柱", elem_classes=["section-header"])
            
            # Display pillars horizontally in a single row
            with gr.Row():
                year_display = gr.Textbox(
                    label="年柱",
                    value="",
                    interactive=True,
                    scale=1,
                    container=True
                )
                month_display = gr.Textbox(
                    label="月柱",
                    value="",
                    interactive=True,
                    scale=1,
                    container=True
                )
                day_display = gr.Textbox(
                    label="日柱",
                    value="",
                    interactive=True,
                    scale=1,
                    container=True
                )
                hour_display = gr.Textbox(
                    label="時柱",
                    value="",
                    interactive=True,
                    scale=1,
                    container=True
                )
            
            reset_btn = gr.Button("重置", variant="secondary")
    
    # State to track current pillar and selections
    pillar_index_state = gr.State(value=0)  # 0=year, 1=month, 2=day, 3=hour
    current_stem_state = gr.State(value="")
    current_branch_state = gr.State(value="")
    year_pillar_state = gr.State(value="")
    month_pillar_state = gr.State(value="")
    day_pillar_state = gr.State(value="")
    hour_pillar_state = gr.State(value="")
    
    # Handler functions
    def handle_stem_click(clicked_stem, current_index, current_stem, current_branch, year, month, day, hour, active_tab):
        """Handle click on a 天干 button"""
        new_stem = clicked_stem
        if current_branch:
            selection_text = f"{new_stem}{current_branch}"
        else:
            selection_text = f"{new_stem}[待選地支]"
        
        # Update the current pillar display with selection text
        display_updates = [year, month, day, hour]
        display_updates[current_index] = selection_text
        
        return (
            new_stem,  # current_stem_state
            current_branch,  # current_branch_state
            year, month, day, hour,  # pillar states (unchanged)
            *display_updates,  # display updates - show selection in current pillar
            "ganzhi"  # active_tab_state - mark ganzhi as active
        )
    
    def handle_branch_click(clicked_branch, current_index, current_stem, current_branch, year, month, day, hour, active_tab):
        """Handle click on a 地支 button"""
        new_branch = clicked_branch
        
        if not current_stem:
            # No stem selected yet
            selection_text = f"[待選天干]{new_branch}"
            # Update the current pillar display with selection text
            display_updates = [year, month, day, hour]
            display_updates[current_index] = selection_text
            return (
                "",  # current_stem_state
                new_branch,  # current_branch_state
                year, month, day, hour,  # pillar states
                *display_updates,  # display updates - show selection in current pillar
                "ganzhi"  # active_tab_state - mark ganzhi as active
            )
        
        # Both stem and branch selected, set the current pillar
        ganzhi = f"{current_stem}{new_branch}"
        next_index = (current_index + 1) % 4
        
        # Set the current pillar
        if current_index == 0:
            year = ganzhi
        elif current_index == 1:
            month = ganzhi
        elif current_index == 2:
            day = ganzhi
        elif current_index == 3:
            hour = ganzhi
        
        # Reset current stem/branch for next pillar
        return (
            "",  # current_stem_state (reset)
            "",  # current_branch_state (reset)
            next_index,  # pillar_index_state
            year, month, day, hour,  # pillar states
            year, month, day, hour,  # displays
            "ganzhi"  # active_tab_state - mark ganzhi as active
        )
    
    def reset_pillars():
        """Reset all pillars"""
        return (
            0,  # pillar_index_state
            "", # current_stem_state
            "", # current_branch_state
            "", "", "", "",  # pillar states
            "", "", "", "",  # displays
            "western"  # active_tab_state - reset to western when resetting ganzhi
        )
    
    # Create handler setup functions
    def setup_handlers():
        """Set up all event handlers for Gan-Zhi inputs"""
        # Wire up 天干 buttons
        def make_stem_handler(stem):
            def handler(current_index, current_stem, current_branch, year, month, day, hour, active_tab):
                return handle_stem_click(stem, current_index, current_stem, current_branch, year, month, day, hour, active_tab)
            return handler
        
        for idx, btn in stem_buttons:
            stem = HEAVENLY_STEMS[idx]
            handler = make_stem_handler(stem)
            btn.click(
                fn=handler,
                inputs=[pillar_index_state, current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, active_tab_state],
                outputs=[current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, year_display, month_display, day_display, hour_display, active_tab_state]
            )
        
        # Wire up 地支 buttons
        def make_branch_handler(branch):
            def handler(current_index, current_stem, current_branch, year, month, day, hour, active_tab):
                result = handle_branch_click(branch, current_index, current_stem, current_branch, year, month, day, hour, active_tab)
                return result
            return handler
        
        for idx, btn in branch_buttons:
            branch = EARTHLY_BRANCHES[idx]
            handler = make_branch_handler(branch)
            btn.click(
                fn=handler,
                inputs=[pillar_index_state, current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, active_tab_state],
                outputs=[current_stem_state, current_branch_state, pillar_index_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, year_display, month_display, day_display, hour_display, active_tab_state]
            )
        
        # Wire up reset button
        reset_btn.click(
            fn=reset_pillars,
            outputs=[pillar_index_state, current_stem_state, current_branch_state, year_pillar_state, month_pillar_state, day_pillar_state, hour_pillar_state, year_display, month_display, day_display, hour_display, active_tab_state]
        )
        
        # Wire up display textboxes to sync with state variables when user types directly
        def handle_year_display_change(value, active_tab):
            """Handle manual edit of year display textbox"""
            # Update state and mark ganzhi tab as active
            return value, "ganzhi"
        
        def handle_month_display_change(value, active_tab):
            """Handle manual edit of month display textbox"""
            return value, "ganzhi"
        
        def handle_day_display_change(value, active_tab):
            """Handle manual edit of day display textbox"""
            return value, "ganzhi"
        
        def handle_hour_display_change(value, active_tab):
            """Handle manual edit of hour display textbox"""
            return value, "ganzhi"
        
        # Connect display textboxes to state variables
        year_display.change(
            fn=handle_year_display_change,
            inputs=[year_display, active_tab_state],
            outputs=[year_pillar_state, active_tab_state]
        )
        
        month_display.change(
            fn=handle_month_display_change,
            inputs=[month_display, active_tab_state],
            outputs=[month_pillar_state, active_tab_state]
        )
        
        day_display.change(
            fn=handle_day_display_change,
            inputs=[day_display, active_tab_state],
            outputs=[day_pillar_state, active_tab_state]
        )
        
        hour_display.change(
            fn=handle_hour_display_change,
            inputs=[hour_display, active_tab_state],
            outputs=[hour_pillar_state, active_tab_state]
        )
    
    ganzhi_inputs = GanzhiDateInputs(
        year_display=year_display,
        month_display=month_display,
        day_display=day_display,
        hour_display=hour_display,
        pillar_index_state=pillar_index_state,
        current_stem_state=current_stem_state,
        current_branch_state=current_branch_state,
        year_pillar_state=year_pillar_state,
        month_pillar_state=month_pillar_state,
        day_pillar_state=day_pillar_state,
        hour_pillar_state=hour_pillar_state
    )
    
    return ganzhi_inputs, setup_handlers


def create_date_inputs() -> DateInputComponents:
    """
    Create all date input components (Western and Gan-Zhi tabs)
    
    Returns:
        DateInputComponents containing all date input components
    """
    # Create shared state for tracking active date tab
    active_date_tab_state = gr.State(value="western")  # Default to Western
    
    with gr.Tabs() as date_tabs:
        # Western Calendar Tab
        with gr.Tab("西曆日期"):
            western, setup_western_handlers = create_western_calendar_tab(active_date_tab_state)
            setup_western_handlers()
        
        # Gan-Zhi Calendar Tab
        with gr.Tab("干支曆"):
            ganzhi, setup_ganzhi_handlers = create_ganzhi_calendar_tab(active_date_tab_state)
            # Set up handlers after components are created
            setup_ganzhi_handlers()
    
    return DateInputComponents(
        western=western,
        ganzhi=ganzhi,
        date_tabs=date_tabs,
        active_date_tab_state=active_date_tab_state
    )

