"""
Formatting utilities for divination results

This module contains functions for formatting divination results into
human-readable strings. The main function format_divination_results_pc()
is shared between the test script and the Gradio UI to ensure identical
output formatting.
"""

import sys
import io
from typing import List, Dict, Any, Tuple

from liu_yao import format_liu_yao_display_pc, format_liu_yao_display_mobile, display_shen_sha_definitions
from ba_zi_base import BaZi

# Grandmaster instructions template (shared between PC and mobile formats)
GRANDMASTER_INSTRUCTIONS = """

Role: 傳統六爻宗師 (Grandmaster of Traditional Liu Yao)

Profile: 你是一位深研《增刪卜易》與《卜筮正宗》的頂尖卦師。你的斷卦風格是「鐵口直斷、理法為體、象法為用」。你極度重視五行生剋的嚴格運算，對於「真假空破」、「進退神」、「回頭生剋」有著外科手術般的精準判斷。

Mission: 對使用者提供的六爻卦象(金錢起卦)進行吉凶運算。先定吉凶（理法），再談細節（象法）。你必須嚴格遵守「重內輕外」的原則，若內部動變邏輯已定吉凶，外部日月只能影響應期或程度，不可翻案。

Core Logic Flow (核心斷卦演算法)

Phase 1: 局勢掃描 (Triangular Analysis)
在此階段，不只看用神，必須同時確立「世、應、用」三者的狀態：

確立用神 (Target)： 根據問題精準選取。若用神不現，檢查「伏神」及其與飛神的生剋關係（飛來生伏得長生，飛去剋伏反傷身）。

確立世爻 (Self)： 代表問卦人、自身條件、現狀。世爻若空破墓絕，如同廢人，難以受生。

確立應爻 (Other)： 代表對方、目的地、客觀環境。

假設是占朋友的掛，那可以將應爻作為朋友，也可以將兄弟爻作為朋友，這取決於解掛時的合理性
假設是占朋友女朋友的卦，那可以將應爻作為朋友的女朋友，也可以將妻財爻作為朋友的女朋友，這取決於解掛時的合理性

特殊格局掃描： 檢查是否為六沖、六合、反吟、伏吟。

Phase 2: 嚴格理法運算 (The Hierarchy of Power)
【黃金法則】：動變 > 靜態。內部變異 > 外部環境。 請依照 P0 → P1 → P2 → P3 順序進行權重評估。

P0: 毀滅性打擊 (Absolute Negation)

檢查是否有「絕路空亡」（動而化空化破、伏而受剋）。

檢查用神或世爻是否「隨鬼入墓」（入動墓、入變墓）。

若 P0 成立，通常直接論凶，除非有極強的解救機制（如沖開墓庫）。

P1: 自身變異 (Self-Mutation) —— 決定性權重 此層級權重最高，直接決定吉凶方向。

回頭剋： 動爻化出變爻剋本位。結論：大凶（根基被斷，日月難救）。

回頭生： 動爻化出變爻生本位。結論：大吉（能量源源不絕）。

化進神： 力量倍增（如寅化卯）。

化退神： 力量消散（如卯化寅），那是「有始無終」。

化絕/化墓： 視為衰敗。

重要例外 (變爻失效判定)： - 若變爻本身「月破」或「日沖且無氣（真破）」，則變爻暫時無法回頭生/剋本位。

吉凶判斷： 若是「回頭剋但變爻破」，為凶中有救；若是「回頭生但變爻破」，為吉事落空或需待時填實。

P2: 內部互動 (Internal Interaction)

動動相連： 檢查是否有「連動相生」（如忌神生原神，原神生用神）。這能將凶局轉化為吉局。

三合局： 檢查動爻與變爻是否構成三合局？三合局力量 > 一般動爻。

P3: 外部環境 (External Environment) 若 P1、P2 無明顯吉凶，此層級才作為最終裁決；若 P1 已定，此層級僅影響應期。

月建： 提綱，管長遠旺衰。

日辰： 主宰，管當下生殺。日沖旺相靜爻為「暗動」，日沖休囚靜爻為「日破」。

空亡論斷： - 「旺不為空，動不為空」：視為假空，出空即應吉凶。

「衰而無氣、被沖剋」：視為真空，到底成空。

Phase 3: 象法細節 (Imagery & Context)
六獸： 結合爻位與五行描述情境（如白虎在五爻道路主車禍，朱雀在世爻主口舌）。

卦名義理： 利用大象變化（如《泰》變《大畜》）描述劇情發展。

Output Format (請嚴格遵守此輸出區塊)

【第一部：核心定調 (The Verdict)】
所問之事： [填入問題]

關鍵三核狀態：

用神（[五行]）： [旺衰狀態]（例如：臨月建，動化回頭生）

世爻（[五行]）： [旺衰狀態]（例如：日破，休囚）

應爻（[五行]）： [旺衰狀態]

吉凶結論： [ 大吉 / 小吉 / 平 / 小凶 / 大凶 ]

【第二部：理法博弈 (The Logic)】
關鍵勝負手 (The Deciding Factor)：

(請在此處解釋 P1/P2 的運算結果。例如：雖然用神臨月建（P3吉），但動而化回頭剋（P1凶），根據重內輕外原則，判定為凶。)

原神/忌神/仇神分析：

(分析連動相生或相剋的鏈條)

日月權重校正：

(解釋空亡、月破是真破還是假破，是否影響最終結果)

【第三部：精細解讀 (Detailed Analysis)】
世應關係解讀：

(分析世應生剋，解讀雙方心態或對待關係)

現象與情境 (六獸/卦意)：

(結合六獸描述具體發生了什麼事)

應期預測：

(具體到月或日)

宗師點評 (Grandmaster's Insight)：

(綜合以上所有資訊，給出最後的結論)\n"""


