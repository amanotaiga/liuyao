"""
Python version of 干支系统模块 (Gan-Zhi System Module)
Converted from C++23 module ganzhi.cppm

Provides core definitions and functions for TianGan (Heavenly Stems) and DiZhi (Earthly Branches).
"""

from enum import IntEnum
from typing import Optional


class DiZhi(IntEnum):
    """
    地支枚举 (Earthly Branches Enum)
    """
    Zi = 0      # 子
    Chou = 1    # 丑
    Yin = 2     # 寅
    Mao = 3     # 卯
    Chen = 4    # 辰
    Si = 5      # 巳
    Wu = 6      # 午
    Wei = 7     # 未
    Shen = 8    # 申
    You = 9     # 酉
    Xu = 10     # 戌
    Hai = 11    # 亥


class Mapper:
    """
    中文名称映射类 (Chinese Name Mapper)
    
    提供天干地支与中文名称之间的转换
    """
    
    # 地支中文名称
    _ZHI_NAMES = [
        "子", "丑", "寅", "卯", "辰", "巳",
        "午", "未", "申", "酉", "戌", "亥"
    ]
    
    @staticmethod
    def to_zh(zhi: DiZhi) -> str:
        """
        将地支枚举转换为中文名称
        
        Args:
            zhi: 地支枚举
        
        Returns:
            中文名称（如 "子"）
        """
        return Mapper._ZHI_NAMES[int(zhi)]
    
    @staticmethod
    def from_zh_zhi(zh_name: str) -> Optional[DiZhi]:
        """
        从中文名称查找地支枚举
        
        Args:
            zh_name: 中文名称（如 "子"）
        
        Returns:
            地支枚举，如果未找到则返回 None
        """
        try:
            idx = Mapper._ZHI_NAMES.index(zh_name)
            return DiZhi(idx)
        except ValueError:
            return None


def is_he(zhi1: DiZhi, zhi2: DiZhi) -> bool:
    """
    判断地支相合（六合）
    
    地支六合是地支之间的合化关系，代表和谐、亲密、合作、喜庆。
    相合主吉祥、团结、婚姻、缘分，力量较三合为弱。
    
    六合对照及合化五行：
    - 子丑合化土：子水配丑土，阴阳相合，水土相济，北方合（鼠牛合）
    - 寅亥合化木：寅木配亥水，木得水生，木旺相生，东北合（虎猪合）
    - 卯戌合化火：卯木配戌土，木火通明，文明之合，东西合（兔狗合）
    - 辰酉合化金：辰土配酉金，土生金旺，金玉良缘，东南西合（龙鸡合）
    - 巳申合化水：巳火配申金，火金相融，水火既济，南西合（蛇猴合）
    - 午未合化土：午火配未土，火土相生，中正之合，南方合（马羊合）
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
    
    Returns:
        True 如果两地支相合
    """
    he_pairs = [
        (0, 1),    # 子(0)丑(1)合化土
        (2, 11),   # 寅(2)亥(11)合化木
        (3, 10),   # 卯(3)戌(10)合化火
        (4, 9),    # 辰(4)酉(9)合化金
        (5, 8),    # 巳(5)申(8)合化水
        (6, 7)     # 午(6)未(7)合化土
    ]
    
    i1 = int(zhi1)
    i2 = int(zhi2)
    
    for a, b in he_pairs:
        if (i1 == a and i2 == b) or (i1 == b and i2 == a):
            return True
    
    return False

