"""
Python version of 八字排盘系统 (BaZi Fortune System)
Converted from C++23 module

This module provides complete BaZi fortune reading functionality, including:
- 大运 (DaYun): 10-year fortune cycles
- 流年 (LiuNian): Yearly fortunes
- 流月 (LiuYue): Monthly fortunes (based on solar terms)
- 流日 (LiuRi): Daily fortunes
- 流时 (LiuShi): Hourly fortunes

Dependencies:
-----------
This module requires the following Python modules:

1. bazi_base module:
   - Pillar class: Represents a 干支 (Gan-Zhi) pillar
   - BaZi class: Represents 八字 (Four Pillars)
   - BaZi.from_solar() static method: Create BaZi from solar date

2. ganzhi module:
   - TianGan: Enum or class for 10 heavenly stems
   - DiZhi: Enum or class for 12 earthly branches
   - ShiShen: Enum or class for 10 gods (十神)
   - get_shi_shen(day_gan, gan) -> ShiShen: Calculate 十神
   - shi_shen_to_zh(shi_shen) -> str: Convert 十神 to Chinese
   - get_cang_gan(zhi) -> List[TianGan]: Get hidden stems in branch
   - get_yin_yang(gan) -> YinYang: Get yin/yang property

3. wuxing_utils module:
   - Various utility functions for five elements

4. tyme module (or equivalent):
   - SolarTime: Solar calendar time
   - SolarDay: Solar calendar day
   - LunarDay: Lunar calendar day
   - LunarMonth: Lunar month
   - LunarYear: Lunar year
   - SixtyCycle: 60-cycle (干支)
   - SolarTerm: Solar term (节气)
   - ChildLimit: Child limit calculation
   - DecadeFortune: 10-year fortune
   - Fortune: Annual fortune
   - Gender: Gender enum (MAN, WOMAN)
   
   Methods needed:
   - SolarTime.from_ymd_hms(year, month, day, hour, minute, second) -> SolarTime
   - SolarDay.from_ymd(year, month, day) -> SolarDay
   - SolarDay.get_lunar_day() -> LunarDay
   - LunarDay.get_lunar_month() -> LunarMonth
   - LunarMonth.get_lunar_year() -> LunarYear
   - LunarYear.get_sixty_cycle() -> SixtyCycle
   - SixtyCycle.get_heaven_stem() -> TianGan
   - SixtyCycle.get_earth_branch() -> DiZhi
   - SolarTerm.from_index(year, index) -> SolarTerm
   - SolarTerm.get_julian_day() -> JulianDay
   - JulianDay.get_solar_time() -> SolarTime
   - SolarTime.next(days) -> SolarTime
   - SolarTime.get_lunar_hour() -> LunarHour
   - LunarHour.get_eight_char() -> EightChar
   - EightChar.get_month() -> SixtyCycle
   - ChildLimit.from_solar_time(solar_time, gender) -> ChildLimit
   - ChildLimit.get_start_age() -> int
   - ChildLimit.get_year_count() -> int
   - ChildLimit.get_month_count() -> int
   - ChildLimit.get_day_count() -> int
   - ChildLimit.get_hour_count() -> int
   - ChildLimit.get_minute_count() -> int
   - ChildLimit.get_start_time() -> SolarTime
   - ChildLimit.get_end_time() -> SolarTime
   - DecadeFortune.from_child_limit(child_limit, index) -> DecadeFortune
   - Fortune.from_child_limit(child_limit, index) -> Fortune
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

# Placeholder imports - replace with actual implementations
try:
    from bazi_base import Pillar, BaZi
except ImportError:
    class Pillar:
        def __init__(self, stem: str = "", branch: str = ""):
            self._stem = stem
            self._branch = branch
        
        def stem(self) -> str:
            return self._stem
        
        def branch(self) -> str:
            return self._branch
        
        def to_string(self) -> str:
            return f"{self._stem}{self._branch}"
    
    class BaZi:
        @staticmethod
        def from_solar(year, month, day, hour):
            # Placeholder - should return BaZi object
            return BaZi()

try:
    from ganzhi import (
        TianGan, DiZhi, ShiShen, YinYang,
        get_shi_shen, shi_shen_to_zh, get_cang_gan, get_yin_yang
    )
except ImportError:
    class TianGan:
        pass
    
    class DiZhi:
        pass
    
    class ShiShen:
        pass
    
    class YinYang(Enum):
        Yang = 1
        Yin = 2
    
    def get_shi_shen(day_gan, gan):
        return ShiShen()
    
    def shi_shen_to_zh(shi_shen) -> str:
        return ""
    
    def get_cang_gan(zhi) -> List:
        return []
    
    def get_yin_yang(gan) -> YinYang:
        return YinYang.Yang

try:
    import tyme
except ImportError:
    # Placeholder tyme module
    class tyme:
        class Gender(Enum):
            MAN = 1
            WOMAN = 2
        
        class SolarTime:
            @staticmethod
            def from_ymd_hms(year, month, day, hour, minute, second):
                return tyme.SolarTime()
            
            def next(self, days):
                return self
            
            def get_month(self):
                return 1
            
            def get_day(self):
                return 1
            
            def get_lunar_hour(self):
                return tyme.LunarHour()
        
        class SolarDay:
            @staticmethod
            def from_ymd(year, month, day):
                return tyme.SolarDay()
            
            def get_lunar_day(self):
                return tyme.LunarDay()
        
        class LunarDay:
            def get_lunar_month(self):
                return tyme.LunarMonth()
        
        class LunarMonth:
            def get_lunar_year(self):
                return tyme.LunarYear()
        
        class LunarYear:
            def get_sixty_cycle(self):
                return tyme.SixtyCycle()
        
        class SixtyCycle:
            def get_heaven_stem(self):
                return tyme.TianGan()
            
            def get_earth_branch(self):
                return tyme.DiZhi()
            
            def get_name(self) -> str:
                return ""
        
        class TianGan:
            def get_name(self) -> str:
                return ""
        
        class DiZhi:
            def get_name(self) -> str:
                return ""
        
        class SolarTerm:
            @staticmethod
            def from_index(year, index):
                return tyme.SolarTerm()
            
            def get_julian_day(self):
                return tyme.JulianDay()
        
        class JulianDay:
            def get_solar_time(self):
                return tyme.SolarTime()
        
        class LunarHour:
            def get_eight_char(self):
                return tyme.EightChar()
        
        class EightChar:
            def get_month(self):
                return tyme.SixtyCycle()
        
        class ChildLimit:
            @staticmethod
            def from_solar_time(solar_time, gender):
                return tyme.ChildLimit()
            
            def get_start_age(self):
                return 0
            
            def get_year_count(self):
                return 0
            
            def get_month_count(self):
                return 0
            
            def get_day_count(self):
                return 0
            
            def get_hour_count(self):
                return 0
            
            def get_minute_count(self):
                return 0
            
            def get_start_time(self):
                return tyme.SolarTime()
            
            def get_end_time(self):
                return tyme.SolarTime()
        
        class DecadeFortune:
            @staticmethod
            def from_child_limit(child_limit, index):
                return tyme.DecadeFortune()
        
        class Fortune:
            @staticmethod
            def from_child_limit(child_limit, index):
                return tyme.Fortune()


@dataclass
class DaYun:
    """大运信息 - 每个大运10年，从某个年龄开始"""
    pillar: Pillar
    start_age: int  # 起运年龄
    end_age: int  # 结束年龄（start_age + 9）
    start_year: int  # 起始公历年份
    end_year: int  # 结束公历年份
    gan_shi_shen: ShiShen  # 天干十神
    zhi_shi_shen: ShiShen  # 地支十神（地支藏干主气）
    
    def __init__(self, pillar: Pillar, age: int, year_start: int, day_gan: TianGan):
        self.pillar = pillar
        self.start_age = age
        self.end_age = age + 9
        self.start_year = year_start
        self.end_year = year_start + 9
        self.gan_shi_shen = get_shi_shen(day_gan, pillar.stem() if hasattr(pillar, 'stem') else pillar._stem)
        # 地支藏干取主气计算十神
        branch = pillar.branch() if hasattr(pillar, 'branch') else pillar._branch
        cang_gan = get_cang_gan(branch)
        if cang_gan:
            self.zhi_shi_shen = get_shi_shen(day_gan, cang_gan[0])
        else:
            self.zhi_shi_shen = get_shi_shen(day_gan, day_gan)  # Fallback
    
    def contains_age(self, age: int) -> bool:
        """判断某个年龄是否在此大运范围内"""
        return self.start_age <= age <= self.end_age
    
    def to_string(self) -> str:
        """转换为字符串"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return f"{pillar_str}({self.start_age}-{self.end_age}岁 {self.start_year}-{self.end_year}年)"
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return {
            "pillar": pillar_str,
            "start_age": self.start_age,
            "end_age": self.end_age,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "gan_shi_shen": shi_shen_to_zh(self.gan_shi_shen),
            "zhi_shi_shen": shi_shen_to_zh(self.zhi_shi_shen)
        }


