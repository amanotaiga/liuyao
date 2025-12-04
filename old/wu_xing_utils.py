"""
Python version of 五行工具模块 (Five Elements Utils Module)
Converted from C++23 module wu_xing_utils.cppm

Provides data mappings and relationship judgment functions for the Five Elements system.
"""

from enum import Enum
from typing import Dict, List


# ==================== 五行关系枚举 ====================

class ElementalRelation(Enum):
    """五行关系枚举"""
    Generates = "生"      # 生 (我生)
    GeneratedBy = "被生"  # 被生 (生我)
    Controls = "克"      # 克 (我克)
    ControlledBy = "被克"  # 被克 (克我)
    Same = "同"          # 同 (比和)
    Error = "錯誤"       # 錯誤


# ==================== 地支五行映射 ====================

# 地支五行映射表
branchFiveElements: Dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 五行索引映射 (用于旺衰和六亲计算)
# 金=0, 水=1, 木=2, 火=3, 土=4
# 生: (i+1)%5, 克: (i+2)%5
fiveElementIndex: Dict[str, int] = {
    "金": 0, "水": 1, "木": 2, "火": 3, "土": 4
}

# ==================== 地支藏干 ====================

# 地支藏干映射表
# 每个地支中藏的天干（本气、中气、余气）
hiddenStems: Dict[str, List[str]] = {
    "子": ["癸"],
    "丑": ["癸", "辛", "己"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# ==================== 辅助函数 ====================


def getElementalRelationship(branch1: str, branch2: str) -> ElementalRelation:
    """
    判断两个地支的五行关系
    
    Args:
        branch1: 第一个地支
        branch2: 第二个地支
    
    Returns:
        ElementalRelation: 五行关系
    """
    if branch1 not in branchFiveElements or branch2 not in branchFiveElements:
        return ElementalRelation.Error
    
    elem1 = branchFiveElements[branch1]
    elem2 = branchFiveElements[branch2]
    
    if elem1 not in fiveElementIndex or elem2 not in fiveElementIndex:
        return ElementalRelation.Error
    
    idx1 = fiveElementIndex[elem1]
    idx2 = fiveElementIndex[elem2]
    
    if idx1 == idx2:
        return ElementalRelation.Same  # 同我
    elif idx2 == (idx1 + 1) % 5:
        return ElementalRelation.Generates  # 我生
    elif idx2 == (idx1 + 2) % 5:
        return ElementalRelation.Controls  # 我克
    elif idx1 == (idx2 + 1) % 5:
        return ElementalRelation.GeneratedBy  # 生我
    elif idx1 == (idx2 + 2) % 5:
        return ElementalRelation.ControlledBy  # 克我
    
    return ElementalRelation.Error


def relationToString(rel: ElementalRelation) -> str:
    """
    将五行关系枚举转为中文字符串
    
    Args:
        rel: 五行关系枚举
    
    Returns:
        str: 中文描述
    """
    return rel.value


def getBranchElement(branch: str) -> str:
    """
    获取地支的五行属性
    
    Args:
        branch: 地支
    
    Returns:
        str: 五行属性（"金"、"木"、"水"、"火"、"土"），如果無效则返回 "未知"
    """
    if branch in branchFiveElements:
        return branchFiveElements[branch]
    return "未知"


# ==================== 旺衰状态计算 ====================


def getWangShuai(lineElement: str, monthBranch: str, lineBranch: str = None) -> str:
    """
    计算爻的旺衰状态
    
    根据月令判断爻的旺衰状态。月令是判断五行强弱的核心标准。
    
    旺衰五态：
    - 旺：当令者旺（五行值月令）
    - 相：生我者相（月令生爻）
    - 休：我生者休（爻生月令）
    - 囚：我克者囚（爻克月令）
    - 死：克我者死（月令克爻）
    
    特殊判断：
    - 臨月：月支和爻支地支相同但五行不同
    - 月扶：月支和爻支五行相同但地支不同
    
    特殊处理：
    - 四季月（辰、戌、丑、未）：土旺金相、火休木囚、水死
    
    Args:
        lineElement: 爻的五行属性（"金"、"木"、"水"、"火"、"土"）
        monthBranch: 月支
        lineBranch: 爻支（可选），如果提供则用于判断臨月和月扶
    
    Returns:
        旺衰状态（"臨月"、"月扶"、"旺"、"相"、"休"、"囚"、"死"、"未知"）
    
    Example:
        >>> getWangShuai("木", "寅", "寅")
        '臨月'  # 月支和爻支相同
        >>> getWangShuai("木", "寅", "卯")
        '月扶'  # 月支和爻支五行相同但地支不同
        >>> getWangShuai("木", "寅")
        '旺'  # 木临月建（仅五行比较）
        >>> getWangShuai("火", "寅")
        '相'  # 木生火
    """
    # 验证输入有效性
    if monthBranch not in branchFiveElements or lineElement not in fiveElementIndex:
        return "未知"
    
    monthElement = branchFiveElements[monthBranch]
    
    if monthElement not in fiveElementIndex:
        return "未知"
    
    # 如果提供了爻支，先判断臨月和月扶
    if lineBranch is not None and lineBranch in branchFiveElements:
        # 臨月：月支和爻支地支相同
        if monthBranch == lineBranch:
            return "臨月"
        
        # 月扶：月支和爻支五行相同但地支不同
        lineBranchElement = branchFiveElements[lineBranch]
        if lineBranchElement == monthElement:
            return "月扶"
    
    lineIdx = fiveElementIndex[lineElement]
    monthIdx = fiveElementIndex[monthElement]
    
    # 五行旺衰判断（基于五行生克循环）
    if lineIdx == monthIdx:
        return "月扶"  # 同我者旺 (临月建)
    elif lineIdx == (monthIdx + 4) % 5:
        return "休"  # 生我者相 (月令生爻)
    elif lineIdx == (monthIdx + 1) % 5:
        return "月生"  # 我生者休 (爻生月令)
    elif lineIdx == (monthIdx + 2) % 5:
        return "月克"  # 我克者囚 (爻克月令)
    elif lineIdx == (monthIdx + 3) % 5:
        return "囚"  # 克我者死 (月令克爻)
    
    return "未知"


def checkLinRiRiFu(lineBranch: str, dayBranch: str) -> tuple[bool, bool]:
    """
    判断爻是否臨日或日扶
    
    根据日支和爻支判断：
    - 臨日：日支和爻支地支相同
    - 日扶：日支和爻支五行相同但地支不同
    
    Args:
        lineBranch: 爻支
        dayBranch: 日支
    
    Returns:
        (是否臨日, 是否日扶)
    
    Example:
        >>> checkLinRiRiFu("寅", "寅")
        (True, False)  # 臨日
        >>> checkLinRiRiFu("卯", "寅")
        (False, True)  # 日扶（都是木）
        >>> checkLinRiRiFu("申", "寅")
        (False, False)  # 既不是臨日也不是日扶
    """
    if lineBranch is None or dayBranch is None:
        return (False, False)
    
    if lineBranch not in branchFiveElements or dayBranch not in branchFiveElements:
        return (False, False)
    
    # 臨日：日支和爻支地支相同
    if dayBranch == lineBranch:
        return (True, False)
    
    # 日扶：日支和爻支五行相同但地支不同
    lineBranchElement = branchFiveElements[lineBranch]
    dayBranchElement = branchFiveElements[dayBranch]
    if lineBranchElement == dayBranchElement:
        return (False, True)
    
    return (False, False)


def checkRiShengRiKe(lineElement: str, dayBranch: str) -> tuple[bool, bool]:
    """
    判断爻是否日生或日克
    
    根据日支和爻的五行判断：
    - 日生：日生爻（日支的五行生爻的五行）
    - 日克：日克爻（日支的五行克爻的五行）
    
    五行生克关系：
    - 生：金生水、水生木、木生火、火生土、土生金
    - 克：金克木、木克土、土克水、水克火、火克金
    
    Args:
        lineElement: 爻的五行属性（"金"、"木"、"水"、"火"、"土"）
        dayBranch: 日支
    
    Returns:
        (是否日生, 是否日克)
    
    Example:
        >>> checkRiShengRiKe("火", "寅")  # 寅属木，木生火，日生爻
        (True, False)  # 日生
        >>> checkRiShengRiKe("火", "申")  # 申属金，金不生火
        (False, False)
        >>> checkRiShengRiKe("木", "申")  # 申属金，金克木，日克爻
        (False, True)  # 日克
    """
    if lineElement is None or dayBranch is None:
        return (False, False)
    
    if lineElement not in fiveElementIndex or dayBranch not in branchFiveElements:
        return (False, False)
    
    dayElement = branchFiveElements[dayBranch]
    if dayElement not in fiveElementIndex:
        return (False, False)
    
    lineIdx = fiveElementIndex[lineElement]
    dayIdx = fiveElementIndex[dayElement]
    
    # 日生：日生爻（dayIdx生lineIdx）
    # 五行生克循环：生我者 (i+4)%5，我生者 (i+1)%5
    # 所以 dayIdx生lineIdx 意味着 lineIdx == (dayIdx + 1) % 5
    if lineIdx == (dayIdx + 1) % 5:
        return (True, False)
    
    # 日克：日克爻（dayIdx克lineIdx）
    # 五行生克循环：克我者 (i+3)%5，我克者 (i+2)%5
    # 所以 dayIdx克lineIdx 意味着 lineIdx == (dayIdx + 2) % 5
    if lineIdx == (dayIdx + 2) % 5:
        return (False, True)
    
    return (False, False)