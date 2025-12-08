"""
Python version of 六爻排盘系统 (Liu Yao Divination System)
Converted from C++23 module

Usage Examples:
-----------
    # Method 1: Using date string (recommended)
    from liu_yao import six_yao_divination_from_date
    yao_list, result = six_yao_divination_from_date(
        "111111",  # 本卦代码
        "2025/12/01 19:00",  # 日期時間字符串
        [1]  # 動爻位置
    )
    
    # Method 2: Using BaZi object directly
    from liu_yao import six_yao_divination, bazi_from_date_string
    from ba_zi_base import BaZi
    
    # Create BaZi from date string
    bazi = bazi_from_date_string("2025/12/01 19:00")
    
    # Or create BaZi manually
    from ba_zi_base import Pillar
    bazi = BaZi(
        Pillar("乙", "巳"),  # 年柱
        Pillar("丁", "亥"),  # 月柱
        Pillar("甲", "子"),  # 日柱
        Pillar("甲", "戌")   # 时柱
    )
    
    # Perform divination
    yao_list, result = six_yao_divination("111111", bazi, [1])

Dependencies:
-----------
This module requires the following Python modules to be implemented or imported:

1. bazi_base module:
   - Pillar class: Represents a 干支 (Gan-Zhi) pillar with methods:
     * stem() -> str: Returns the 天干 (heavenly stem)
     * branch() -> str: Returns the 地支 (earthly branch)
     * to_string() -> str: Returns string representation
   - BaZi class: Represents 八字 (Four Pillars) with attributes:
     * year: Pillar object
     * month: Pillar object
     * day: Pillar object
     * hour: Pillar object

2. ganzhi module:
   - Mapper class with static methods:
     * from_zh_zhi(zh: str) -> Optional[DiZhi]: Convert Chinese character to DiZhi enum
     * to_zh(dz: DiZhi) -> str: Convert DiZhi enum to Chinese character
   - DiZhi: Enum or class representing the 12 earthly branches
   - is_he(zhi1, zhi2) -> bool: Check if two branches are in 合 (he) relationship

3. wuxing_utils module:
   - fiveElementIndex: Dict[str, int] - Maps five elements (五行) to indices
   - branchFiveElements: Dict[str, str] - Maps earthly branches to their five elements
   - getWangShuai(element: str, month_branch: str) -> str: Calculate 旺衰 (strength/weakness)

If these modules are not available, placeholder classes are provided that you should replace
with actual implementations.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import json
import sys
from collections import defaultdict
from functools import lru_cache

if TYPE_CHECKING:
    from PIL import Image

# Note: These imports assume you have equivalent Python modules
# You'll need to implement or import:
# - Pillar and BaZi classes from a bazi_base module
# - GanZhi utilities (Mapper, DiZhi, is_he) from a ganzhi module  
# - WuXingUtils (fiveElementIndex, branchFiveElements, getWangShuai) from a wuxing_utils module

# For now, we'll define placeholder types - you should replace these with actual imports
try:
    from ba_zi_base import Pillar, BaZi
except ImportError:
    # Placeholder - replace with actual implementation
    class Pillar:
        def __init__(self, stem: str, branch: str):
            self._stem = stem
            self._branch = branch
        
        def stem(self) -> str:
            return self._stem
        
        def branch(self) -> str:
            return self._branch
        
        def to_string(self) -> str:
            return f"{self._stem}{self._branch}"
    
    class BaZi:
        def __init__(self, year, month, day, hour):
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour

try:
    from ganzhi import Mapper, DiZhi, is_he
except ImportError:
    # Placeholder - replace with actual implementation
    class Mapper:
        @staticmethod
        def from_zh_zhi(zh: str):
            # Return Optional[DiZhi]
            pass
        
        @staticmethod
        def to_zh(dz) -> str:
            return ""
    
    class DiZhi:
        pass
    
    def is_he(zhi1, zhi2) -> bool:
        return False

try:
    from wu_xing_utils import fiveElementIndex, branchFiveElements, getWangShuai, getElementalRelationship, ElementalRelation, checkLinRiRiFu, checkRiShengRiKe
except ImportError:
    # Placeholder - replace with actual implementation
    fiveElementIndex = {}
    branchFiveElements = {}
    def getWangShuai(element: str, month_branch: str) -> str:
        return ""
    def getElementalRelationship(branch1: str, branch2: str):
        return None
    class ElementalRelation:
        Generates = "生"
        GeneratedBy = "被生"
        Controls = "克"
        ControlledBy = "被克"
        Same = "同"
        Error = "錯誤"


def get_he_type(month_or_day_branch: str, yao_branch: str, is_month: bool = True) -> Optional[str]:
    """
    判断合的类型（生合、克合、平合）
    
    月合规则：
    - 生合（月->爻）：午火->未土、辰土->酉金、亥水->寅木
    - 克合：巳火->申金、卯木->戌土、丑土->子水
    - 平合：
      * 标准平合：未土->午火、酉金->辰土、寅木->亥水、申金->巳火、戌土->卯木、子水->丑土
      * 月氣1：辰月->寅爻、辰月->卯爻
      * 月氣2：未月->巳爻、未月->午爻
    
    日合规则（只有生合和克合，没有平合）：
    - 生合（日->爻）：午火->未土、辰土->酉金、亥水->寅木
    - 克合：巳火->申金、卯木->戌土、丑土->子水
    
    Args:
        month_or_day_branch: 月支或日支
        yao_branch: 爻支
        is_month: 是否为月合（True为月合，False为日合）
    
    Returns:
        "生合"、"克合"、"平合" 或 None（如果不相合）
    """
    if month_or_day_branch not in branchFiveElements or yao_branch not in branchFiveElements:
        return None
    
    # 定义生合关系（月/日->爻）
    sheng_he_pairs = [
        ("午", "未"),  # 午火->未土
        ("辰", "酉"),  # 辰土->酉金
        ("亥", "寅")   # 亥水->寅木
    ]
    
    # 定义克合关系（月/日->爻）
    ke_he_pairs = [
        ("巳", "申"),  # 巳火->申金
        ("卯", "戌"),  # 卯木->戌土
        ("丑", "子")   # 丑土->子水
    ]
    
    # 定义平合关系（月/日->爻，仅用于月合）
    ping_he_pairs = [
        ("未", "午"),  # 未土->午火
        ("酉", "辰"),  # 酉金->辰土
        ("寅", "亥"),  # 寅木->亥水
        ("申", "巳"),  # 申金->巳火
        ("戌", "卯"),  # 戌土->卯木
        ("子", "丑")   # 子水->丑土
    ]
    
    # 檢查生合
    for branch1, branch2 in sheng_he_pairs:
        if month_or_day_branch == branch1 and yao_branch == branch2:
            return "生合"
    
    # 檢查克合
    for branch1, branch2 in ke_he_pairs:
        if month_or_day_branch == branch1 and yao_branch == branch2:
            return "克合"
    
    # 檢查平合（仅用于月合）
    if is_month:
        # 标准平合关系
        for branch1, branch2 in ping_he_pairs:
            if month_or_day_branch == branch1 and yao_branch == branch2:
                return "平合"
        
        # 特殊情况1：当month是辰的时候，爻的寅卯也是平合
        if month_or_day_branch == "辰" and yao_branch in ["寅", "卯"]:
            return "平合"
        
        # 特殊情况2：当month是未的时候，巳午也是平合
        if month_or_day_branch == "未" and yao_branch in ["巳", "午"]:
            return "平合"
    
    return None


def check_san_he_ju(liu_yao: List['YaoDetails'], bazi: BaZi) -> Optional[str]:
    """
    判断三合局
    
    三合局有四种：
    - 巳酉丑（中神：酉）
    - 申子辰（中神：子）
    - 亥卯未（中神：卯）
    - 寅午戌（中神：午）
    
    条件：
    1. 必须是動爻(changing=True)，或是暗動(an_dong=True)，或是动之变爻(changed_pillar不为None且is_changing=True)，或是日、月
    2. 静爻不参加
    3. 中神必须为動爻，如果是动之变爻的话，必须跟動爻一起参加
    
    Args:
        liu_yao: 六爻详细信息列表
        bazi: 八字對象
    
    Returns:
        三合局字符串（如"巳酉丑三合局"），如果没有则返回 None
    """
    # 定义三合局组合及其中神
    san_he_ju_groups = [
        (["巳", "酉", "丑"], "酉"),  # 巳酉丑，中神酉
        (["申", "子", "辰"], "子"),  # 申子辰，中神子
        (["亥", "卯", "未"], "卯"),  # 亥卯未，中神卯
        (["寅", "午", "戌"], "午")   # 寅午戌，中神午
    ]
    
    day_branch = bazi.day.branch()
    month_branch = bazi.month.branch()
    
    # 对每个三合局组合进行檢查
    for branches, zhong_shen in san_he_ju_groups:
        # 记录每个地支的来源信息
        # 格式: {地支: {"source": "本卦爻"/"变爻"/"日"/"月", "is_changing": bool, "yao_index": int}}
        branch_sources = {}
        
        # 檢查本卦爻
        for i, yao in enumerate(liu_yao):
            if yao.main_pillar is not None:
                main_branch = yao.main_pillar.branch()
                if main_branch in branches:
                    # 必须是動爻或暗動
                    if yao.is_changing or yao.an_dong:
                        if main_branch not in branch_sources:
                            branch_sources[main_branch] = {
                                "source": "本卦爻",
                                "is_changing": yao.is_changing,
                                "yao_index": i
                            }
        
        # 檢查变爻
        for i, yao in enumerate(liu_yao):
            if yao.changed_pillar is not None and yao.is_changing:
                changed_branch = yao.changed_pillar.branch()
                if changed_branch in branches:
                    # 变爻必须对應的本爻是動爻
                    if changed_branch not in branch_sources:
                        branch_sources[changed_branch] = {
                            "source": "变爻",
                            "is_changing": True,
                            "yao_index": i
                        }
        
        # 檢查日
        if day_branch in branches:
            branch_sources[day_branch] = {
                "source": "日",
                "is_changing": True,  # 日视为动
                "yao_index": -1
            }
        
        # 檢查月
        if month_branch in branches:
            branch_sources[month_branch] = {
                "source": "月",
                "is_changing": True,  # 月视为动
                "yao_index": -1
            }
        
        # 檢查三个地支是否都存在
        if len(branch_sources) == 3:
            # 檢查中神是否存在
            zhong_shen_source = branch_sources.get(zhong_shen)
            if zhong_shen_source is None:
                continue
            
            # 中神必须为動爻（is_changing=True）
            # 注意：暗動(an_dong)不算動爻，所以中神不能只是暗動
            if not zhong_shen_source["is_changing"]:
                continue
            
            # 如果中神是变爻，檢查对應的本爻是否也是動爻
            if zhong_shen_source["source"] == "变爻":
                yao_index = zhong_shen_source["yao_index"]
                if yao_index >= 0 and yao_index < len(liu_yao):
                    yao = liu_yao[yao_index]
                    if not yao.is_changing:
                        continue
            
            # 如果中神是本卦爻，确保它是動爻（不是暗動）
            if zhong_shen_source["source"] == "本卦爻":
                yao_index = zhong_shen_source["yao_index"]
                if yao_index >= 0 and yao_index < len(liu_yao):
                    yao = liu_yao[yao_index]
                    # 中神必须是動爻，不能只是暗動
                    if not yao.is_changing:
                        continue
            
            # 所有条件满足，返回三合局名称
            return f"{branches[0]}{branches[1]}{branches[2]}三合局"
    
    return None


@dataclass
class YaoDetails:
    """存储每一爻的详细信息"""
    position: int  # 1-6
    
    # 本卦信息
    main_pillar: Optional[Pillar] = None
    main_element: str = ""
    main_relative: str = ""
    
    # 伏神信息
    hidden_pillar: Optional[Pillar] = None
    hidden_relative: str = ""
    hidden_element: str = ""
    
    # 变爻/變卦信息
    is_changing: bool = False
    changed_pillar: Optional[Pillar] = None
    changed_element: str = ""
    changed_relative: str = ""
    
    # 其他辅助信息
    spirit: str = ""
    wang_shuai: str = ""
    shi_ying_mark: str = " "
    main_yao_type: str = '0'  # '0' or '1'
    change_mark: str = " "  # 'X' 阴变, 'O' 阳变, " "
    
    # 神煞标记
    xun_kong: bool = False  # 旬空
    yue_peng: bool = False  # 月破
    ri_chong: bool = False  # 日沖
    yue_he: Optional[str] = None  # 月合类型（"生合"、"克合"、"平合"）
    ri_he: Optional[str] = None  # 日合类型（"生合"、"克合"）
    lin_ri: bool = False  # 臨日
    ri_fu: bool = False  # 日扶
    ri_sheng: bool = False  # 日生
    ri_ke: bool = False  # 日克
    an_dong: bool = False  # 暗動
    ri_peng: bool = False  # 日破
    shen_sha_markers: List[str] = field(default_factory=list)  # 其他神煞标记（如：禄、刃、桃花等）
    
    # 變卦神煞标记（用于動爻變卦的日月關係）
    changed_xun_kong: bool = False  # 變卦旬空
    changed_yue_peng: bool = False  # 變卦月破
    changed_ri_peng: bool = False  # 變卦日破
    changed_ri_chong: bool = False  # 變卦日沖
    changed_yue_he: Optional[str] = None  # 變卦月合类型（"生合"、"克合"、"平合"）
    changed_ri_he: Optional[str] = None  # 變卦日合类型（"生合"、"克合"）
    changed_lin_ri: bool = False  # 變卦臨日
    changed_ri_fu: bool = False  # 變卦日扶
    changed_ri_sheng: bool = False  # 變卦日生
    changed_ri_ke: bool = False  # 變卦日克
    changed_an_dong: bool = False  # 變卦暗動
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "position": self.position,
            "mainPillar": self.main_pillar.to_string() if self.main_pillar else "",
            "mainElement": self.main_element,
            "mainRelative": self.main_relative,
            "hiddenPillar": self.hidden_pillar.to_string() if self.hidden_pillar else "",
            "hiddenRelative": self.hidden_relative,
            "hiddenElement": self.hidden_element,
            "isChanging": self.is_changing,
            "changedPillar": self.changed_pillar.to_string() if self.changed_pillar else "",
            "changedElement": self.changed_element,
            "changedRelative": self.changed_relative,
            "spirit": self.spirit,
            "wangShuai": self.wang_shuai,
            "shiYingMark": self.shi_ying_mark,
            "mainYaoType": self.main_yao_type,
            "changeMark": self.change_mark,
            "xunKong": self.xun_kong,
            "yuePeng": self.yue_peng,
            "riPeng": self.ri_chong,
            "yueHe": self.yue_he if self.yue_he else False,
            "riHe": self.ri_he if self.ri_he else False,
            "linRi": self.lin_ri,
            "riFu": self.ri_fu,
            "riSheng": self.ri_sheng,
            "riKe": self.ri_ke,
            "anDong": self.an_dong,
            "riPeng": self.ri_peng,
            "shenShaMarkers": self.shen_sha_markers
        }


@dataclass
class HexagramInfo:
    """卦象信息"""
    name: str  # 卦名
    meaning: str  # 简要含义
    five_element: str  # 五行属性
    shi_yao_position: int  # 世爻位置 (1-6)
    ying_yao_position: int  # 應爻位置 (1-6)
    is_yang_hexagram: bool  # 阳卦/阴卦
    palace_type: str  # 所属宫位 (如 "乾", "坎"...)
    inner_hexagram: str  # 内卦
    outer_hexagram: str  # 外卦
    structure_type: str = ""  # 卦结构类型 (如 "本宫", "游魂", "归魂", "" for others)
    
    def get_detailed_name(self) -> str:
        """获取详细的卦名，包括宫位和结构类型
        
        Returns:
            格式化的卦名，如 "乾宫: 火天大有 归魂卦" 或 "乾宫: 乾为天 本宫卦"
        """
        parts = [f"{self.palace_type}宫:", self.name]
        if self.structure_type:
            parts.append(f"{self.structure_type}卦")
        return " ".join(parts)


# 卦象映射表
HEXAGRAM_MAP: Dict[str, HexagramInfo] = {
    # 乾宮（金）系列
    "111111": HexagramInfo("乾為天", "剛健中正", "金", 6, 3, True, "乾", "乾", "乾", "本宮(六沖)"),
    "011111": HexagramInfo("天風姤", "陰陽相遇", "金", 1, 4, True, "乾", "巽", "乾", ""),
    "001111": HexagramInfo("天山遁", "退避保全", "金", 2, 5, True, "乾", "艮", "乾", ""),
    "000111": HexagramInfo("天地否", "閉塞不通", "金", 3, 6, True, "乾", "坤", "乾", "六合"),
    "000011": HexagramInfo("風地觀", "觀察民情", "金", 4, 1, True, "乾", "坤", "巽", ""),
    "000001": HexagramInfo("山地剝", "陰盛陽衰", "金", 5, 2, True, "乾", "坤", "艮", ""),
    "000101": HexagramInfo("火地晉", "光明晉升", "金", 4, 1, True, "乾", "坤", "離", "游魂"),
    "111101": HexagramInfo("火天大有", "昌隆富有", "金", 3, 6, True, "乾", "乾", "離", "歸魂"),
    
    # 坎宮（水）系列
    "010010": HexagramInfo("坎為水", "險陷重重", "水", 6, 3, True, "坎", "坎", "坎", "本宮(六沖)"),
    "110010": HexagramInfo("水澤節", "節制有度", "水", 1, 4, True, "坎", "兌", "坎", "六合"),
    "100010": HexagramInfo("水雷屯", "初生艱難", "水", 2, 5, True, "坎", "震", "坎", ""),
    "101010": HexagramInfo("水火既濟", "事已完成", "水", 3, 6, True, "坎", "離", "坎", ""),
    "101110": HexagramInfo("澤火革", "變革創新", "水", 4, 1, True, "坎", "離", "兌", ""),
    "101100": HexagramInfo("雷火豐", "盛大光明", "水", 5, 2, True, "坎", "離", "震", ""),
    "101000": HexagramInfo("地火明夷", "光明受傷", "水", 4, 1, True, "坎", "離", "坤", "游魂"),
    "010000": HexagramInfo("地水師", "興師動眾", "水", 3, 6, True, "坎", "坤", "坎", "歸魂"),
    
    # 艮宮（土）系列
    "001001": HexagramInfo("艮為山", "靜止不動", "土", 6, 3, True, "艮", "艮", "艮", "本宮(六沖)"),
    "101001": HexagramInfo("山火賁", "文飾美化", "土", 1, 4, True, "艮", "離", "艮", "六合"),
    "111001": HexagramInfo("山天大畜", "積蓄力量", "土", 2, 5, True, "艮", "乾", "艮", ""),
    "110001": HexagramInfo("山澤損", "減損之道", "土", 3, 6, True, "艮", "兌", "艮", ""),
    "110101": HexagramInfo("火澤睽", "意見相左", "土", 4, 1, True, "艮", "兌", "離", ""),
    "110111": HexagramInfo("天澤履", "謹慎行事", "土", 5, 2, True, "艮", "兌", "乾", ""),
    "110011": HexagramInfo("風澤中孚", "誠信立身", "土", 4, 1, True, "艮", "兌", "巽", "游魂"),
    "001011": HexagramInfo("風山漸", "循序漸進", "土", 3, 6, True, "艮", "艮", "巽", "歸魂"),
    
    # 震宮（木）系列
    "100100": HexagramInfo("震為雷", "震動奮發", "木", 6, 3, True, "震", "震", "震", "本宮(六沖)"),
    "000100": HexagramInfo("雷地豫", "安樂警惕", "木", 1, 4, True, "震", "坤", "震", "六合"),
    "010100": HexagramInfo("雷水解", "解除困境", "木", 2, 5, True, "震", "坎", "震", ""),
    "011100": HexagramInfo("雷風恒", "恒久之道", "木", 3, 6, True, "震", "巽", "震", ""),
    "011000": HexagramInfo("地風升", "步步高升", "木", 4, 1, True, "震", "巽", "坤", ""),
    "011010": HexagramInfo("水風井", "滋養不窮", "木", 5, 2, True, "震", "巽", "坎", ""),
    "011110": HexagramInfo("澤風大過", "非常行動", "木", 4, 1, True, "震", "巽", "兌", "游魂"),
    "100110": HexagramInfo("澤雷隨", "隨從之道", "木", 3, 6, True, "震", "震", "兌", "歸魂"),
    
    # 巽宮（木）系列
    "011011": HexagramInfo("巽為風", "謙遜柔順", "木", 6, 3, False, "巽", "巽", "巽", "本宮(六沖)"),
    "111011": HexagramInfo("風天小畜", "積蓄力量", "木", 1, 4, False, "巽", "乾", "巽", ""),
    "101011": HexagramInfo("風火家人", "家庭倫理", "木", 2, 5, False, "巽", "離", "巽", ""),
    "100011": HexagramInfo("風雷益", "增益之道", "木", 3, 6, False, "巽", "震", "巽", ""),
    "100111": HexagramInfo("天雷無妄", "不可妄為", "木", 4, 1, False, "巽", "震", "乾", "六沖"),
    "100101": HexagramInfo("火雷噬嗑", "排除障礙", "木", 5, 2, False, "巽", "震", "離", ""),
    "100001": HexagramInfo("山雷頤", "頤養之道", "木", 4, 1, False, "巽", "震", "艮", "游魂"),
    "011001": HexagramInfo("山風蠱", "整治腐敗", "木", 3, 6, False, "巽", "巽", "艮", "歸魂"),
    
    # 離宮（火）系列
    "101101": HexagramInfo("離為火", "光明美麗", "火", 6, 3, False, "離", "離", "離", "本宮(六沖)"),
    "001101": HexagramInfo("火山旅", "行旅之道", "火", 1, 4, False, "離", "艮", "離", "六合"),
    "011101": HexagramInfo("火風鼎", "穩重圖新", "火", 2, 5, False, "離", "巽", "離", ""),
    "010101": HexagramInfo("火水未濟", "事未完成", "火", 3, 6, False, "離", "坎", "離", ""),
    "010001": HexagramInfo("山水蒙", "啟蒙教育", "火", 4, 1, False, "離", "坎", "艮", ""),
    "010011": HexagramInfo("風水渙", "渙散分離", "火", 5, 2, False, "離", "巽", "坎", ""),
    "010111": HexagramInfo("天水訟", "爭訟糾紛", "火", 4, 1, False, "離", "坎", "乾", "游魂"),
    "101111": HexagramInfo("天火同人", "同心協力", "火", 3, 6, False, "離", "乾", "離", "歸魂"),
    
    # 坤宮（土）系列
    "000000": HexagramInfo("坤為地", "厚德載物", "土", 6, 3, False, "坤", "坤", "坤", "本宮(六沖)"),
    "100000": HexagramInfo("地雷復", "陽氣復歸", "土", 1, 4, False, "坤", "震", "坤", "六合"),
    "110000": HexagramInfo("地澤臨", "督導視察", "土", 2, 5, False, "坤", "兌", "坤", ""),
    "111000": HexagramInfo("地天泰", "天地交泰", "土", 3, 6, False, "坤", "乾", "坤", "六合"),
    "111100": HexagramInfo("雷天大壯", "強盛壯大", "土", 4, 1, False, "坤", "乾", "震", "六沖"),
    "111110": HexagramInfo("澤天夬", "果斷決策", "土", 5, 2, False, "坤", "乾", "兌", ""),
    "111010": HexagramInfo("水天需", "耐心等待", "土", 4, 1, False, "坤", "乾", "坎", "游魂"),
    "000010": HexagramInfo("水地比", "親和依附", "土", 3, 6, False, "坤", "坤", "坎", "歸魂"),
    
    # 兌宮（金）系列
    "110110": HexagramInfo("兌為澤", "喜悅溝通", "金", 6, 3, False, "兌", "兌", "兌", "本宮(六沖)"),
    "010110": HexagramInfo("澤水困", "困境求生", "金", 1, 4, False, "兌", "坎", "兌", "六合"),
    "000110": HexagramInfo("澤地萃", "人才薈萃", "金", 2, 5, False, "兌", "坤", "兌", ""),
    "001110": HexagramInfo("澤山咸", "感應相知", "金", 3, 6, False, "兌", "艮", "兌", ""),
    "001010": HexagramInfo("水山蹇", "艱難險阻", "金", 4, 1, False, "兌", "艮", "坎", ""),
    "001000": HexagramInfo("地山謙", "謙虛美德", "金", 5, 2, False, "兌", "艮", "坤", ""),
    "001100": HexagramInfo("雷山小過", "小有過失", "金", 4, 1, False, "兌", "艮", "震", "游魂"),
    "110100": HexagramInfo("雷澤歸妹", "婚嫁之道", "金", 3, 6, False, "兌", "震", "兌", "歸魂"),
}

# 地支序列
PALACE_BRANCH_PATTERNS: Dict[str, List[str]] = {
    "乾": ["子", "寅", "辰", "午", "申", "戌"],  # 阳金
    "坎": ["寅", "辰", "午", "申", "戌", "子"],  # 阳水
    "艮": ["辰", "午", "申", "戌", "子", "寅"],  # 阳土
    "震": ["子", "寅", "辰", "午", "申", "戌"],  # 阳木
    "巽": ["丑", "亥", "酉", "未", "巳", "卯"],  # 阴木（逆序）
    "離": ["卯", "丑", "亥", "酉", "未", "巳"],  # 阴火（逆序）
    "坤": ["未", "巳", "卯", "丑", "亥", "酉"],  # 阴土
    "兌": ["巳", "卯", "丑", "亥", "酉", "未"],  # 阴金（逆序）
}

# 天干序列（默认冬至后）
PALACE_STEM_PATTERNS: Dict[str, List[str]] = {
    "乾": ["甲", "甲", "甲", "壬", "壬", "壬"],  # 冬至后内甲外壬
    "坎": ["戊", "戊", "戊", "戊", "戊", "戊"],  # 内外均戊
    "艮": ["丙", "丙", "丙", "丙", "丙", "丙"],  # 内外均丙
    "震": ["庚", "庚", "庚", "庚", "庚", "庚"],  # 内外均庚
    "巽": ["辛", "辛", "辛", "辛", "辛", "辛"],  # 内外均辛
    "離": ["己", "己", "己", "己", "己", "己"],  # 内外均己
    "坤": ["乙", "乙", "乙", "癸", "癸", "癸"],  # 冬至后内乙外癸
    "兌": ["丁", "丁", "丁", "丁", "丁", "丁"],  # 内外均丁
}

# 日干到六神起始索引
DAY_STEM_TO_SPIRIT_START: Dict[str, int] = {
    "甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2,
    "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5
}

# 六神排列表
SIX_SPIRITS: List[str] = ["青龍", "朱雀", "勾陳", "螣蛇", "白虎", "玄武"]

# 六亲
RELATIVE_NAMES: List[str] = ["兄弟", "子孫", "妻財", "官鬼", "父母"]


def get_relative(palace_element: str, yao_element: str) -> str:
    """计算六親關係"""
    if not palace_element or not yao_element:
        return "錯誤"
    
    if palace_element not in fiveElementIndex or yao_element not in fiveElementIndex:
        return "錯誤"
    
    if palace_element == yao_element:
        return RELATIVE_NAMES[0]  # 兄弟
    
    palace_idx = fiveElementIndex[palace_element]
    yao_idx = fiveElementIndex[yao_element]
    
    # palaceIdx: 我, yaoIdx: 爻
    # (yaoIdx - palaceIdx + 5) % 5: 0-同, 1-我生, 2-我克, 3-克我, 4-生我
    diff = (yao_idx - palace_idx + 5) % 5
    return RELATIVE_NAMES[diff]


# Pre-computed lookup tables for shen sha calculations (moved outside function for better performance)
_SHEN_SHA_LU_Shen_MAP = {
    "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
    "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"
}

_SHEN_SHA_YANG_REN_MAP = {
    "甲": "卯", "乙": "辰", "丙": "午", "丁": "未", "戊": "午",
    "己": "未", "庚": "酉", "辛": "戌", "壬": "子", "癸": "丑"
}

_SHEN_SHA_TAO_HUA_MAP = {
    "寅": "卯", "午": "卯", "戌": "卯",  # 寅午戌见卯
    "申": "酉", "子": "酉", "辰": "酉",  # 申子辰见酉
    "亥": "子", "卯": "子", "未": "子",  # 亥卯未见子
    "巳": "午", "酉": "午", "丑": "午"   # 巳酉丑见午
}

_SHEN_SHA_YI_MA_MAP = {
    "寅": "申", "午": "申", "戌": "申",  # 寅午戌见申
    "申": "寅", "子": "寅", "辰": "寅",  # 申子辰见寅
    "亥": "巳", "卯": "巳", "未": "巳",  # 亥卯未见巳
    "巳": "亥", "酉": "亥", "丑": "亥"   # 巳酉丑见亥
}

_SHEN_SHA_GUI_REN_MAP = {
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],  # 甲戊庚牛羊
    "乙": ["子", "申"], "己": ["子", "申"],  # 乙己鼠猴乡
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],  # 丙丁猪鸡位
    "壬": ["巳", "卯"], "癸": ["巳", "卯"],  # 壬癸兔蛇藏
    "辛": ["午", "寅"]  # 辛金马虎乡
}

# Pre-compute DiZhi chong (冲) lookup table: each branch's opposite (加6取模12)
_DIZHI_CHONG_MAP = {
    "子": "午", "丑": "未", "寅": "申", "卯": "酉", "辰": "戌", "巳": "亥",
    "午": "子", "未": "丑", "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳"
}

# Pre-compute DiZhi he (合) lookup table
_DIZHI_HE_MAP = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午"
}

# Cache for build_shen_sha_map results
_shen_sha_cache = {}

def build_shen_sha_map(bazi: BaZi) -> Dict[str, List[str]]:
    """直接根據四柱和六個主卦爻支構建神煞彙總圖"""
    
    # Create cache key from BaZi string representation
    cache_key = f"{bazi.year.to_string()}_{bazi.month.to_string()}_{bazi.day.to_string()}_{bazi.hour.to_string()}"
    if cache_key in _shen_sha_cache:
        # Return a deep copy to avoid mutation issues
        return {k: v[:] for k, v in _shen_sha_cache[cache_key].items()}
    
    shen_sha_definition_map: Dict[str, List[str]] = defaultdict(list)
    
    day_stem = bazi.day.stem()
    day_branch = bazi.day.branch()
    month_branch = bazi.month.branch()
    year_branch = bazi.year.branch()
    
    # 1. 基於年月日支本身
    # shen_sha_definition_map["太歲"].append(year_branch)
    shen_sha_definition_map["月建"].append(month_branch)
    shen_sha_definition_map["日辰"].append(day_branch)
    
    # 2. 基于冲合关系 - use pre-computed lookup tables
    # 计算月破（月支的冲支）
    if month_branch in _DIZHI_CHONG_MAP:
        shen_sha_definition_map["月破"].append(_DIZHI_CHONG_MAP[month_branch])
    # 计算月合
    if month_branch in _DIZHI_HE_MAP:
        shen_sha_definition_map["月合"].append(_DIZHI_HE_MAP[month_branch])
    
    # 计算日沖（日支的冲支）
    if day_branch in _DIZHI_CHONG_MAP:
        shen_sha_definition_map["日沖"].append(_DIZHI_CHONG_MAP[day_branch])
    # 计算日合
    if day_branch in _DIZHI_HE_MAP:
        shen_sha_definition_map["日合"].append(_DIZHI_HE_MAP[day_branch])
    
    # 3. 基于干支关系的神煞 - use pre-computed lookup tables
    # shen_sha_definition_map["日禄"].append(_SHEN_SHA_LU_Shen_MAP[day_stem])
    shen_sha_definition_map["羊刃"].append(_SHEN_SHA_YANG_REN_MAP[day_stem])
    shen_sha_definition_map["桃花"].append(_SHEN_SHA_TAO_HUA_MAP[day_branch])
    shen_sha_definition_map["驛馬"].append(_SHEN_SHA_YI_MA_MAP[day_branch])
    
    # 天乙贵人
    nobles = _SHEN_SHA_GUI_REN_MAP[day_stem]
    shen_sha_definition_map["貴人"].extend(nobles)
    
    # 排序贵人地支
    shen_sha_definition_map["貴人"].sort()
    
    # Convert to regular dict and cache
    result = dict(shen_sha_definition_map)
    _shen_sha_cache[cache_key] = {k: v[:] for k, v in result.items()}  # Cache deep copy
    
    return result


def display_shen_sha_definitions(shen_sa: Dict[str, List[str]]) -> None:
    """Display all shen sha definitions from the shen_sha_definition_map.
    
    This function prints all shen sha items (太歲, 月建, 日辰, 月破, 日沖, 
    月合, 日合, 羊刃, 桃花, 驛馬, 貴人, etc.) in a formatted way.
    
    Args:
        shen_sa: Dictionary containing shen sha definitions (from result_json['shen_sa'])
                 Key is the shen sha name (e.g., "驛馬"), value is a list of branches (e.g., ["巳"])

    Example:
        >>> shen_sa = {"驛馬": ["巳"], "桃花": ["子"], "貴人": ["未", "丑"]}
        >>> display_shen_sha_definitions(shen_sa)
        驛馬: 巳
        桃花: 子
        貴人: 未、丑
    """
    if not shen_sa:
        return
    
    # Common shen sha items to display (in order of importance/common usage)
    shen_sha_order = ["羊刃", "桃花", "驛馬", "貴人"]
    # Display items in specified order first
    for shen_sha_name in shen_sha_order:
        if shen_sha_name in shen_sa:
            value_list = shen_sa[shen_sha_name]
            if value_list:
                value_str = "、".join(value_list)
                print(f"{shen_sha_name}: {value_str}")


def format_yao_line(main_yao_type: str, change_mark: str) -> str:
    """格式化爻象线条 (用于表格输出)"""
    line = "▅▅▅▅▅" if main_yao_type == '1' else "▅▅ ▅▅"
    if change_mark == " ":
        return f"{line:^7}"
    else:
        return f"{line} {change_mark}"


def initialize_yao_details_vector(main_info: HexagramInfo, changing_line_indices: List[int]) -> List[YaoDetails]:
    """初始化包含6个YaoDetails的列表，并设置position"""
    yao_details_list = []
    for i in range(6):
        yao = YaoDetails(position=i + 1)
        
        # 檢查是否为動爻
        if (i + 1) in changing_line_indices:
            yao.is_changing = True
        
        # 设置世應標記
        if (i + 1) == main_info.shi_yao_position:
            yao.shi_ying_mark = "世"
        elif (i + 1) == main_info.ying_yao_position:
            yao.shi_ying_mark = "應"
        else:
            yao.shi_ying_mark = ""
        
        yao_details_list.append(yao)
    
    return yao_details_list


def generate_tian_gan_and_di_zhi(yao_details_list: List[YaoDetails], hexagram: HexagramInfo, type_yao: int):
    """生成六个爻的天干地支
    
    Args:
        yao_details_list: 六个爻位
        hexagram: 64卦的信息
        type_yao: 0 飞神 1 變卦 2伏神
    """
    inner_stems = PALACE_STEM_PATTERNS[hexagram.inner_hexagram]
    inner_branches = PALACE_BRANCH_PATTERNS[hexagram.inner_hexagram]
    outer_stems = PALACE_STEM_PATTERNS[hexagram.outer_hexagram]
    outer_branches = PALACE_BRANCH_PATTERNS[hexagram.outer_hexagram]
    
    # 内卦（0-2）  外卦（3-5）
    w = 3
    for i in range(6):
        if type_yao == 0:
            pillar = yao_details_list[i].main_pillar
        elif type_yao == 1:
            pillar = yao_details_list[i].changed_pillar
        elif type_yao == 2:
            pillar = yao_details_list[i].hidden_pillar
        else:
            print("generateTianGanAndDiZhi <UNK>")
            continue
        
        # 使用字符串构造函数创建 Pillar
        if i < 3:
            stem = inner_stems[i]
            branch = inner_branches[i]
        else:
            stem = outer_stems[w]
            branch = outer_branches[w]
            w += 1
        
        # 创建新的 Pillar 對象
        new_pillar = Pillar(stem, branch)
        if type_yao == 0:
            yao_details_list[i].main_pillar = new_pillar
        elif type_yao == 1:
            yao_details_list[i].changed_pillar = new_pillar
        elif type_yao == 2:
            yao_details_list[i].hidden_pillar = new_pillar


def calculate_hidden_gods(base_palace_info: HexagramInfo, main_palace_element: str, yao_list: List[YaoDetails]):
    """计算伏神信息，只添加缺失的六亲"""
    # 首先确定本卦中已有的六亲
    main_relatives = set()
    for yao in yao_list:
        if yao.main_relative and yao.main_relative not in ["錯誤", "未知", ""]:
            main_relatives.add(yao.main_relative)
    
    generate_tian_gan_and_di_zhi(yao_list, base_palace_info, 2)
    
    for i in range(6):
        if yao_list[i].hidden_pillar is None:
            yao_list[i].hidden_element = ""
            yao_list[i].hidden_relative = ""
            continue
        hidden_branch = yao_list[i].hidden_pillar.branch()
        if hidden_branch in branchFiveElements:
            yao_list[i].hidden_element = branchFiveElements[hidden_branch]
            # 关键：变爻六亲相对于【本卦】宫位五行
            calculated_relative = get_relative(main_palace_element, yao_list[i].hidden_element)
            # 只保留缺失的六亲，如果该六亲已在本卦中存在，则清空所有伏神信息（六亲、天干地支、五行）
            if calculated_relative not in ["錯誤", "未知", ""] and calculated_relative not in main_relatives:
                yao_list[i].hidden_relative = calculated_relative
            else:
                # 清空所有伏神信息：六亲、天干地支、五行
                yao_list[i].hidden_pillar = None
                yao_list[i].hidden_element = ""
                yao_list[i].hidden_relative = ""
        else:
            yao_list[i].hidden_element = ""
            yao_list[i].hidden_relative = ""
            print(f"警告: 無法找到变爻地支 '{hidden_branch}' 的五行属性。", file=sys.stderr)


def fill_element_and_relative(yao_list: List[YaoDetails], palace_element: str, is_main_hexagram: bool):
    """填充爻的五行和六亲信息"""
    for i in range(6):
        pillar = yao_list[i].main_pillar if is_main_hexagram else yao_list[i].changed_pillar
        if pillar is None:
            if is_main_hexagram:
                yao_list[i].main_element = "未知"
                yao_list[i].main_relative = "錯誤"
            else:
                yao_list[i].changed_element = "未知"
                yao_list[i].changed_relative = "錯誤"
            continue
        branch = pillar.branch()
        
        if branch in branchFiveElements:
            element = branchFiveElements[branch]
            relative = get_relative(palace_element, element)
            
            if is_main_hexagram:
                yao_list[i].main_element = element
                yao_list[i].main_relative = relative
            else:
                yao_list[i].changed_element = element
                yao_list[i].changed_relative = relative
        else:
            if is_main_hexagram:
                yao_list[i].main_element = "未知"
                yao_list[i].main_relative = "錯誤"
            else:
                yao_list[i].changed_element = "未知"
                yao_list[i].changed_relative = "錯誤"
            print(f"警告: 無法找到地支 '{branch}' 的五行属性。", file=sys.stderr)


def check_hua_jin_tui(main_branch: str, changed_branch: str) -> Optional[str]:
    """
    檢查化進神/化退神
    
    化進神：寅→卯, 申→酉, 未→戌, 丑→辰
    化退神：卯→寅, 酉→申, 戌→未, 辰→丑
    
    Args:
        main_branch: 本卦地支
        changed_branch: 變卦地支
    
    Returns:
        "化進神", "化退神", 或 None
    """
    # 化進神映射
    hua_jin_map = {
        "寅": "卯",
        "申": "酉",
        "未": "戌",
        "丑": "辰"
    }
    
    # 化退神映射
    hua_tui_map = {
        "卯": "寅",
        "酉": "申",
        "戌": "未",
        "辰": "丑"
    }
    
    # 檢查化進神
    if main_branch in hua_jin_map and changed_branch == hua_jin_map[main_branch]:
        return "化進神"
    
    # 檢查化退神
    if main_branch in hua_tui_map and changed_branch == hua_tui_map[main_branch]:
        return "化退神"
    
    return None


def check_hui_tou_sheng_ke(main_element: str, changed_element: str) -> Optional[str]:
    """
    檢查回頭生/回頭克
    
    回頭生：變卦五行生本卦五行 (changed_element 生 main_element)
    回頭克：變卦五行克本卦五行 (changed_element 克 main_element)
    
    Args:
        main_element: 本卦五行
        changed_element: 變卦五行
    
    Returns:
        "回頭生", "回頭克", 或 None
    """
    if not main_element or not changed_element:
        return None
    
    # 檢查五行是否有效
    if main_element not in fiveElementIndex or changed_element not in fiveElementIndex:
        return None
    
    main_idx = fiveElementIndex[main_element]
    changed_idx = fiveElementIndex[changed_element]
    
    # 判断 changed_element 对 main_element 的关系
    # 生：changed_idx 生 main_idx，即 (main_idx - changed_idx + 5) % 5 == 1
    # 克：changed_idx 克 main_idx，即 (main_idx - changed_idx + 5) % 5 == 2
    
    diff = (main_idx - changed_idx + 5) % 5
    
    if diff == 1:
        return "回頭生"  # changed_element 生 main_element
    elif diff == 2:
        return "回頭克"  # changed_element 克 main_element
    
    return None


@lru_cache(maxsize=1000)
def bazi_from_date_string(date_str: str) -> BaZi:
    """从日期字符串创建八字對象
    
    Args:
        date_str: 日期時間字符串，支持以下格式：
            - "YYYY/MM/DD HH:MM" (例如: "2025/12/01 19:00")
            - "YYYY/MM/DD HH:MM:SS" (例如: "2025/12/01 19:00:30")
            - "YYYY-MM-DD HH:MM" (例如: "2025-12-01 19:00")
            - "YYYY-MM-DD HH:MM:SS" (例如: "2025-12-01 19:00:30")
    
    Returns:
        BaZi 對象
    
    Raises:
        ValueError: 如果日期格式無效或無法解析
        NotImplementedError: 如果 lunar_python 库不可用
    
    Example:
        >>> bazi = bazi_from_date_string("2025/12/01 19:00")
        >>> print(bazi.year.to_string())  # 输出年柱
    """
    import re
    
    # 支持的日期格式模式
    patterns = [
        # YYYY/MM/DD HH:MM:SS
        (r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})', 
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)), 
                   int(m.group(4)), int(m.group(5)), int(m.group(6)))),
        # YYYY/MM/DD HH:MM
        (r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})', 
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)), 
                   int(m.group(4)), int(m.group(5)), 0)),
        # YYYY-MM-DD HH:MM:SS
        (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})', 
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)), 
                   int(m.group(4)), int(m.group(5)), int(m.group(6)))),
        # YYYY-MM-DD HH:MM
        (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})', 
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)), 
                   int(m.group(4)), int(m.group(5)), 0)),
    ]
    
    # 尝试匹配日期格式
    for pattern, extractor in patterns:
        match = re.match(pattern, date_str.strip())
        if match:
            try:
                year, month, day, hour, minute, second = extractor(match)
                
                # 验证日期范围
                if not (1 <= month <= 12):
                    raise ValueError(f"Invalid month: {month} (must be 1-12)")
                if not (1 <= day <= 31):
                    raise ValueError(f"Invalid day: {day} (must be 1-31)")
                if not (0 <= hour <= 23):
                    raise ValueError(f"Invalid hour: {hour} (must be 0-23)")
                if not (0 <= minute <= 59):
                    raise ValueError(f"Invalid minute: {minute} (must be 0-59)")
                if not (0 <= second <= 59):
                    raise ValueError(f"Invalid second: {second} (must be 0-59)")
                
                # 使用 BaZi.from_solar() 创建八字
                try:
                    return BaZi.from_solar(year, month, day, hour, minute, second)
                except (NotImplementedError, ImportError, AttributeError) as e:
                    error_msg = (
                        f"\n{'='*70}\n"
                        f"ERROR: Cannot calculate BaZi from date string!\n"
                        f"{'='*70}\n"
                        f"The 'lunar_python' library is required to calculate BaZi from solar dates.\n"
                        f"Date requested: {date_str}\n\n"
                        f"To fix this, please install the 'lunar_python' library:\n"
                        f"  pip install lunar_python\n\n"
                        f"Alternatively, you can create BaZi manually:\n"
                        f"  from ba_zi_base import Pillar, BaZi\n"
                        f"  bazi = BaZi(\n"
                        f"      Pillar('年干', '年支'),\n"
                        f"      Pillar('月干', '月支'),\n"
                        f"      Pillar('日干', '日支'),\n"
                        f"      Pillar('时干', '时支')\n"
                        f"  )\n"
                        f"{'='*70}\n"
                    )
                    raise NotImplementedError(error_msg) from e
            except ValueError as e:
                raise ValueError(f"Invalid date value in '{date_str}': {e}") from e
    
    # 如果没有匹配到任何格式
    raise ValueError(
        f"Invalid date format: '{date_str}'\n"
        f"Supported formats:\n"
        f"  - YYYY/MM/DD HH:MM (e.g., '2025/12/01 19:00')\n"
        f"  - YYYY/MM/DD HH:MM:SS (e.g., '2025/12/01 19:00:30')\n"
        f"  - YYYY-MM-DD HH:MM (e.g., '2025-12-01 19:00')\n"
        f"  - YYYY-MM-DD HH:MM:SS (e.g., '2025-12-01 19:00:30')"
    )


def six_yao_divination(main_hexagram_code: str, bazi: BaZi, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]:
    """主排盘函数
    
    Args:
        main_hexagram_code: 本卦代码（6位字符串，'1'=阳爻，'0'=阴爻，从下往上）
        bazi: 八字對象（BaZi）
        changing_line_indices: 動爻位置列表（1-6）
    
    Returns:
        (yao_list, result_json): 六爻详细信息列表和结果JSON字典
    """
    
    result_json = {}
    result_json["ba_zi"] = {
        "year": bazi.year.to_string() if hasattr(bazi.year, 'to_string') else str(bazi.year),
        "month": bazi.month.to_string() if hasattr(bazi.month, 'to_string') else str(bazi.month),
        "day": bazi.day.to_string() if hasattr(bazi.day, 'to_string') else str(bazi.day),
        "hour": bazi.hour.to_string() if hasattr(bazi.hour, 'to_string') else str(bazi.hour),
    }
    # 添加旬空信息
    if hasattr(bazi, 'xun_kong_1') and bazi.xun_kong_1:
        result_json["ba_zi"]["xun_kong_1"] = bazi.xun_kong_1
    if hasattr(bazi, 'xun_kong_2') and bazi.xun_kong_2:
        result_json["ba_zi"]["xun_kong_2"] = bazi.xun_kong_2
    
    # ===== 第1步：初始化本卦信息 =====
    main_info = HEXAGRAM_MAP[main_hexagram_code]
    liu_yao = initialize_yao_details_vector(main_info, changing_line_indices)
    
    # 生成本卦天干地支（纳甲）
    generate_tian_gan_and_di_zhi(liu_yao, main_info, 0)
    # 预留三合局字段（将在所有信息计算完成后更新）
    result_json["san_he_ju"] = None
    result_json["ben_gua_name"] = main_info.get_detailed_name()
    result_json["ben_gua_info"] = {
        "palace": main_info.palace_type,
        "name": main_info.name,
        "structure_type": main_info.structure_type,
        "five_element": main_info.five_element,
        "meaning": main_info.meaning
    }
    
    # ===== 第2步：填充爻的阴阳类型 =====
    for i in range(6):
        liu_yao[i].main_yao_type = main_hexagram_code[i]  # '0' 或 '1'
    
    # ===== 第3步：标记動爻 =====
    for change_idx in changing_line_indices:
        if 1 <= change_idx <= 6:
            yao_index = change_idx - 1  # 转换为 0-based index
            liu_yao[yao_index].is_changing = True
            liu_yao[yao_index].change_mark = "O" if liu_yao[yao_index].main_yao_type == '1' else "X"  # 阳动O, 阴动X
    
    # ===== 第4步：计算本卦五行和六亲 =====
    main_palace_element = main_info.five_element
    fill_element_and_relative(liu_yao, main_palace_element, True)
    
    # ===== 第5步：处理變卦（如果有動爻）=====
    if changing_line_indices:
        # 生成變卦代码
        changed_hexagram_code = list(main_hexagram_code)
        for idx in changing_line_indices:
            if 1 <= idx <= 6:
                array_index = idx - 1  # 转换为 0-5
                changed_hexagram_code[array_index] = '1' if changed_hexagram_code[array_index] == '0' else '0'
            else:
                print(f"警告: 動爻位置超出范围: {idx}", file=sys.stderr)
        
        changed_hexagram_code = ''.join(changed_hexagram_code)
        
        # 获取變卦信息并生成纳甲
        changed_info = HEXAGRAM_MAP[changed_hexagram_code]
        generate_tian_gan_and_di_zhi(liu_yao, changed_info, 1)
        result_json["bian_gua_name"] = changed_info.get_detailed_name()
        result_json["bian_gua_info"] = {
            "palace": changed_info.palace_type,
            "name": changed_info.name,
            "structure_type": changed_info.structure_type,
            "five_element": changed_info.five_element,
            "meaning": changed_info.meaning
        }
        
        # 计算變卦五行和六亲（注意：变爻六亲相对于本卦宫位五行）
        fill_element_and_relative(liu_yao, main_palace_element, False)
    
    # ===== 第6步：计算伏神 =====
    # 获取本宫卦代码
    palace_code_map = {
        "乾": "111111", "坎": "010010", "艮": "001001", "震": "100100",
        "巽": "011011", "離": "101101", "坤": "000000", "兌": "110110"
    }
    
    palace_type = main_info.palace_type
    if palace_type in palace_code_map:
        base_palace_code = palace_code_map[palace_type]
        base_palace_info = HEXAGRAM_MAP[base_palace_code]
        calculate_hidden_gods(base_palace_info, main_palace_element, liu_yao)
    else:
        print(f"警告：未知的宫位类型: {palace_type}", file=sys.stderr)
    
    # ===== 第7步：计算六神 =====
    day_stem = bazi.day.stem()
    if day_stem and day_stem in DAY_STEM_TO_SPIRIT_START:
        start_idx = DAY_STEM_TO_SPIRIT_START[day_stem]
        for i in range(6):
            spirit_idx = (start_idx + i) % 6
            liu_yao[i].spirit = SIX_SPIRITS[spirit_idx]
    else:
        print(f"警告：無法计算六神（日干: {day_stem}）", file=sys.stderr)
        for i in range(6):
            liu_yao[i].spirit = "空" if not day_stem else "未知"
    
    # ===== 第8步：计算旺衰 =====
    month_branch = bazi.month.branch()
    day_branch = bazi.day.branch()
    for i in range(6):
        # 获取爻支（如果存在）
        line_branch = None
        if liu_yao[i].main_pillar is not None:
            line_branch = liu_yao[i].main_pillar.branch()
        liu_yao[i].wang_shuai = getWangShuai(liu_yao[i].main_element, month_branch, line_branch)
        
        # 判断臨日和日扶
        if line_branch is not None:
            lin_ri, ri_fu = checkLinRiRiFu(line_branch, day_branch)
            liu_yao[i].lin_ri = lin_ri
            liu_yao[i].ri_fu = ri_fu
        
        # 判断日生和日克
        ri_sheng, ri_ke = checkRiShengRiKe(liu_yao[i].main_element, day_branch)
        liu_yao[i].ri_sheng = ri_sheng
        liu_yao[i].ri_ke = ri_ke
    
    # ===== 第8.5步：标记旬空（在计算神煞之前） =====
    # 获取旬空地支
    xun_kong_branches = []
    if hasattr(bazi, 'xun_kong_1') and bazi.xun_kong_1:
        xun_kong_branches.append(bazi.xun_kong_1)
    if hasattr(bazi, 'xun_kong_2') and bazi.xun_kong_2:
        xun_kong_branches.append(bazi.xun_kong_2)
    
    # 为每个爻标记旬空
    for yao in liu_yao:
        if yao.main_pillar is not None:
            yao_branch = yao.main_pillar.branch()
            # 檢查旬空
            if yao_branch in xun_kong_branches:
                yao.xun_kong = True
    
    # ===== 第9步：计算神煞 =====
    shen_sha_map = build_shen_sha_map(bazi)
    result_json["shen_sa"] = shen_sha_map
    
    # ===== 第10步：为每个爻标记神煞 =====
    day_branch = bazi.day.branch()
    month_branch = bazi.month.branch()
    
    # 获取月破、日沖、月合、日合
    yue_peng_branches = shen_sha_map.get("月破", [])
    ri_chong_branches = shen_sha_map.get("日沖", [])
    yue_he_branches = shen_sha_map.get("月合", [])
    ri_he_branches = shen_sha_map.get("日合", [])
    
    # 为每个爻标记神煞
    for yao in liu_yao:
        if yao.main_pillar is not None:
            yao_branch = yao.main_pillar.branch()
            
            # 檢查月破
            if yao_branch in yue_peng_branches:
                yao.yue_peng = True
            
            # 檢查日沖
            if yao_branch in ri_chong_branches:
                yao.ri_chong = True
            
            # 檢查月合并判断类型
            # 标准六合关系
            if yao_branch in yue_he_branches:
                he_type = get_he_type(month_branch, yao_branch, is_month=True)
                if he_type:
                    yao.yue_he = he_type
            # 特殊情况：辰月->寅爻/卯爻、未月->巳爻/午爻也是月平合
            elif month_branch == "辰" and yao_branch in ["寅", "卯"]:
                yao.yue_he = "平合"
            elif month_branch == "未" and yao_branch in ["巳", "午"]:
                yao.yue_he = "平合"
            
            # 檢查日合并判断类型
            if yao_branch in ri_he_branches:
                he_type = get_he_type(day_branch, yao_branch, is_month=False)
                if he_type:
                    yao.ri_he = he_type
            
            # 判断暗動和日破（仅对静爻且日沖）
            if yao.ri_chong and not yao.is_changing:
                # 判断是否为月旺相
                # 月旺相包括：月生、月生合、月平合、月扶、臨月
                is_yue_wang_xiang = False
                if yao.wang_shuai in ["月生", "月扶", "臨月"]:
                    is_yue_wang_xiang = True
                elif yao.yue_he in ["生合", "平合"]:
                    is_yue_wang_xiang = True
                
                if is_yue_wang_xiang:
                    yao.an_dong = True  # 暗動
                else:
                    yao.ri_peng = True  # 日破
            
            # 檢查其他神煞（祿、刃、桃花、驛馬等）
            for shen_sha_name, branches in shen_sha_map.items():
                if shen_sha_name not in ["太歲", "月建", "日辰", "月破", "日沖", "月合", "日合"]:
                    if yao_branch in branches:
                        # 简化标记名称
                        marker_name = shen_sha_name
                        if shen_sha_name == "桃花":
                            marker_name = "桃花"
                        elif shen_sha_name == "日祿":
                            marker_name = "祿"
                        elif shen_sha_name == "羊刃":
                            marker_name = "羊刃"
                        elif shen_sha_name == "驛馬":
                            marker_name = "驛馬"
                        elif shen_sha_name == "天馬":
                            marker_name = "天馬"
                        elif shen_sha_name == "華蓋":
                            marker_name = "蓋"
                        elif shen_sha_name == "將星":
                            marker_name = "將"
                        elif shen_sha_name == "劫煞":
                            marker_name = "劫"
                        elif shen_sha_name == "災煞":
                            marker_name = "災"
                        elif shen_sha_name == "文昌":
                            marker_name = "昌"
                        elif shen_sha_name == "謀星":
                            marker_name = "謀"
                        elif shen_sha_name == "日德":
                            marker_name = "德"
                        elif shen_sha_name == "貴人":
                            marker_name = "貴人"
                        
                        if marker_name not in yao.shen_sha_markers:
                            yao.shen_sha_markers.append(marker_name)
    
    # ===== 第10.3步：為變卦（動爻變卦）計算日月關係 =====
    # 只對有變卦的動爻計算
    for yao in liu_yao:
        if yao.is_changing and yao.changed_pillar is not None:
            changed_branch = yao.changed_pillar.branch()
            changed_element = yao.changed_element
            
            # 標記變卦旬空
            if changed_branch in xun_kong_branches:
                yao.changed_xun_kong = True
            
            # 計算變卦臨日和日扶
            lin_ri, ri_fu = checkLinRiRiFu(changed_branch, day_branch)
            yao.changed_lin_ri = lin_ri
            yao.changed_ri_fu = ri_fu
            
            # 計算變卦日生和日克
            ri_sheng, ri_ke = checkRiShengRiKe(changed_element, day_branch)
            yao.changed_ri_sheng = ri_sheng
            yao.changed_ri_ke = ri_ke
            
            # 檢查變卦月破
            if changed_branch in yue_peng_branches:
                yao.changed_yue_peng = True
            
            # 檢查變卦日沖
            if changed_branch in ri_chong_branches:
                yao.changed_ri_chong = True
            
            # 檢查變卦月合並判斷類型
            if changed_branch in yue_he_branches:
                he_type = get_he_type(month_branch, changed_branch, is_month=True)
                if he_type:
                    yao.changed_yue_he = he_type
            # 特殊情況：辰月->寅爻/卯爻、未月->巳爻/午爻也是月平合
            elif month_branch == "辰" and changed_branch in ["寅", "卯"]:
                yao.changed_yue_he = "平合"
            elif month_branch == "未" and changed_branch in ["巳", "午"]:
                yao.changed_yue_he = "平合"
            
            # 檢查變卦日合並判斷類型
            if changed_branch in ri_he_branches:
                he_type = get_he_type(day_branch, changed_branch, is_month=False)
                if he_type:
                    yao.changed_ri_he = he_type
            
            # 判斷變卦暗動和日破（僅對靜爻且日沖，但變卦都是動爻，所以通常不適用）
            # 但為了完整性，我們還是檢查一下
            if yao.changed_ri_chong:
                # 變卦是動爻的結果，所以通常不需要判斷暗動/日破
                # 但如果需要，可以基於變卦的旺衰狀態判斷
                # 這裡暫時不計算，因為變卦都是動爻的結果
                pass
    
    # ===== 第10.5步：檢查化進神/化退神和回頭生/回頭克（仅对動爻）=====
    # 这些信息将显示在變卦栏位，而不是神煞栏位
    for yao in liu_yao:
        if yao.is_changing:
            # 檢查化進神/化退神（存储用于在變卦栏位显示）
            if yao.main_pillar is not None and yao.changed_pillar is not None:
                main_branch = yao.main_pillar.branch()
                changed_branch = yao.changed_pillar.branch()
                hua_result = check_hua_jin_tui(main_branch, changed_branch)
                if hua_result:
                    # 存储到 shen_sha_markers 中，但会在显示时从神煞栏位过滤掉，显示在變卦栏位
                    if hua_result not in yao.shen_sha_markers:
                        yao.shen_sha_markers.append(hua_result)
            
            # 檢查回頭生/回頭克（存储用于在變卦栏位显示）
            if yao.main_element and yao.changed_element:
                hui_tou_result = check_hui_tou_sheng_ke(yao.main_element, yao.changed_element)
                if hui_tou_result:
                    # 存储到 shen_sha_markers 中，但会在显示时从神煞栏位过滤掉，显示在變卦栏位
                    if hui_tou_result not in yao.shen_sha_markers:
                        yao.shen_sha_markers.append(hui_tou_result)
    
    # ===== 第10.6步：判断三合局（在所有信息计算完成后）=====
    san_he_ju_result = check_san_he_ju(liu_yao, bazi)
    if san_he_ju_result:
        result_json["san_he_ju"] = san_he_ju_result
    
    # ===== 第11步：输出排盘结果（调试模式）=====
    # 可以在这里添加调试输出
    
    # ===== 返回结果 =====
    result_json["yao"] = [yao.to_dict() for yao in liu_yao]
    return liu_yao, result_json


def six_yao_divination_from_date(main_hexagram_code: str, date_str: str, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]:
    """从日期字符串进行六爻排盘（便捷函数）
    
    Args:
        main_hexagram_code: 本卦代码（6位字符串，'1'=阳爻，'0'=阴爻，从下往上）
        date_str: 日期時間字符串，支持格式：
            - "YYYY/MM/DD HH:MM" (例如: "2025/12/01 19:00")
            - "YYYY/MM/DD HH:MM:SS" (例如: "2025/12/01 19:00:30")
            - "YYYY-MM-DD HH:MM" (例如: "2025-12-01 19:00")
            - "YYYY-MM-DD HH:MM:SS" (例如: "2025-12-01 19:00:30")
        changing_line_indices: 動爻位置列表（1-6）
    
    Returns:
        (yao_list, result_json): 六爻详细信息列表和结果JSON字典
    
    Example:
        >>> yao_list, result = six_yao_divination_from_date(
        ...     "111111", 
        ...     "2025/12/01 19:00", 
        ...     [1]
        ... )
    """
    bazi = bazi_from_date_string(date_str)
    return six_yao_divination(main_hexagram_code, bazi, changing_line_indices)


def display_width(s: str) -> int:
    """Calculate the display width of a string, considering Chinese characters.
    
    Chinese characters (CJK) typically take 2 display units, while ASCII
    characters take 1 display unit.
    
    Args:
        s: Input string
        
    Returns:
        Display width (number of character units)
    """
    width = 0
    for char in s:
        # Check if character is a CJK (Chinese, Japanese, Korean) character
        if '\u4e00' <= char <= '\u9fff' or \
           '\u3400' <= char <= '\u4dbf' or \
           '\uf900' <= char <= '\ufaff' or \
           '\u3000' <= char <= '\u303f':  # CJK punctuation
            width += 2
        else:
            width += 1
    return width


def pad_to_display_width(s: str, target_width: int, align: str = 'left') -> str:
    """Pad a string to a specific display width, considering Chinese characters.
    
    Args:
        s: Input string
        target_width: Target display width
        align: Alignment, 'left' or 'right' (default: 'left')
        
    Returns:
        Padded string with display width equal to target_width
    """
    current_width = display_width(s)
    if current_width >= target_width:
        return s
    
    padding_needed = target_width - current_width
    # Use double spaces (each takes 2 display units) for padding
    num_double_spaces = padding_needed // 2
    padding = "  " * num_double_spaces
    
    if align == 'left':
        return s + padding
    else:
        return padding + s


def get_char_length_for_display_width(target_display_width: int) -> int:
    """Calculate the character length needed to achieve a target display width.
    
    Since Chinese characters take 2 display units and ASCII takes 1,
    we need to estimate the character length. For padding purposes,
    we assume we'll use double spaces (2 chars = 2 display units).
    
    Args:
        target_display_width: Target display width
        
    Returns:
        Estimated character length needed
    """
    # For padding, we use double spaces, so character length ≈ display width
    # But we need to account for the fact that existing content may have mixed widths
    # For simplicity, we'll use target_display_width as an approximation
    # The actual padding will be handled by pad_to_display_width
    return target_display_width

def format_liu_yao_display_pc(yao_list: List[YaoDetails], show_shen_sha: bool = True, for_gradio: bool = False) -> str:
    """格式化六爻排盤結果，輸出為PC友好格式（簡化版，更易讀）
    
    Args:
        yao_list: 六爻詳細信息列表（position 1-6，從下往上）
        show_shen_sha: 是否顯示神煞標記（默認True）
        for_gradio: 是否為Gradio界面顯示（默認False，終端顯示用6個字符，Gradio用5個字符）
    
    Returns:
        格式化後的字符串，使用簡化的表格格式
    """
    lines = []
    
    # Line number mapping: position 6 -> [六], position 5 -> [五], ..., position 1 -> [初]
    line_numbers = ["六", "五", "四", "三", "二", "初"]
    
    # Check if all relatives are present (to determine if we show hidden gods)
    main_relatives = set()
    for yao in yao_list:
        if yao.main_relative and yao.main_relative not in ["錯誤", "未知", ""]:
            main_relatives.add(yao.main_relative)
    all_relatives_present = len(main_relatives) == len(RELATIVE_NAMES) and all(rel in main_relatives for rel in RELATIVE_NAMES)
    
    # First pass: collect all column data and calculate max widths
    spirit_cols = []
    hidden_cols = []
    ben_gua_cols = []
    bian_gua_cols = []
    shen_sha_cols = []
    
    for idx in range(5, -1, -1):
        yao = yao_list[idx]
        
        # Six Spirits (六獸) - format with space between characters
        spirit = ""
        if yao.spirit:
            spirit = "  ".join(list(yao.spirit))
        else:
            spirit = "   "
        spirit_cols.append(spirit)
        
        # Hidden God (伏神) - in parentheses if present
        hidden_str = ""
        if not all_relatives_present:
            if yao.hidden_pillar is not None and yao.hidden_pillar.to_string():
                hidden_pillar_str = yao.hidden_pillar.to_string()
                hidden_element = yao.hidden_element if yao.hidden_element else ""
                hidden_relative = yao.hidden_relative if yao.hidden_relative else ""
                if hidden_relative and hidden_pillar_str and hidden_element:
                    hidden_str = f"({hidden_relative}{hidden_pillar_str}{hidden_element})"
        hidden_cols.append(hidden_str)
        
        # Main Hexagram (本卦)
        main_relative = yao.main_relative if yao.main_relative else ""
        main_shi_ying = yao.shi_ying_mark if yao.shi_ying_mark != " " else ""
        
        if yao.main_yao_type == '1':
            yao_type_str = "▇▇▇" if for_gradio else "▇▇▇▇▇▇"
        else:
            yao_type_str = "▇  ▇"
        
        main_pillar_full = ""
        if yao.main_pillar is not None:
            main_pillar_str = yao.main_pillar.to_string()
            main_element = yao.main_element if yao.main_element else ""
            main_pillar_full = f"{main_pillar_str}{main_element}"
        
        change_mark = ""
        if yao.is_changing:
            if yao.change_mark == "O":
                change_mark = "○"
            elif yao.change_mark == "X":
                change_mark = "×"
        
        # Build marker parts for 本卦
        # 標記優先順序說明：
        # 1. 月破 - 最高優先級（月建沖破）
        # 2. 旬空 - 獨立標記，不與其他衝突
        # 3. 日沖系列（暗動/日破/日沖）- 優先於日扶、日克
        # 4. 月合系列（月生合/月克合/月平合/月合）- 獨立標記
        # 5. 日合系列（日生合/日克合/日合）- 優先於日生、日克
        # 6. 臨日 - 獨立標記
        # 7. 日扶 - 需排除日沖（日沖優先）
        # 8. 日生 - 需排除日生合（日生合優先）
        # 9. 日克 - 需排除日克合和日沖（日克合優先，日沖優先）
        marker_parts = []
        if main_shi_ying!="":
            marker_parts.append(main_shi_ying)
        if yao.wang_shuai and yao.wang_shuai.strip():
            if yao.yue_peng:
                if yao.wang_shuai not in ["休", "囚", "月生", "月克"]:
                    marker_parts.append(yao.wang_shuai)
            elif yao.yue_he:
                if yao.wang_shuai not in ["休", "囚", "月生", "月克"]:
                    marker_parts.append(yao.wang_shuai)
            else:
                marker_parts.append(yao.wang_shuai)
        # 1. 月破（最高優先級）
        if yao.yue_peng:
            marker_parts.append("月破")
        # 2. 旬空（獨立標記）
        if yao.xun_kong:
            marker_parts.append("旬空")
        # 3. 日沖系列（優先於日扶、日克）
        if yao.ri_chong:
            if yao.an_dong:
                marker_parts.append("暗動")
            elif yao.ri_peng:
                marker_parts.append("日破")
            else:
                marker_parts.append("日沖")
        # 4. 月合系列（獨立標記）
        if yao.yue_he:
            if yao.yue_he == "生合":
                marker_parts.append("月生合")
            elif yao.yue_he == "克合":
                marker_parts.append("月克合")
            elif yao.yue_he == "平合":
                marker_parts.append("月平合")
            else:
                marker_parts.append("月合")
        # 5. 日合系列（優先於日生、日克）
        if yao.ri_he:
            if yao.ri_he == "生合":
                marker_parts.append("日生合")
            elif yao.ri_he == "克合":
                marker_parts.append("日克合")
            else:
                marker_parts.append("日合")
        # 6. 臨日（獨立標記）
        if yao.lin_ri:
            marker_parts.append("臨日")
        # 7. 日扶（需排除日沖：日沖優先）
        if yao.ri_fu and not yao.ri_chong:
            marker_parts.append("日扶")
        # 8. 日生（需排除日生合：日生合優先）
        if yao.ri_sheng and yao.ri_he != "生合":
            marker_parts.append("日生")
        # 9. 日克（需排除日克合和日沖：日克合優先，日沖優先）
        if yao.ri_ke and yao.ri_he != "克合" and not yao.ri_chong:
            marker_parts.append("日克")
        
        # Build 本卦 string: 父母 己巳火 ▇▇▇ ○ [月破]
        ben_gua_parts = []
        if main_relative:
            ben_gua_parts.append(main_relative)
        if main_pillar_full:
            ben_gua_parts.append(main_pillar_full)
        ben_gua_parts.append(yao_type_str)
        if change_mark:
            ben_gua_parts.append(change_mark)
        if marker_parts:
            ben_gua_parts.append("[" + "/".join(marker_parts) + "]")
        ben_gua_str = " ".join(ben_gua_parts)
        ben_gua_cols.append(ben_gua_str)
        
        # Changed Hexagram (變卦)
        bian_gua_str = ""
        if yao.changed_pillar is not None:
            changed_pillar_str = yao.changed_pillar.to_string()
            changed_element = yao.changed_element if yao.changed_element else ""
            changed_relative = yao.changed_relative if yao.changed_relative else ""
            
            if yao.is_changing:
                if yao.main_yao_type == '1':
                    changed_yao_type = "▇  ▇"
                else:
                    changed_yao_type = "▇▇▇" if for_gradio else "▇▇▇▇▇▇"
            else:
                if yao.main_yao_type == '1':
                    changed_yao_type = "▇▇▇" if for_gradio else "▇▇▇▇▇▇"
                else:
                    changed_yao_type = "▇  ▇"
            
            # Build marker parts for 變卦
            changed_marker_parts = []
            #if yao.shi_ying_mark in ["應", "世"]:
                #changed_marker_parts.append(yao.shi_ying_mark)
            
            # Add 化進神/化退神 and 回頭生/回頭克
            for marker in yao.shen_sha_markers:
                if marker in ["化進神", "化退神", "回頭生", "回頭克"]:
                    changed_marker_parts.append(marker)
            
            # Add 變卦的日月關係 (only for changing lines)
            # 標記優先順序說明：
            # 1. 月破 - 最高優先級（月建沖破）
            # 2. 旬空 - 獨立標記，不與其他衝突
            # 3. 日沖系列（暗動/日破/日沖）- 優先於日扶、日克
            # 4. 月合系列（月生合/月克合/月平合/月合）- 獨立標記
            # 5. 日合系列（日生合/日克合/日合）- 優先於日生、日克
            # 6. 臨日 - 獨立標記
            # 7. 日扶 - 需排除日沖（日沖優先）
            # 8. 日生 - 需排除日生合（日生合優先）
            # 9. 日克 - 需排除日克合和日沖（日克合優先，日沖優先）
            if yao.is_changing:
                # 1. 月破（最高優先級）
                if yao.changed_yue_peng:
                    changed_marker_parts.append("月破")
                # 2. 旬空（獨立標記）
                if yao.changed_xun_kong:
                    changed_marker_parts.append("旬空")
                # 3. 日沖系列（優先於日扶、日克）
                if yao.changed_ri_chong:
                    if yao.changed_an_dong:
                        changed_marker_parts.append("暗動")
                    elif yao.changed_ri_peng:
                        changed_marker_parts.append("日破")
                    else:
                        changed_marker_parts.append("日沖")
                # 4. 月合系列（獨立標記）
                if yao.changed_yue_he:
                    if yao.changed_yue_he == "生合":
                        changed_marker_parts.append("月生合")
                    elif yao.changed_yue_he == "克合":
                        changed_marker_parts.append("月克合")
                    elif yao.changed_yue_he == "平合":
                        changed_marker_parts.append("月平合")
                    else:
                        changed_marker_parts.append("月合")
                # 5. 日合系列（優先於日生、日克）
                if yao.changed_ri_he:
                    if yao.changed_ri_he == "生合":
                        changed_marker_parts.append("日生合")
                    elif yao.changed_ri_he == "克合":
                        changed_marker_parts.append("日克合")
                    else:
                        changed_marker_parts.append("日合")
                # 6. 臨日（獨立標記）
                if yao.changed_lin_ri:
                    changed_marker_parts.append("臨日")
                # 7. 日扶（需排除日沖：日沖優先）
                if yao.changed_ri_fu and not yao.changed_ri_chong:
                    changed_marker_parts.append("日扶")
                # 8. 日生（需排除日生合：日生合優先）
                if yao.changed_ri_sheng and yao.changed_ri_he != "生合":
                    changed_marker_parts.append("日生")
                # 9. 日克（需排除日克合和日沖：日克合優先，日沖優先）
                if yao.changed_ri_ke and yao.changed_ri_he != "克合" and not yao.changed_ri_chong:
                    changed_marker_parts.append("日克")
            
            # Build 變卦 string: 兄弟 丁未土 ▇  ▇ [月破]
            bian_gua_parts = []
            if changed_relative:
                bian_gua_parts.append(changed_relative)
            if changed_pillar_str and changed_element:
                bian_gua_parts.append(f"{changed_pillar_str}{changed_element}")
            bian_gua_parts.append(changed_yao_type)
            if changed_marker_parts:
                bian_gua_parts.append("[" + "/".join(changed_marker_parts) + "]")
            bian_gua_str = " ".join(bian_gua_parts)
        bian_gua_cols.append(bian_gua_str)
        
        # Shen sha markers (神煞) - shown in rightmost column
        shen_sha_str = ""
        if show_shen_sha:
            # Filter out markers that are already shown in 本卦 or 變卦
            filtered_shen_sha = [m for m in yao.shen_sha_markers 
                                if m not in ["化進神", "化退神", "回頭生", "回頭克"]]
            if filtered_shen_sha:
                shen_sha_str = " ".join(filtered_shen_sha)
        shen_sha_cols.append(shen_sha_str)
    
    # Calculate max display widths for each column
    max_spirit_width = max(display_width(s) for s in spirit_cols) if spirit_cols else 6
    max_hidden_width = max(display_width(s) for s in hidden_cols) if hidden_cols else 0
    max_ben_gua_width = max(display_width(s) for s in ben_gua_cols) if ben_gua_cols else 0
    max_bian_gua_width = max(display_width(s) for s in bian_gua_cols) if bian_gua_cols else 0
    max_shen_sha_width = max(display_width(s) for s in shen_sha_cols) if shen_sha_cols else 0
    
    # Header - more compact spacing
    header = "        六獸    伏  神              本  卦                                       變  卦                           神 煞"
    lines.append(header)
    lines.append("─────────────────────────────────────────────────────────────")
    
    # Second pass: build rows with proper alignment and compact spacing
    for idx in range(5, -1, -1):
        yao_idx = 5 - idx
        line_num = line_numbers[yao_idx]
        
        # Pad each column to max width (except 變卦 and 神煞 for compact layout)
        spirit_padded = pad_to_display_width(spirit_cols[yao_idx], max_spirit_width)
        hidden_padded = pad_to_display_width(hidden_cols[yao_idx], max_hidden_width) if max_hidden_width > 0 else hidden_cols[yao_idx]
        ben_gua_padded = pad_to_display_width(ben_gua_cols[yao_idx], max_ben_gua_width)
        # Don't pad 變卦 to max width - use actual content width for compact layout
        bian_gua_str = bian_gua_cols[yao_idx] if bian_gua_cols[yao_idx] else ""
        # Don't pad 神煞 - use actual content width for compact layout
        shen_sha_str = shen_sha_cols[yao_idx] if shen_sha_cols[yao_idx] else ""
        
        # Build the row with compact spacing
        # Format: [六]   朱  雀  (伏神)  本卦内容      ➔   變卦内容    神煞
        row = f"[{line_num}]    {spirit_padded}"
        if hidden_padded:
            row += f"  {hidden_padded}"
        # Add compact spacing (2 spaces) before 本卦
        row += "  " + ben_gua_padded
        if bian_gua_str:
            row += "  ➔  " + bian_gua_str
        if shen_sha_str:
            row += "  " + shen_sha_str
        
        lines.append(row)
    
    lines.append("───────────────────────────────────────────────────────────")
    
    return "\n".join(lines)


def format_liu_yao_display_mobile(yao_list: List[YaoDetails], show_shen_sha: bool = True, for_gradio: bool = False) -> str:
    """格式化六爻排盤結果，輸出為移動端友好格式（垂直緊湊版）
    
    Args:
        yao_list: 六爻詳細信息列表（position 1-6，從下往上）
        show_shen_sha: 是否顯示神煞標記（默認True）
        for_gradio: 是否為Gradio界面顯示（默認False，終端顯示用6個字符，Gradio用5個字符）
    
    Returns:
        格式化後的字符串，使用垂直緊湊格式，適合移動端顯示
    """
    lines = []
    
    # Line number mapping: position 6 -> [六], position 5 -> [五], ..., position 1 -> [初]
    line_numbers = ["六", "五", "四", "三", "二", "初"]
    
    # Check if all relatives are present (to determine if we show hidden gods)
    main_relatives = set()
    for yao in yao_list:
        if yao.main_relative and yao.main_relative not in ["錯誤", "未知", ""]:
            main_relatives.add(yao.main_relative)
    all_relatives_present = len(main_relatives) == len(RELATIVE_NAMES) and all(rel in main_relatives for rel in RELATIVE_NAMES)
    
    # Process each yao from top to bottom (position 6 to 1)
    for idx in range(5, -1, -1):
        yao = yao_list[idx]
        yao_idx = 5 - idx
        line_num = line_numbers[yao_idx]
        
        # Six Spirits (六獸)
        spirit = yao.spirit if yao.spirit else ""
        
        # Main Hexagram (本卦)
        main_relative = yao.main_relative if yao.main_relative else ""
        main_shi_ying = yao.shi_ying_mark if yao.shi_ying_mark != " " else ""

        if yao.main_yao_type == '1':
            yao_type_str = "▇▇▇" if for_gradio else "▇▇▇"
        else:
            yao_type_str = "▇  ▇"
        
        main_pillar_full = ""
        if yao.main_pillar is not None:
            main_pillar_str = yao.main_pillar.to_string()
            main_element = yao.main_element if yao.main_element else ""
            main_pillar_full = f"{main_pillar_str}{main_element}"
        
        change_mark = ""
        if yao.is_changing:
            if yao.change_mark == "O":
                change_mark = "○"
            elif yao.change_mark == "X":
                change_mark = "×"
        
        # Build marker parts for 本卦
        # 標記優先順序說明：
        # 1. 月破 - 最高優先級（月建沖破）
        # 2. 旬空 - 獨立標記，不與其他衝突
        # 3. 日沖系列（暗動/日破/日沖）- 優先於日扶、日克
        # 4. 月合系列（月生合/月克合/月平合/月合）- 獨立標記
        # 5. 日合系列（日生合/日克合/日無平合）- 優先於日生、日克
        # 6. 臨日 - 獨立標記
        # 7. 日扶 - 需排除日沖（日沖優先）
        # 8. 日生 - 需排除日生合（日生合優先）
        # 9. 日克 - 需排除日克合和日沖（日克合優先，日沖優先）
        marker_parts = []
        if main_shi_ying!="":
            marker_parts.append(main_shi_ying)
        if yao.wang_shuai and yao.wang_shuai.strip():
            if yao.yue_peng:
                if yao.wang_shuai not in ["休", "囚", "月生", "月克"]:
                    marker_parts.append(yao.wang_shuai)
            elif yao.yue_he:
                if yao.wang_shuai not in ["休", "囚", "月生", "月克"]:
                    marker_parts.append(yao.wang_shuai)
            else:
                marker_parts.append(yao.wang_shuai)
        # 1. 月破（最高優先級）
        if yao.yue_peng:
            marker_parts.append("月破")
        # 2. 旬空（獨立標記）
        if yao.xun_kong:
            marker_parts.append("旬空")  
        # 3. 日沖系列（優先於日扶、日克）
        if yao.ri_chong:
            if yao.an_dong:
                marker_parts.append("暗動")
            elif yao.ri_peng:
                marker_parts.append("日破")
            else:
                marker_parts.append("日沖")
        # 4. 月合系列（獨立標記）
        if yao.yue_he:
            if yao.yue_he == "生合":
                marker_parts.append("月生合")  
            elif yao.yue_he == "克合":
                marker_parts.append("月克合")  
            elif yao.yue_he == "平合":
                marker_parts.append("月平合")  
            else:
                marker_parts.append("月合")  
        # 5. 日合系列（優先於日生、日克）
        if yao.ri_he:
            if yao.ri_he == "生合":
                marker_parts.append("日生合")  
            elif yao.ri_he == "克合":
                marker_parts.append("日克合")  
            else:
                marker_parts.append("日無平合")  
        # 6. 臨日（獨立標記）
        if yao.lin_ri:
            marker_parts.append("臨日")
        # 7. 日扶（需排除日沖：日沖優先）
        if yao.ri_fu and not yao.ri_chong:
            marker_parts.append("日扶")
        # 8. 日生（需排除日生合：日生合優先）
        if yao.ri_sheng and yao.ri_he != "生合":
            marker_parts.append("日生")
        # 9. 日克（需排除日克合和日沖：日克合優先，日沖優先）
        if yao.ri_ke and yao.ri_he != "克合" and not yao.ri_chong:
            marker_parts.append("日克")  
        
        # Build 本卦 string: 官鬼辛卯木 ▇▇▇ [月生/空/暗動]
        ben_gua_parts = []
        if main_relative:
            ben_gua_parts.append(main_relative)
        if main_pillar_full:
            ben_gua_parts.append(main_pillar_full)
        ben_gua_parts.append(yao_type_str)
        if change_mark:
            ben_gua_parts.append(change_mark)
        if marker_parts:
            ben_gua_parts.append("[" + "/".join(marker_parts) + "]")
        ben_gua_str = " ".join(ben_gua_parts)
        
        # Build main line: 【六】勾陳 官鬼辛卯木 ▇▇▇ [月生/空/暗動]
        main_line = f"\n【{line_num}】{spirit} {ben_gua_str}"
        
        # Add shen sha markers on the same line if present
        shen_sha_on_line = ""
        if show_shen_sha:
            # Filter out markers that are already shown in 本卦 or 變卦
            filtered_shen_sha = [m for m in yao.shen_sha_markers 
                                if m not in ["化進神", "化退神", "回頭生", "回頭克"]]
            # Only show specific shen sha that should appear on the line (like 羊刃)
            for marker in filtered_shen_sha:
                if marker in ["羊刃", "桃花", "驛馬", "貴人"]:
                    if shen_sha_on_line:
                        shen_sha_on_line += " " + marker
                    else:
                        shen_sha_on_line = marker
        
        if shen_sha_on_line:
            main_line += " " + shen_sha_on_line

        lines.append(main_line)
        
        # Changed Hexagram (變卦) - indented
        if yao.changed_pillar is not None:
            changed_pillar_str = yao.changed_pillar.to_string()
            changed_element = yao.changed_element if yao.changed_element else ""
            changed_relative = yao.changed_relative if yao.changed_relative else ""
            
            if yao.is_changing:
                if yao.main_yao_type == '1':
                    changed_yao_type = "▇  ▇"
                else:
                    changed_yao_type = "▇▇▇" if for_gradio else "▇▇▇"
            else:
                if yao.main_yao_type == '1':
                    changed_yao_type = "▇▇▇" if for_gradio else "▇▇▇"
                else:
                    changed_yao_type = "▇  ▇"
            
            # Build marker parts for 變卦 (simplified for mobile)
            changed_marker_parts = []
            #if yao.shi_ying_mark in ["應", "世"]:
                #changed_marker_parts.append(yao.shi_ying_mark)
            
            # Add 化進神/化退神 and 回頭生/回頭克
            for marker in yao.shen_sha_markers:
                if marker in ["化進神", "化退神", "回頭生", "回頭克"]:
                    changed_marker_parts.append(marker)

            # Add 變卦的日月關係 (only for changing lines)
            # 標記優先順序說明：
            # 1. 月破 - 最高優先級（月建沖破）
            # 2. 旬空 - 獨立標記，不與其他衝突
            # 3. 日沖系列（暗動/日破/日沖）- 優先於日扶、日克
            # 4. 月合系列（生合/克合/平合/合）- 獨立標記
            # 5. 日合系列（生合/克合/日無平合）- 優先於日生、日克
            # 6. 臨日 - 獨立標記
            # 7. 日扶 - 需排除日沖（日沖優先）
            # 8. 日生 - 需排除日生合（日生合優先）
            # 9. 日克 - 需排除日克合和日沖（日克合優先，日沖優先）
            if yao.is_changing:
                # 1. 月破（最高優先級）
                if yao.changed_yue_peng:
                    changed_marker_parts.append("月破")
                # 2. 旬空（獨立標記）
                if yao.changed_xun_kong:
                    changed_marker_parts.append("旬空")  
                # 3. 日沖系列（優先於日扶、日克）
                if yao.changed_ri_chong:
                    if yao.changed_an_dong:
                        changed_marker_parts.append("暗動")
                    elif yao.changed_ri_peng:
                        changed_marker_parts.append("日破")
                    else:
                        changed_marker_parts.append("日沖")
                # 4. 月合系列（獨立標記）
                if yao.changed_yue_he:
                    if yao.changed_yue_he == "生合":
                        changed_marker_parts.append("生合") 
                    elif yao.changed_yue_he == "克合":
                        changed_marker_parts.append("克合") 
                    elif yao.changed_yue_he == "平合":
                        changed_marker_parts.append("平合")  
                    else:
                        changed_marker_parts.append("合")  
                # 5. 日合系列（優先於日生、日克）
                if yao.changed_ri_he:
                    if yao.changed_ri_he == "生合":
                        changed_marker_parts.append("生合") 
                    elif yao.changed_ri_he == "克合":
                        changed_marker_parts.append("克合")  
                    else:
                        changed_marker_parts.append("日無平合") 
                # 6. 臨日（獨立標記）
                if yao.changed_lin_ri:
                    changed_marker_parts.append("臨日")
                # 7. 日扶（需排除日沖：日沖優先）
                if yao.changed_ri_fu and not yao.changed_ri_chong:
                    changed_marker_parts.append("日扶")
                # 8. 日生（需排除日生合：日生合優先）
                if yao.changed_ri_sheng and yao.changed_ri_he != "生合":
                    changed_marker_parts.append("日生")
                # 9. 日克（需排除日克合和日沖：日克合優先，日沖優先）
                if yao.changed_ri_ke and yao.changed_ri_he != "克合" and not yao.changed_ri_chong:
                    changed_marker_parts.append("日克")  
            
            # Build 變卦 string: 兄弟壬戌土 ▇▇▇[回頭生]
            # For mobile format, markers go directly after yao_type without space
            bian_gua_content = []
            if changed_relative:
                bian_gua_content.append(changed_relative)
            if changed_pillar_str and changed_element:
                bian_gua_content.append(f"{changed_pillar_str}{changed_element}")
            
            if changed_marker_parts:
                # Join content parts, add yao_type, then markers without space before bracket
                if bian_gua_content:
                    content_str = " ".join(bian_gua_content)
                    bian_gua_str = f"{content_str} {changed_yao_type}[" + "/".join(changed_marker_parts) + "]"
                else:
                    bian_gua_str = f"{changed_yao_type}[" + "/".join(changed_marker_parts) + "]"
            else:
                bian_gua_content.append(changed_yao_type)
                bian_gua_str = " ".join(bian_gua_content)
            
            # Indented line for 變卦
            lines.append(f"    ➔ 變: {bian_gua_str}")
        
        # Hidden God (伏神) - indented, shown on separate line if present
        if not all_relatives_present:
            if yao.hidden_pillar is not None and yao.hidden_pillar.to_string():
                hidden_pillar_str = yao.hidden_pillar.to_string()
                hidden_element = yao.hidden_element if yao.hidden_element else ""
                hidden_relative = yao.hidden_relative if yao.hidden_relative else ""
                if hidden_relative and hidden_pillar_str and hidden_element:
                    hidden_str = f"    ➔ 伏: {hidden_relative}{hidden_pillar_str}{hidden_element}"
                    lines.append(hidden_str)
    
    return "\n".join(lines)


def get_hexagram_map() -> Dict[str, HexagramInfo]:
    """獲取卦象映射表（供外部模塊使用）"""
    return HEXAGRAM_MAP