class DaYunSystem:
    """大运系统 - 管理一个人一生的大运，使用 tyme 库计算起运年龄"""
    
    def __init__(self, bazi: BaZi, is_male: bool, birth_year: int, birth_month: int, 
                 birth_day: int, birth_hour: int = 12, birth_minute: int = 0, birth_second: int = 0):
        """
        构造函数
        
        Args:
            bazi: 八字
            is_male: 是否为男性
            birth_year: 出生年份
            birth_month: 出生月份
            birth_day: 出生日
            birth_hour: 出生时辰（默认12）
            birth_minute: 出生分钟（默认0）
            birth_second: 出生秒（默认0）
        """
        self.child_limit_ = self._create_child_limit(
            birth_year, birth_month, birth_day, birth_hour, birth_minute, birth_second, is_male
        )
        self.birth_year_ = birth_year
        
        # 判断年柱天干阴阳（阳年为阳，阴年为阴）
        year_gan = bazi.year.stem() if hasattr(bazi.year, 'stem') else bazi.year._stem
        yang_year = (get_yin_yang(year_gan) == YinYang.Yang)
        
        # 阳男阴女顺排，阴男阳女逆排
        self.shun_pai_ = (is_male == yang_year)
        
        # 计算实际起运年龄（周岁）= 起运年份 - 出生年份
        qi_yun_year = self.child_limit_.get_end_time().get_year() if hasattr(self.child_limit_.get_end_time(), 'get_year') else birth_year
        self.qi_yun_age_ = qi_yun_year - birth_year
        
        # 生成大运列表（一般排10个大运，100年）
        self.da_yun_list_ = self._generate_da_yun_list(bazi, 10, birth_year)
    
    def get_da_yun_list(self) -> List[DaYun]:
        """获取大运列表"""
        return self.da_yun_list_
    
    def get_qi_yun_age(self) -> int:
        """获取起运年龄"""
        return self.qi_yun_age_
    
    def get_da_yun_by_age(self, age: int) -> Optional[DaYun]:
        """根据年龄获取当前大运"""
        for dy in self.da_yun_list_:
            if dy.contains_age(age):
                return dy
        return None
    
    def is_shun_pai(self) -> bool:
        """是否顺排"""
        return self.shun_pai_
    
    def get_child_limit(self):
        """获取童限對象（用于访问 tyme 库的详细信息）"""
        return self.child_limit_
    
    @dataclass
    class ChildLimitDetail:
        """童限详细信息"""
        start_age: int  # 起运年龄（虚岁）
        year_count: int  # 年数
        month_count: int  # 月数
        day_count: int  # 日数
        hour_count: int  # 小时数
        minute_count: int  # 分钟数
        start_time: 'tyme.SolarTime'  # 出生时刻
        end_time: 'tyme.SolarTime'  # 起运时刻
    
    def get_child_limit_detail(self) -> ChildLimitDetail:
        """获取童限详细信息"""
        return self.ChildLimitDetail(
            self.child_limit_.get_start_age(),
            self.child_limit_.get_year_count(),
            self.child_limit_.get_month_count(),
            self.child_limit_.get_day_count(),
            self.child_limit_.get_hour_count(),
            self.child_limit_.get_minute_count(),
            self.child_limit_.get_start_time(),
            self.child_limit_.get_end_time()
        )
    
    def get_tyme_decade_fortune(self, index: int):
        """从 tyme 库获取指定索引的大运"""
        return tyme.DecadeFortune.from_child_limit(self.child_limit_, index)
    
    def get_all_tyme_decade_fortunes(self, count: int = 10) -> List:
        """获取所有大运的 tyme 對象列表"""
        fortunes = []
        for i in range(count):
            fortunes.append(tyme.DecadeFortune.from_child_limit(self.child_limit_, i))
        return fortunes
    
    @staticmethod
    def _create_child_limit(year: int, month: int, day: int, hour: int, minute: int, 
                            second: int, is_male: bool):
        """创建童限對象"""
        # 创建公历時間對象
        solar_time = tyme.SolarTime.from_ymd_hms(year, month, day, hour, minute, second)
        
        # 创建性别對象
        gender = tyme.Gender.MAN if is_male else tyme.Gender.WOMAN
        
        # 使用 tyme 库计算童限（包含起运年龄）
        return tyme.ChildLimit.from_solar_time(solar_time, gender)
    
    def _generate_da_yun_list(self, bazi: BaZi, count: int, birth_year: int) -> List[DaYun]:
        """生成大运列表"""
        da_yun_list = []
        
        # 从月柱开始推算
        month_gan = bazi.month.stem() if hasattr(bazi.month, 'stem') else bazi.month._stem
        month_zhi = bazi.month.branch() if hasattr(bazi.month, 'branch') else bazi.month._branch
        
        # 从童限获取实际起运年份
        end_time = self.child_limit_.get_end_time()
        qi_yun_year = end_time.get_year() if hasattr(end_time, 'get_year') else birth_year
        
        # 计算实际起运年龄（周岁）
        current_age = qi_yun_year - birth_year
        current_year = qi_yun_year
        
        # 获取日干
        day_gan = bazi.day.stem() if hasattr(bazi.day, 'stem') else bazi.day._stem
        
        # 转换为枚举类型（如果使用枚举）
        try:
            if isinstance(month_gan, str):
                # 假设有映射函数将字符串转换为枚举
                current_gan = month_gan
            else:
                current_gan = month_gan
            
            if isinstance(month_zhi, str):
                current_zhi = month_zhi
            else:
                current_zhi = month_zhi
        except:
            current_gan = month_gan
            current_zhi = month_zhi
        
        for i in range(count):
            # 前进或后退一柱
            if self.shun_pai_:
                # 顺排：干支都加1
                if isinstance(current_gan, int):
                    current_gan = (current_gan + 1) % 10
                else:
                    # 字符串处理 - 需要天干列表
                    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
                    try:
                        idx = gan_list.index(current_gan)
                        current_gan = gan_list[(idx + 1) % 10]
                    except:
                        pass
                
                if isinstance(current_zhi, int):
                    current_zhi = (current_zhi + 1) % 12
                else:
                    # 字符串处理 - 需要地支列表
                    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
                    try:
                        idx = zhi_list.index(current_zhi)
                        current_zhi = zhi_list[(idx + 1) % 12]
                    except:
                        pass
            else:
                # 逆排：干支都减1
                if isinstance(current_gan, int):
                    current_gan = (current_gan + 9) % 10
                else:
                    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
                    try:
                        idx = gan_list.index(current_gan)
                        current_gan = gan_list[(idx + 9) % 10]
                    except:
                        pass
                
                if isinstance(current_zhi, int):
                    current_zhi = (current_zhi + 11) % 12
                else:
                    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
                    try:
                        idx = zhi_list.index(current_zhi)
                        current_zhi = zhi_list[(idx + 11) % 12]
                    except:
                        pass
            
            # 创建大运干支
            da_yun_pillar = Pillar(current_gan, current_zhi)
            da_yun_list.append(DaYun(da_yun_pillar, current_age, current_year, day_gan))
            
            current_age += 10
            current_year += 10
        
        return da_yun_list