def _format_result_header(
    bazi: BaZi,
    result_json: Dict[str, Any],
    show_shen_sha: bool = True
) -> List[str]:
    """Format the common header parts of divination results (date, hexagram, shen_sha).
    
    This is a helper function to avoid code duplication between PC and mobile formats.
    
    Args:
        bazi: BaZi object
        result_json: Result dictionary from six_yao_divination
        show_shen_sha: Whether to show shen sha markers
    
    Returns:
        List of output string parts for the header
    """
    output_parts = []

    output_parts.append("起卦人的問題是: \n\n")
    
    # Format date: 日期: 乙巳年 丁亥月 戊申日 甲子時 (旬空:寅卯)
    xun_kong_list = []
    if 'ba_zi' in result_json:
        ba_zi = result_json['ba_zi']
        if 'xun_kong_1' in ba_zi and ba_zi['xun_kong_1']:
            xun_kong_list.append(ba_zi['xun_kong_1'])
        if 'xun_kong_2' in ba_zi and ba_zi['xun_kong_2']:
            xun_kong_list.append(ba_zi['xun_kong_2'])
    
    date_str = f"日期: {bazi.year.to_string()}年 {bazi.month.to_string()}月 {bazi.day.to_string()}日 {bazi.hour.to_string()}時"
    if xun_kong_list:
        date_str += f" (旬空:{''.join(xun_kong_list)})"
    output_parts.append(date_str + "\n\n")
    
    # Format hexagram: 卦象: [艮宫] 火澤睽 (本卦) ➔ [兌宫] 雷澤歸妹 (變卦)
    ben_gua_name = result_json.get('ben_gua_name', 'N/A')
    # Extract palace and name from ben_gua_name (format: "艮宫: 火澤睽" or similar)
    ben_palace = ""
    ben_name = ben_gua_name
    if 'ben_gua_info' in result_json and 'palace' in result_json['ben_gua_info']:
        ben_palace = result_json['ben_gua_info']['palace']
        if 'name' in result_json['ben_gua_info']:
            ben_name = result_json['ben_gua_info']['name']
    elif ':' in ben_gua_name:
        parts = ben_gua_name.split(':', 1)
        ben_palace = parts[0].replace('宫', '')
        ben_name = parts[1].strip().split()[0] if parts[1].strip() else ben_gua_name
    
    hexagram_str = f"卦象: [{ben_palace}宫] {ben_name} (本卦)"
    
    if 'bian_gua_name' in result_json:
        bian_gua_name = result_json.get('bian_gua_name', 'N/A')
        # Extract palace and name from bian_gua_name
        bian_palace = ""
        bian_name = bian_gua_name
        if 'bian_gua_info' in result_json and 'palace' in result_json['bian_gua_info']:
            bian_palace = result_json['bian_gua_info']['palace']
            if 'name' in result_json['bian_gua_info']:
                bian_name = result_json['bian_gua_info']['name']
        elif ':' in bian_gua_name:
            parts = bian_gua_name.split(':', 1)
            bian_palace = parts[0].replace('宫', '')
            bian_name = parts[1].strip().split()[0] if parts[1].strip() else bian_gua_name
        
        hexagram_str += f" ➔ [{bian_palace}宫] {bian_name} (變卦)"
    
    output_parts.append(hexagram_str + "\n\n")
    
    # Display 三合局 if exists
    if 'san_he_ju' in result_json and result_json['san_he_ju']:
        san_he_ju = result_json['san_he_ju']
        # 支持单个字符串或多个三合局的列表
        if isinstance(san_he_ju, list):
            san_he_ju_str = "、".join(san_he_ju)
        else:
            san_he_ju_str = san_he_ju
        output_parts.append(f"三合局: {san_he_ju_str}\n\n")
    
    # Extract and display 羊刃 and 桃花 from shen_sa
    if 'shen_sa' in result_json and show_shen_sha:
        # Capture output from display_shen_sha_definitions
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            display_shen_sha_definitions(result_json['shen_sa'])
            shen_sha_output = buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        output_parts.append(shen_sha_output)
    
    output_parts.append("\n")
    
    return output_parts


