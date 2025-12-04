"""
Python version of 八字基础数据结构 (BaZi Base Data Structures)
Converted from C++23 module ba_zi_base.cppm

Provides basic data structures for Gan-Zhi pillars and BaZi (Four Pillars).
"""

from dataclasses import dataclass
from typing import Optional, Tuple


class Pillar:
    """
    干支柱结构体（Gan-Zhi Pillar）
    
    表示一个天干地支的组合（如"甲子"）
    """
    
    def __init__(self, stem: str = "甲", branch: str = "子"):
        """
        构造函数
        
        Args:
            stem: 天干字符串（如 "甲"）
            branch: 地支字符串（如 "子"）
        """
        # 验证天干
        valid_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        if stem not in valid_stems:
            raise ValueError(f"無效的天干: {stem}")
        
        # 验证地支
        valid_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        if branch not in valid_branches:
            raise ValueError(f"無效的地支: {branch}")
        
        self._stem = stem
        self._branch = branch
    
    def stem(self) -> str:
        """
        获取天干字符串
        @return 如 "甲"
        """
        return self._stem
    
    def branch(self) -> str:
        """
        获取地支字符串
        @return 如 "子"
        """
        return self._branch
    
    def to_string(self) -> str:
        """
        转换为完整字符串
        @return 如 "甲子"
        """
        return f"{self._stem}{self._branch}"
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"Pillar('{self._stem}', '{self._branch}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Pillar):
            return False
        return self._stem == other._stem and self._branch == other._branch
    
    def __hash__(self) -> int:
        return hash((self._stem, self._branch))