@dataclass
class LiuNian:
    """流年信息"""
    year: int  # 公历年份
    pillar: Pillar  # 流年干支
    age: int  # 虚岁年龄
    gan_shi_shen: ShiShen  # 天干十神
    zhi_shi_shen: ShiShen  # 地支十神
    
    def __init__(self, year: int, pillar: Pillar, age: int, day_gan: TianGan):
        self.year = year
        self.pillar = pillar
        self.age = age
        stem = pillar.stem() if hasattr(pillar, 'stem') else pillar._stem
        self.gan_shi_shen = get_shi_shen(day_gan, stem)
        branch = pillar.branch() if hasattr(pillar, 'branch') else pillar._branch
        cang_gan = get_cang_gan(branch)
        if cang_gan:
            self.zhi_shi_shen = get_shi_shen(day_gan, cang_gan[0])
        else:
            self.zhi_shi_shen = get_shi_shen(day_gan, day_gan)  # Fallback
    
    def to_string(self) -> str:
        """转换为字符串"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return f"{self.year}年 {pillar_str} ({self.age}岁)"
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return {
            "year": self.year,
            "pillar": pillar_str,
            "age": self.age,
            "gan_shi_shen": shi_shen_to_zh(self.gan_shi_shen),
            "zhi_shi_shen": shi_shen_to_zh(self.zhi_shi_shen)
        }


def create_liu_nian(year: int, birth_year: int, day_gan: TianGan) -> LiuNian:
    """创建流年
    
    Args:
        year: 公历年份
        birth_year: 出生年份
        day_gan: 日干
    
    Returns:
        LiuNian 流年對象
    """
    # 从年份获取干支
    # 使用年中的日期（7月1日）以确保获取正确的农历年干支
    solar_day = tyme.SolarDay.from_ymd(year, 7, 1)
    lunar_day = solar_day.get_lunar_day()
    lunar_year = lunar_day.get_lunar_month().get_lunar_year()
    year_cycle = lunar_year.get_sixty_cycle()
    
    # 转换为 Pillar
    gan_name = year_cycle.get_heaven_stem().get_name()
    zhi_name = year_cycle.get_earth_branch().get_name()
    year_pillar = Pillar(gan_name, zhi_name)
    
    # 计算虚岁
    age = year - birth_year + 1
    
    return LiuNian(year, year_pillar, age, day_gan)


@dataclass
class LiuYue:
    """流月信息（节气月）"""
    lunar_month_index: int  # 农历月序号（1-12，对應寅月到丑月）
    pillar: Pillar  # 流月干支
    gan_shi_shen: ShiShen  # 天干十神
    zhi_shi_shen: ShiShen  # 地支十神
    start_date: str  # 起始日期（公历）
    end_date: str  # 结束日期（公历）
    
    def __init__(self, index: int, pillar: Pillar, day_gan: TianGan, 
                 start: str, end: str = ""):
        self.lunar_month_index = index
        self.pillar = pillar
        self.start_date = start
        self.end_date = end
        stem = pillar.stem() if hasattr(pillar, 'stem') else pillar._stem
        self.gan_shi_shen = get_shi_shen(day_gan, stem)
        branch = pillar.branch() if hasattr(pillar, 'branch') else pillar._branch
        cang_gan = get_cang_gan(branch)
        if cang_gan:
            self.zhi_shi_shen = get_shi_shen(day_gan, cang_gan[0])
        else:
            self.zhi_shi_shen = get_shi_shen(day_gan, day_gan)  # Fallback
    
    def to_string(self) -> str:
        """转换为字符串"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return f"{self.lunar_month_index}月 {pillar_str} ({self.start_date})"
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return {
            "lunar_month_index": self.lunar_month_index,
            "pillar": pillar_str,
            "start_date": self.start_date,
            "gan_shi_shen": shi_shen_to_zh(self.gan_shi_shen),
            "zhi_shi_shen": shi_shen_to_zh(self.zhi_shi_shen)
        }