def format_divination_results_pc(
    bazi: BaZi,
    result_json: Dict[str, Any],
    yao_list: List[Any],
    show_shen_sha: bool = True,
    for_gradio: bool = False
) -> Tuple[str, str]:
    """Format divination results as a string in PC-friendly format.
    
    This function formats results with a compact header and simpler table format
    optimized for PC display.
    
    Args:
        bazi: BaZi object
        result_json: Result dictionary from six_yao_divination
        yao_list: List of YaoDetails from six_yao_divination
        show_shen_sha: Whether to show shen sha markers
        for_gradio: Whether this is for Gradio interface (uses 5 chars for yang) vs terminal (6 chars)
    
    Returns:
        Tuple of (formatted_result_with_prompt, formatted_result_without_prompt)
    """
    # Use shared header formatting
    output_parts = _format_result_header(bazi, result_json, show_shen_sha)
    
    # Main table using PC format
    table_output = format_liu_yao_display_pc(yao_list, show_shen_sha=show_shen_sha, for_gradio=for_gradio) + "\n"
    output_parts.append(table_output)
    
    # Create version without prompt
    output_parts_without_prompt = output_parts.copy()
    result_without_prompt = "".join(output_parts_without_prompt)
    
    # Create version with prompt
    output_parts.append(GRANDMASTER_INSTRUCTIONS)
    result_with_prompt = "".join(output_parts)
    
    return result_with_prompt, result_without_prompt


def format_divination_results_mobile(
    bazi: BaZi,
    result_json: Dict[str, Any],
    yao_list: List[Any],
    show_shen_sha: bool = True,
    for_gradio: bool = False
) -> Tuple[str, str]:
    """Format divination results as a string in mobile-friendly format.
    
    This function formats results with a compact header and vertical table format
    optimized for mobile display.
    
    Args:
        bazi: BaZi object
        result_json: Result dictionary from six_yao_divination
        yao_list: List of YaoDetails from six_yao_divination
        show_shen_sha: Whether to show shen sha markers
        for_gradio: Whether this is for Gradio interface (uses 5 chars for yang) vs terminal (6 chars)
    
    Returns:
        Tuple of (formatted_result_with_prompt, formatted_result_without_prompt)
    """
    # Use shared header formatting
    output_parts = _format_result_header(bazi, result_json, show_shen_sha)
    
    # Main table using mobile format
    table_output = format_liu_yao_display_mobile(yao_list, show_shen_sha=show_shen_sha, for_gradio=for_gradio) + "\n"
    output_parts.append(table_output)
    
    # Create version without prompt
    output_parts_without_prompt = output_parts.copy()
    result_without_prompt = "".join(output_parts_without_prompt)
    
    # Create version with prompt
    output_parts.append(GRANDMASTER_INSTRUCTIONS)
    result_with_prompt = "".join(output_parts)
    
    return result_with_prompt, result_without_prompt