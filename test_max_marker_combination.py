"""
测试脚本：找出本卦中最长的状态标记组合

根据代码逻辑，本卦中可能出现的标记有：
1. 世/應
2. ○/× (動爻标记)
3. 旺衰信息：臨月、月扶、旺、相、月生、月克、死、休、囚
   （注意：如果有月合或月破，则不显示"休"或"囚"）
4. 月破
5. 日沖
6. 月合
7. 日合

互斥关系：
- 跟月有关的只会有一种：臨月、月扶、月破、月合 互斥（只能出现一个）
- 日合、日冲 互斥（只能出现一个）
"""

from liu_yao import YaoDetails
from ba_zi_base import Pillar


def calculate_marker_length(yao: YaoDetails) -> tuple:
    """
    计算一个爻的标记长度和标记列表
    
    Returns:
        (总长度, 标记列表)
    """
    marker_parts = []
    
    # 1. 世應标记
    main_shi_ying = yao.shi_ying_mark if yao.shi_ying_mark != " " else ""
    if main_shi_ying:
        marker_parts.append(main_shi_ying)
    
    # 2. 動爻标记
    change_mark = ""
    if yao.is_changing:
        if yao.change_mark == "O":
            change_mark = "○"
        elif yao.change_mark == "X":
            change_mark = "×"
    if change_mark:
        marker_parts.append(change_mark)
    
    # 3. 旺衰信息（月合月破优先）
    if yao.wang_shuai and yao.wang_shuai.strip():
        # 如果有月破，则不显示"月生"、"月克"（优先月破）
        if yao.yue_peng:
            if yao.wang_shuai not in ["休", "囚", "月生", "月克"]:
                marker_parts.append(yao.wang_shuai)
        # 如果有月合，则不显示"休"、"囚"或"月生"（优先月合）
        elif yao.yue_he:
            if yao.wang_shuai not in ["休", "囚", "月生"]:
                marker_parts.append(yao.wang_shuai)
        else:
            marker_parts.append(yao.wang_shuai)
    
    # 4. 月破、日沖、月合、日合
    if yao.yue_peng:
        marker_parts.append("月破")
    if yao.ri_chong:
        marker_parts.append("日沖")
    if yao.yue_he:
        marker_parts.append("月合")
    if yao.ri_he:
        marker_parts.append("日合")
    
    # 计算总长度（包括标记本身和它们之间的空格）
    # 格式：" {marker1} {marker2}" 或 " {marker}" 或 ""
    if marker_parts:
        markers_str = " " + " ".join(marker_parts)
        total_length = len(markers_str)
    else:
        markers_str = ""
        total_length = 0
    
    return total_length, marker_parts, markers_str