def get_liu_yue_of_year(year: int, day_gan: TianGan) -> List[LiuYue]:
    """获取某年的所有节气月（流月）
    
    节气月从立春开始，按照十二地支顺序：
    正月（寅月）：立春开始
    二月（卯月）：惊蛰开始
    三月（辰月）：清明开始
    四月（巳月）：立夏开始
    五月（午月）：芒种开始
    六月（未月）：小暑开始
    七月（申月）：立秋开始
    八月（酉月）：白露开始
    九月（戌月）：寒露开始
    十月（亥月）：立冬开始
    十一月（子月）：大雪开始
    十二月（丑月）：小寒开始
    """
    result = []
    
    # 节气索引（tyme库中的24节气索引，0=冬至）
    # 寅月从立春开始（索引3），每个月相差2（节+气）
    jie_qi_indices = [
        3,   # 寅月（正月）：立春（索引3）
        5,   # 卯月（二月）：惊蛰（索引5）
        7,   # 辰月（三月）：清明（索引7）
        9,   # 巳月（四月）：立夏（索引9）
        11,  # 午月（五月）：芒种（索引11）
        13,  # 未月（六月）：小暑（索引13）
        15,  # 申月（七月）：立秋（索引15）
        17,  # 酉月（八月）：白露（索引17）
        19,  # 戌月（九月）：寒露（索引19）
        21,  # 亥月（十月）：立冬（索引21）
        23,  # 子月（十一月）：大雪（索引23）
        1    # 丑月（十二月）：小寒（索引1，需要用下一年）
    ]
    
    for i in range(12):
        term_index = jie_qi_indices[i]
        term_year = year
        
        # 丑月的小寒在下一年1月
        if i == 11:
            term_year = year + 1
        
        # 获取节气
        solar_term = tyme.SolarTerm.from_index(term_year, term_index)
        term_time = solar_term.get_julian_day().get_solar_time()
        
        # 使用节气后的某一天获取该月的八字月柱
        month_time = term_time.next(10)  # 节气后10天
        lunar_hour = month_time.get_lunar_hour()
        eight_char = lunar_hour.get_eight_char()
        month_cycle = eight_char.get_month()
        
        # 获取节气月的干支
        gan_name = month_cycle.get_heaven_stem().get_name()
        zhi_name = month_cycle.get_earth_branch().get_name()
        month_pillar = Pillar(gan_name, zhi_name)
        
        # 格式化起始日期（只显示起始，不显示结束）
        month = term_time.get_month() if hasattr(term_time, 'get_month') else 1
        day = term_time.get_day() if hasattr(term_time, 'get_day') else 1
        start_date = f"{month}月{day}日起"
        
        result.append(LiuYue(i + 1, month_pillar, day_gan, start_date, ""))
    
    return result


