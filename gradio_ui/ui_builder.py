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
        
        # Usage instructions accordion
        with gr.Accordion("📖 使用說明", open=False, elem_classes=["usage-instructions"]):
            gr.Markdown("""
### 什麼是易經六爻？

易經六爻是中國傳統的占卜方法，通過六條爻線（陽爻或陰爻）組成一個卦象，來預測和分析事物的發展趨勢。每條爻線可以分為：
- **陽爻**：用實線（—）表示
- **陰爻**：用虛線（--）表示

六爻從下往上排列，形成本卦，如果出現變爻（動爻），則會產生變卦，用於更深入的分析。

---

### 如何使用這個網站？

1. **選擇日期時間**：在「西曆日期」或「干支曆」標籤中選擇起卦當下的日期和時間
2. **選擇起卦方式**：
   - **新手擲幣**：適合初學者，使用三枚硬幣擲六次
   - **八卦組卦**：適合中級使用者，直接選擇卦名
   - **逐爻起卦**：適合高級使用者，逐條選擇每爻的陰陽
3. **標記變爻**：如果某爻為動爻，勾選對應的爻
4. **開始解盤**：點擊「開始解盤」按鈕，系統會自動生成詳細的排盤結果
5. **複製結果**：點擊「📋 複製」按鈕，將結果複製到剪貼板

---

### 新手擲幣方法（金錢起卦）

這是初學者最常用的起卦方法，使用三枚硬幣（或銅錢）進行：

**步驟：**
1. 準備三枚相同的硬幣（建議使用古銅錢，現代硬幣也可以）
2. 確定硬幣的正面和反面：
   - **正面（正）**：通常是有數字或文字的一面
   - **反面（反）**：通常是圖案或花紋的一面
3. 依次擲六次（每次擲三枚硬幣,擲完一次後記錄結果）：

**結果對應：**
- **正正正**（三個正面）
- **正正反**（兩正一反）
- **正反反**（一正兩反）
- **反反反**（三個反面）

**操作流程：**
1. 在「新手擲幣」標籤中，找到「丟第1次的結果」
2. 根據你擲出的結果，點擊對應的按鈕（正正正、正正反、正反反、或反反反）
3. 重複步驟1-2，完成六次擲幣
4. 系統會自動標記變爻
5. 確認日期時間無誤後，點擊「開始解盤」按鈕

---

### 中級與高級起卦方式

**八卦組卦**（適合中級使用者）：
- 直接在「八卦組卦」標籤中，選出外卦與內卦
- 系統會自動填入對應的六爻
- 手動勾選需要變動的爻線

**逐爻起卦**（適合中級使用者）：
- 在「逐爻起卦」標籤中，從下往上逐條點擊選擇每爻的陰陽
- 可以精確控制每一爻的狀態
- 手動勾選需要變動的爻線

---

### 簡潔模式

在排盤結果區域，有一個「簡潔模式」選項：
- **勾選簡潔模式**：結果會以更緊湊的格式顯示，適合手機等小螢幕閱讀

---

### 如何複製結果並貼到AI？

1. **完成排盤**：按照上述步驟完成起卦和解盤
2. **查看結果**：在「詳細排盤表」區域查看生成的排盤結果
3. **複製內容**：點擊「📋 複製」按鈕，系統會將結果複製到剪貼板
4. **貼到AI**：
   - 打開你常用的AI對話工具（如ChatGPT、Claude、Gemini等）
   - 貼上剛才複製的排盤結果（Ctrl+V 或 Cmd+V）
   - 在第一行輸入你的問題或想詢問的事情
   - 發送給AI，請它幫你解讀卦象

這樣AI就能根據完整的排盤資訊，為你提供詳細的卦象解讀和分析。
""")
        
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

