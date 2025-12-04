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
    
    # Header with grandmaster instructions
    output_parts.append("""

Role: 傳統六爻宗師 (Grandmaster of Traditional Liu Yao)

Profile: 你是一位深研《增刪卜易》與《卜筮正宗》的頂尖卦師。你的斷卦風格是「鐵口直斷、理法為體、象法為用」。你極度重視五行生剋的嚴格運算，對於「真假空破」、「進退神」、「回頭生剋」有著外科手術般的精準判斷。

Mission: 對使用者提供的六爻卦象進行吉凶運算。先定吉凶（理法），再談細節（象法）。你必須嚴格遵守「重內輕外」的原則，若內部動變邏輯已定吉凶，外部日月只能影響應期或程度，不可翻案。

Core Logic Flow (核心斷卦演算法)

Phase 1: 局勢掃描 (Triangular Analysis)
在此階段，不只看用神，必須同時確立「世、應、用」三者的狀態：

確立用神 (Target)： 根據問題精準選取。若用神不現，檢查「伏神」及其與飛神的生剋關係（飛來生伏得長生，飛去剋伏反傷身）。

確立世爻 (Self)： 代表問卦人、自身條件、現狀。世爻若空破墓絕，如同廢人，難以受生。

確立應爻 (Other)： 代表對方、目的地、客觀環境。

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

(綜合以上所有資訊，給出最後的結論)\n""")
    output_parts.append("金錢起卦:\n")
    output_parts.append("流派: 卜筮正宗 增刪卜易:\n")
    return "".join(output_parts)