@dataclass
class LiuRi:
    """流日信息"""
    year: int  # 公历年份
    month: int  # 公历月份
    day: int  # 公历日
    pillar: Pillar  # 流日干支
    gan_shi_shen: ShiShen  # 天干十神
    zhi_shi_shen: ShiShen  # 地支十神
    
    def __init__(self, year: int, month: int, day: int, pillar: Pillar, day_gan: TianGan):
        self.year = year
        self.month = month
        self.day = day
        self.pillar = pillar
        stem = pillar.stem() if hasattr(pillar, 'stem') else pillar._stem
        self.gan_shi_shen = get_shi_shen(day_gan, stem)
        branch = pillar.branch() if hasattr(pillar, 'branch') else pillar._branch
        cang_gan = get_cang_gan(branch)
        if cang_gan:
            self.zhi_shi_shen = get_shi_shen(day_gan, cang_gan[0])
        else:
            self.zhi_shi_shen = get_shi_shen(day_gan, day_gan)  # Fallback
    
    def to_string(self) -> str:
        """转换为字符串"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return f"{self.year}年{self.month}月{self.day}日 {pillar_str}"
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "pillar": pillar_str,
            "gan_shi_shen": shi_shen_to_zh(self.gan_shi_shen),
            "zhi_shi_shen": shi_shen_to_zh(self.zhi_shi_shen)
        }


def create_liu_ri(year: int, month: int, day: int, day_gan: TianGan) -> LiuRi:
    """创建流日
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日
        day_gan: 日干
    
    Returns:
        LiuRi 流日對象
    """
    # 从年月日获取干支
    bazi = BaZi.from_solar(year, month, day, 12)
    
    return LiuRi(year, month, day, bazi.day, day_gan)


@dataclass
class LiuShi:
    """流时信息"""
    hour: int  # 时辰（0-23）
    pillar: Pillar  # 流时干支
    gan_shi_shen: ShiShen  # 天干十神
    zhi_shi_shen: ShiShen  # 地支十神
    
    def __init__(self, hour: int, pillar: Pillar, day_gan: TianGan):
        self.hour = hour
        self.pillar = pillar
        stem = pillar.stem() if hasattr(pillar, 'stem') else pillar._stem
        self.gan_shi_shen = get_shi_shen(day_gan, stem)
        branch = pillar.branch() if hasattr(pillar, 'branch') else pillar._branch
        cang_gan = get_cang_gan(branch)
        if cang_gan:
            self.zhi_shi_shen = get_shi_shen(day_gan, cang_gan[0])
        else:
            self.zhi_shi_shen = get_shi_shen(day_gan, day_gan)  # Fallback
    
    def to_string(self) -> str:
        """转换为字符串"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return f"{self.hour}时 {pillar_str}"
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        pillar_str = self.pillar.to_string() if hasattr(self.pillar, 'to_string') else str(self.pillar)
        return {
            "hour": self.hour,
            "pillar": pillar_str,
            "gan_shi_shen": shi_shen_to_zh(self.gan_shi_shen),
            "zhi_shi_shen": shi_shen_to_zh(self.zhi_shi_shen)
        }