@dataclass
class BaZi:
    """
    四柱八字结构体 (Four Pillars of BaZi)
    
    表示一个完整的四柱八字信息（年月日时）
    """
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    xun_kong_1: str = ""  # 旬空地支1
    xun_kong_2: str = ""  # 旬空地支2
    
    def __init__(self, year: Pillar, month: Pillar, day: Pillar, hour: Pillar,
                 xun_kong_1: str = "", xun_kong_2: str = ""):
        """
        完整构造函数
        
        Args:
            year: 年柱
            month: 月柱
            day: 日柱
            hour: 时柱
            xun_kong_1: 旬空地支1
            xun_kong_2: 旬空地支2
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.xun_kong_1 = xun_kong_1
        self.xun_kong_2 = xun_kong_2
    
    def __str__(self) -> str:
        return (f"年柱: {self.year}\n"
                f"月柱: {self.month}\n"
                f"日柱: {self.day}\n"
                f"时柱: {self.hour}\n"
                f"旬空: {self.xun_kong_1}{self.xun_kong_2}")
    
    def __repr__(self) -> str:
        return (f"BaZi(year={self.year!r}, month={self.month!r}, "
                f"day={self.day!r}, hour={self.hour!r}, "
                f"xun_kong_1='{self.xun_kong_1}', xun_kong_2='{self.xun_kong_2}')")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BaZi):
            return False
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day and
                self.hour == other.hour and
                self.xun_kong_1 == other.xun_kong_1 and
                self.xun_kong_2 == other.xun_kong_2)
    
    @staticmethod
    def from_solar(year: int, month: int, day: int, hour: int, 
                   minute: int = 0, second: int = 0) -> 'BaZi':
        """
        从公历日期時間创建八字
        
        Args:
            year: 公历年（如 2024）
            month: 公历月（1-12）
            day: 公历日（1-31）
            hour: 公历时（0-23）
            minute: 公历分（0-59，默认0）
            second: 公历秒（0-59，默认0）
        
        Returns:
            八字對象（包含旬空信息）
        
        Note:
            此方法需要农历時間库支持。如果库不可用，将抛出 NotImplementedError。
        """
        try:
            # Try to import lunar_python library
            from lunar_python import Solar
            
            # Create solar date
            solar = Solar.fromYmdHms(year, month, day, hour, minute, second)
            
            # Convert to lunar date
            lunar = solar.getLunar()
            
            # Get EightChar (八字) object
            eight_char = lunar.getEightChar()
            
            # Get GanZhi (干支) strings for each pillar
            # Try different API methods depending on library version
            try:
                # Method 1: Direct GanZhi string methods (if available)
                year_gz = lunar.getYearInGanZhi()
                month_gz = lunar.getMonthInGanZhi()
                day_gz = lunar.getDayInGanZhi()
                time_gz = lunar.getTimeInGanZhi()
            except AttributeError:
                # Method 2: Use EightChar object methods
                year_gz = eight_char.getYear()
                month_gz = eight_char.getMonth()
                day_gz = eight_char.getDay()
                time_gz = eight_char.getTime()
                
                # If these return objects, convert to strings
                if hasattr(year_gz, 'toString'):
                    year_gz = year_gz.toString()
                    month_gz = month_gz.toString()
                    day_gz = day_gz.toString()
                    time_gz = time_gz.toString()
                elif hasattr(year_gz, '__str__'):
                    year_gz = str(year_gz)
                    month_gz = str(month_gz)
                    day_gz = str(day_gz)
                    time_gz = str(time_gz)
            
            # Parse GanZhi strings to get stem and branch
            year_pillar = BaZi._parse_ganzhi_string(year_gz)
            month_pillar = BaZi._parse_ganzhi_string(month_gz)
            day_pillar = BaZi._parse_ganzhi_string(day_gz)
            hour_pillar = BaZi._parse_ganzhi_string(time_gz)
            
            # Calculate xun kong (旬空) based on day pillar
            try:
                xun_kong = lunar.getDayXunKong()
                if isinstance(xun_kong, (list, tuple)):
                    xk1 = xun_kong[0] if len(xun_kong) > 0 else ""
                    xk2 = xun_kong[1] if len(xun_kong) > 1 else ""
                else:
                    # If it's a string, try to parse it
                    xun_kong_str = str(xun_kong)
                    xk1 = xun_kong_str[0] if len(xun_kong_str) > 0 else ""
                    xk2 = xun_kong_str[1] if len(xun_kong_str) > 1 else ""
            except (AttributeError, IndexError):
                # If xun kong calculation is not available, leave empty
                xk1 = ""
                xk2 = ""
            
            return BaZi(year_pillar, month_pillar, day_pillar, hour_pillar, xk1, xk2)
        except ImportError:
            raise NotImplementedError(
                "BaZi.from_solar() requires the 'lunar_python' library for lunar calendar conversion. "
                "Please install it with: pip install lunar_python"
            )
        except Exception as e:
            # Handle any other errors
            raise NotImplementedError(
                f"BaZi.from_solar() encountered an error with lunar_python library: {e}. "
                "Please ensure you have the latest version: pip install --upgrade lunar_python"
            )
    
    @staticmethod
    def from_lunar(year: int, month: int, day: int, hour: int,
                   minute: int = 0, second: int = 0) -> 'BaZi':
        """
        从农历日期時間创建八字
        
        Args:
            year: 农历年
            month: 农历月（1-12，负数表示闰月）
            day: 农历日（1-30）
            hour: 时辰（0-23）
            minute: 分钟（0-59，默认0）
            second: 秒（0-59，默认0）
        
        Returns:
            八字對象（包含旬空信息）
        
        Note:
            此方法需要农历時間库支持。如果库不可用，将抛出 NotImplementedError。
        """
        try:
            from lunar_python import Lunar
            
            # Create lunar date (month can be negative for leap months)
            lunar = Lunar.fromYmdHms(year, month, day, hour, minute, second)
            
            # Get EightChar (八字) object
            eight_char = lunar.getEightChar()
            
            # Get GanZhi (干支) strings for each pillar
            try:
                # Method 1: Direct GanZhi string methods (if available)
                year_gz = lunar.getYearInGanZhi()
                month_gz = lunar.getMonthInGanZhi()
                day_gz = lunar.getDayInGanZhi()
                time_gz = lunar.getTimeInGanZhi()
            except AttributeError:
                # Method 2: Use EightChar object methods
                year_gz = eight_char.getYear()
                month_gz = eight_char.getMonth()
                day_gz = eight_char.getDay()
                time_gz = eight_char.getTime()
                
                # If these return objects, convert to strings
                if hasattr(year_gz, 'toString'):
                    year_gz = year_gz.toString()
                    month_gz = month_gz.toString()
                    day_gz = day_gz.toString()
                    time_gz = time_gz.toString()
                elif hasattr(year_gz, '__str__'):
                    year_gz = str(year_gz)
                    month_gz = str(month_gz)
                    day_gz = str(day_gz)
                    time_gz = str(time_gz)
            
            # Parse GanZhi strings to get stem and branch
            year_pillar = BaZi._parse_ganzhi_string(year_gz)
            month_pillar = BaZi._parse_ganzhi_string(month_gz)
            day_pillar = BaZi._parse_ganzhi_string(day_gz)
            hour_pillar = BaZi._parse_ganzhi_string(time_gz)
            
            # Calculate xun kong (旬空)
            try:
                xun_kong = lunar.getDayXunKong()
                if isinstance(xun_kong, (list, tuple)):
                    xk1 = xun_kong[0] if len(xun_kong) > 0 else ""
                    xk2 = xun_kong[1] if len(xun_kong) > 1 else ""
                else:
                    xun_kong_str = str(xun_kong)
                    xk1 = xun_kong_str[0] if len(xun_kong_str) > 0 else ""
                    xk2 = xun_kong_str[1] if len(xun_kong_str) > 1 else ""
            except (AttributeError, IndexError):
                xk1 = ""
                xk2 = ""
            
            return BaZi(year_pillar, month_pillar, day_pillar, hour_pillar, xk1, xk2)
        except ImportError:
            raise NotImplementedError(
                "BaZi.from_lunar() requires the 'lunar_python' library for lunar calendar conversion. "
                "Please install it with: pip install lunar_python"
            )
        except Exception as e:
            raise NotImplementedError(
                f"BaZi.from_lunar() encountered an error with lunar_python library: {e}. "
                "Please ensure you have the latest version: pip install --upgrade lunar_python"
            )
    
    @staticmethod
    def _parse_ganzhi_string(ganzhi_str: str) -> Pillar:
        """
        解析干支字符串为 Pillar 對象
        
        Args:
            ganzhi_str: 干支字符串，如 "甲子"、"乙丑" 等（2个字符）
        
        Returns:
            Pillar 干支柱對象
        """
        if len(ganzhi_str) != 2:
            raise ValueError(f"Invalid GanZhi string format: {ganzhi_str} (expected 2 characters)")
        
        gan = ganzhi_str[0]  # 天干
        zhi = ganzhi_str[1]  # 地支
        
        return Pillar(gan, zhi)
    
    @staticmethod
    def _convert_sixty_cycle_to_pillar(cycle) -> Pillar:
        """
        将 SixtyCycle 转换为 Pillar (保留用于向后兼容)
        
        Args:
            cycle: 六十甲子對象
        
        Returns:
            Pillar 干支柱對象
        """
        # Get gan and zhi names
        gan_name = cycle.get_heaven_stem().get_name()
        zhi_name = cycle.get_earth_branch().get_name()
        
        # Create Pillar from strings
        return Pillar(gan_name, zhi_name)
    
    @staticmethod
    def calculate_xun_kong(day_pillar: Pillar) -> Tuple[str, str]:
        """
        根据日柱计算旬空（空亡）
        
        旬空是根据日柱的天干地支来确定的。每个旬（10天）有两个空亡地支。
        旬空规律：
        - 甲子旬: 戌亥空
        - 甲戌旬: 申酉空
        - 甲申旬: 午未空
        - 甲午旬: 辰巳空
        - 甲辰旬: 寅卯空
        - 甲寅旬: 子丑空
        
        Args:
            day_pillar: 日柱（Pillar對象）
        
        Returns:
            Tuple[str, str]: (xun_kong_1, xun_kong_2) 两个空亡地支
        """
        # 天干地支序列
        stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        day_stem = day_pillar.stem()
        day_branch = day_pillar.branch()
        
        # 找到日柱在六十甲子中的位置
        stem_idx = stems.index(day_stem)
        branch_idx = branches.index(day_branch)
        
        # 计算日柱所在的旬首地支
        # 旬首是甲X，其中X是地支
        # 计算：从日柱往前推，找到最近的甲X
        # 如果日柱是甲X，则旬首就是甲X
        # 否则，需要找到对應的甲X
        # 公式：旬首地支 = (地支索引 - 天干索引) % 12
        xun_start_branch_idx = (branch_idx - stem_idx) % 12
        if xun_start_branch_idx < 0:
            xun_start_branch_idx += 12
        
        # 根据旬首地支确定空亡
        # 空亡地支 = 旬首地支 + 10, 旬首地支 + 11 (mod 12)
        kong1_idx = (xun_start_branch_idx + 10) % 12
        kong2_idx = (xun_start_branch_idx + 11) % 12
        
        return (branches[kong1_idx], branches[kong2_idx])