def test_all_combinations():
    """测试所有可能的组合，找出最长的"""
    
    # 所有可能的旺衰状态
    wang_shuai_options = ["臨月", "月扶", "月生", "月克", "休", "囚"]
    
    # 所有可能的组合
    max_length = 0
    max_combination = None
    max_markers_str = ""
    max_markers = []
    
    print("=" * 80)
    print("测试所有可能的标记组合...")
    print("=" * 80)
    print("约束条件:")
    print("  1. 跟月有关的只会有一种：臨月、月扶、月破、月合 互斥（只能出现一个）")
    print("  2. 日合、日冲 互斥（只能出现一个）")
    print("  3. 如果有月破，则不显示'月生'、'月克'（优先月破）")
    print("  4. 如果有月合，则不显示'月生'（优先月合）")
    print("  5. 如果有月合或月破，则不显示'休'或'囚'")
    print("=" * 80)
    
    # 测试所有组合
    for shi_ying in ["", "世", "應"]:
        for is_changing in [False, True]:
            for wang_shuai in wang_shuai_options:
                # 跟月有关的互斥：臨月、月扶、月破、月合 只能出现一个
                # 如果旺衰是"臨月"或"月扶"，则不能有月破或月合
                if wang_shuai in ["臨月", "月扶"]:
                    yue_options = [(False, False)]  # 不能有月破或月合
                else:
                    # 月破和月合不能同时为True
                    yue_options = [(False, False), (True, False), (False, True)]
                
                for yue_peng, yue_he in yue_options:
                    # 日合、日冲 互斥
                    for ri_chong, ri_he in [(False, False), (True, False), (False, True)]:
                        # 创建测试爻
                        yao = YaoDetails(position=1)
                        yao.shi_ying_mark = shi_ying if shi_ying else " "
                        yao.is_changing = is_changing
                        if is_changing:
                            yao.change_mark = "O"  # 假设是阳动
                        yao.wang_shuai = wang_shuai
                        yao.yue_peng = yue_peng
                        yao.ri_chong = ri_chong
                        yao.yue_he = yue_he
                        yao.ri_he = ri_he
                        
                        # 计算长度
                        length, markers, markers_str = calculate_marker_length(yao)
                        
                        if length > max_length:
                            max_length = length
                            max_combination = {
                                "shi_ying": shi_ying,
                                "is_changing": is_changing,
                                "wang_shuai": wang_shuai,
                                "yue_peng": yue_peng,
                                "ri_chong": ri_chong,
                                "yue_he": yue_he,
                                "ri_he": ri_he,
                            }
                            max_markers_str = markers_str
                            max_markers = markers
    
    print(f"\n最长组合（长度: {max_length} 字符）:")
    print(f"标记字符串: {max_markers_str}")
    print(f"标记列表: {max_markers}")
    print(f"\n组合详情:")
    for key, value in max_combination.items():
        print(f"  {key}: {value}")
    
    # 测试一些特殊情况
    print("\n" + "=" * 80)
    print("测试特殊情况...")
    print("=" * 80)
    
    # 情况1: 有月合或月破时，休/囚不显示
    print("\n情况1: 有月合时，休/囚不显示")
    yao1 = YaoDetails(position=1)
    yao1.shi_ying_mark = "應"
    yao1.is_changing = True
    yao1.change_mark = "O"
    yao1.wang_shuai = "休"  # 應该不显示
    yao1.yue_he = True
    yao1.ri_chong = True
    length1, markers1, str1 = calculate_marker_length(yao1)
    print(f"  标记: {str1}")
    print(f"  长度: {length1}")
    
    # 情况1b: 有月破时，月生不显示（优先月破）
    print("\n情况1b: 有月破时，月生不显示（优先月破）")
    yao1b = YaoDetails(position=1)
    yao1b.shi_ying_mark = "應"
    yao1b.is_changing = True
    yao1b.change_mark = "O"
    yao1b.wang_shuai = "月生"  # 應该不显示（优先月破）
    yao1b.yue_peng = True  # 月破
    yao1b.ri_chong = True
    length1b, markers1b, str1b = calculate_marker_length(yao1b)
    print(f"  标记: {str1b}")
    print(f"  长度: {length1b}")
    print(f"  注意: 只显示'月破'，不显示'月生'")
    
    # 情况1c: 有月破时，月克不显示（优先月破）
    print("\n情况1c: 有月破时，月克不显示（优先月破）")
    yao1c = YaoDetails(position=1)
    yao1c.shi_ying_mark = "應"
    yao1c.is_changing = True
    yao1c.change_mark = "O"
    yao1c.wang_shuai = ""  # 應该不显示（优先月破）
    yao1c.yue_peng = True  # 月破
    yao1c.ri_chong = True
    length1c, markers1c, str1c = calculate_marker_length(yao1c)
    print(f"  标记: {str1c}")
    print(f"  长度: {length1c}")
    print(f"  注意: 只显示'月破'，不显示'月克'")
    
    # 情况2: 没有月合/月破时，休/囚可以显示
    print("\n情况2: 没有月合/月破时，休/囚可以显示")
    yao2 = YaoDetails(position=1)
    yao2.shi_ying_mark = "世"
    yao2.is_changing = True
    yao2.change_mark = "X"
    yao2.wang_shuai = "囚"  # 可以显示
    yao2.ri_chong = True
    yao2.ri_he = True
    length2, markers2, str2 = calculate_marker_length(yao2)
    print(f"  标记: {str2}")
    print(f"  长度: {length2}")
    
    # 情况3: 所有状态都有的最长情况（遵守互斥规则）
    print("\n情况3: 所有状态都有的最长情况（遵守互斥规则）")
    print("  选项A: 臨月 + 日冲（臨月是最长的旺衰标记）")
    print("  选项B: 月扶 + 日冲（月扶不能和月破/月合同时出现）")
    print("  选项C: 月破 + 其他旺衰 + 日冲")
    print("  选项D: 月合 + 其他旺衰 + 日合")
    
    # 选项A: 臨月 + 日冲（最长旺衰）
    yao3a = YaoDetails(position=1)
    yao3a.shi_ying_mark = "應"
    yao3a.is_changing = True
    yao3a.change_mark = "O"
    yao3a.wang_shuai = "臨月"  # 臨月（最长，2字符）
    yao3a.ri_chong = True  # 日冲
    yao3a.yue_peng = False  # 不能有月破（和臨月互斥）
    yao3a.yue_he = False  # 不能有月合（和臨月互斥）
    yao3a.ri_he = False
    length3a, markers3a, str3a = calculate_marker_length(yao3a)
    print(f"\n  选项A (應○臨月日冲): {str3a}")
    print(f"  长度: {length3a}")
    print(f"  标记列表: {markers3a}")
    
    # 选项B: 月扶 + 日冲（月扶不能和月破/月合同时出现）
    yao3b = YaoDetails(position=1)
    yao3b.shi_ying_mark = "應"
    yao3b.is_changing = True
    yao3b.change_mark = "O"
    yao3b.wang_shuai = "月扶"  # 月扶（2字符，不能和月破/月合同时出现）
    yao3b.ri_chong = True  # 日冲
    yao3b.yue_peng = False
    yao3b.yue_he = False
    yao3b.ri_he = False
    length3b, markers3b, str3b = calculate_marker_length(yao3b)
    print(f"\n  选项B (應○月扶日冲): {str3b}")
    print(f"  长度: {length3b}")
    print(f"  标记列表: {markers3b}")
    
    # 选项C: 月破 + 其他旺衰 + 日冲（月破不能和臨月/月扶/月生/月克同时出现）
    yao3c = YaoDetails(position=1)
    yao3c.shi_ying_mark = "應"
    yao3c.is_changing = True
    yao3c.change_mark = "O"
    yao3c.wang_shuai = "月破"  # 不能是臨月、月扶、月生或月克（因为和月破互斥或优先月破）
    yao3c.yue_peng = True  # 月破
    yao3c.ri_chong = True  # 日冲
    yao3c.yue_he = False
    yao3c.ri_he = False
    length3c, markers3c, str3c = calculate_marker_length(yao3c)
    print(f"\n  选项C (應○月破日冲): {str3c}")
    print(f"  长度: {length3c}")
    print(f"  标记列表: {markers3c}")
    print(f"  注意: 如果有月破，则不显示'月生'、'月克'（优先月破）")
    
    # 选项D: 月合 + 其他旺衰 + 日合
    yao3d = YaoDetails(position=1)
    yao3d.shi_ying_mark = "應"
    yao3d.is_changing = True
    yao3d.change_mark = "O"
    yao3d.wang_shuai = "月生"  # 不能是臨月或月扶（因为和月合互斥）
    yao3d.yue_he = True  # 月合
    yao3d.ri_he = True  # 日合
    yao3d.yue_peng = False
    yao3d.ri_chong = False
    length3d, markers3d, str3d = calculate_marker_length(yao3d)
    print(f"\n  选项D (應○月生月合日合): {str3d}")
    print(f"  长度: {length3d}")
    print(f"  标记列表: {markers3d}")
    
    return max_length, max_combination, max_markers_str


if __name__ == "__main__":
    max_length, max_combination, max_markers_str = test_all_combinations()
    
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    print(f"最长标记组合长度: {max_length} 字符")
    print(f"最长标记字符串: {max_markers_str}")
    print(f"\n示例输出格式:")
    print(f"  本卦: 父母 ▇▇▇▇▇▇ 甲子水{max_markers_str}")