def create_liu_shi(year: int, month: int, day: int, hour: int, day_gan: TianGan) -> LiuShi:
    """创建流时
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日
        hour: 时辰
        day_gan: 日干
    
    Returns:
        LiuShi 流时對象
    """
    # 从年月日时获取干支
    bazi = BaZi.from_solar(year, month, day, hour)
    
    return LiuShi(hour, bazi.hour, day_gan)


@dataclass
class BaZiResult:
    """完整八字排盘结果 - 包含八字、大运、流年等所有信息"""
    ba_zi: BaZi  # 四柱八字
    is_male: bool  # 性别
    birth_year: int  # 出生年份
    birth_month: int  # 出生月份
    birth_day: int  # 出生日
    birth_hour: int  # 出生时辰
    birth_minute: int  # 出生分钟
    birth_second: int  # 出生秒
    da_yun_system: DaYunSystem  # 大运系统
    
    def __init__(self, bazi: BaZi, is_male: bool, birth_year: int, birth_month: int, 
                 birth_day: int, birth_hour: int, birth_minute: int = 0, birth_second: int = 0):
        self.ba_zi = bazi
        self.is_male = is_male
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.birth_hour = birth_hour
        self.birth_minute = birth_minute
        self.birth_second = birth_second
        self.da_yun_system = DaYunSystem(
            bazi, is_male, birth_year, birth_month, birth_day, 
            birth_hour, birth_minute, birth_second
        )
    
    def get_liu_nian(self, year: int) -> LiuNian:
        """获取指定年份的流年"""
        day_gan = self.ba_zi.day.stem() if hasattr(self.ba_zi.day, 'stem') else self.ba_zi.day._stem
        return create_liu_nian(year, self.birth_year, day_gan)
    
    def get_liu_yue_list(self, year: int) -> List[LiuYue]:
        """获取指定年份的所有流月（节气月）"""
        day_gan = self.ba_zi.day.stem() if hasattr(self.ba_zi.day, 'stem') else self.ba_zi.day._stem
        return get_liu_yue_of_year(year, day_gan)
    
    def get_liu_ri(self, year: int, month: int, day: int) -> LiuRi:
        """获取指定日期的流日"""
        day_gan = self.ba_zi.day.stem() if hasattr(self.ba_zi.day, 'stem') else self.ba_zi.day._stem
        return create_liu_ri(year, month, day, day_gan)
    
    def get_liu_shi(self, year: int, month: int, day: int, hour: int) -> LiuShi:
        """获取指定时辰的流时"""
        day_gan = self.ba_zi.day.stem() if hasattr(self.ba_zi.day, 'stem') else self.ba_zi.day._stem
        return create_liu_shi(year, month, day, hour, day_gan)
    
    def get_current_da_yun(self, age: int) -> Optional[DaYun]:
        """获取当前年龄的大运"""
        return self.da_yun_system.get_da_yun_by_age(age)
    
    def get_child_limit_detail(self) -> DaYunSystem.ChildLimitDetail:
        """获取童限详细信息"""
        return self.da_yun_system.get_child_limit_detail()
    
    def get_tyme_decade_fortune(self, index: int):
        """获取 tyme 库的大运對象"""
        return self.da_yun_system.get_tyme_decade_fortune(index)
    
    def get_all_tyme_decade_fortunes(self, count: int = 10) -> List:
        """获取所有 tyme 库的大运對象"""
        return self.da_yun_system.get_all_tyme_decade_fortunes(count)
    
    def get_tyme_fortune(self, index: int):
        """获取 tyme 库的小运對象"""
        return tyme.Fortune.from_child_limit(self.da_yun_system.get_child_limit(), index)
    
    def get_si_zhu_shi_shen(self) -> List[ShiShen]:
        """获取四柱十神"""
        day_gan = self.ba_zi.day.stem() if hasattr(self.ba_zi.day, 'stem') else self.ba_zi.day._stem
        year_gan = self.ba_zi.year.stem() if hasattr(self.ba_zi.year, 'stem') else self.ba_zi.year._stem
        month_gan = self.ba_zi.month.stem() if hasattr(self.ba_zi.month, 'stem') else self.ba_zi.month._stem
        hour_gan = self.ba_zi.hour.stem() if hasattr(self.ba_zi.hour, 'stem') else self.ba_zi.hour._stem
        
        return [
            get_shi_shen(day_gan, year_gan),
            get_shi_shen(day_gan, month_gan),
            get_shi_shen(day_gan, day_gan),  # 日干比肩
            get_shi_shen(day_gan, hour_gan)
        ]
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        # 转换八字
        ba_zi_dict = {}
        if hasattr(self.ba_zi, 'to_dict'):
            ba_zi_dict = self.ba_zi.to_dict()
        else:
            ba_zi_dict = {
                "year": self.ba_zi.year.to_string() if hasattr(self.ba_zi.year, 'to_string') else str(self.ba_zi.year),
                "month": self.ba_zi.month.to_string() if hasattr(self.ba_zi.month, 'to_string') else str(self.ba_zi.month),
                "day": self.ba_zi.day.to_string() if hasattr(self.ba_zi.day, 'to_string') else str(self.ba_zi.day),
                "hour": self.ba_zi.hour.to_string() if hasattr(self.ba_zi.hour, 'to_string') else str(self.ba_zi.hour),
            }
        
        # 大运
        da_yun_list = [dy.to_dict() for dy in self.da_yun_system.get_da_yun_list()]
        
        # 十神
        shi_shen_arr = self.get_si_zhu_shi_shen()
        
        return {
            "ba_zi": ba_zi_dict,
            "is_male": self.is_male,
            "birth_date": {
                "year": self.birth_year,
                "month": self.birth_month,
                "day": self.birth_day,
                "hour": self.birth_hour
            },
            "da_yun": {
                "qi_yun_age": self.da_yun_system.get_qi_yun_age(),
                "shun_pai": self.da_yun_system.is_shun_pai(),
                "list": da_yun_list
            },
            "shi_shen": {
                "year": shi_shen_to_zh(shi_shen_arr[0]),
                "month": shi_shen_to_zh(shi_shen_arr[1]),
                "day": shi_shen_to_zh(shi_shen_arr[2]),
                "hour": shi_shen_to_zh(shi_shen_arr[3])
            }
        }

