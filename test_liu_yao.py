"""
Simple test code for liu_yao.py
Test case: 2025/11/25 19:00, hexagram changes from 111111 to 011111

Command-line Usage:
    # Using traditional format (老陽/陽/老陰/陰) - automatically extracts changing lines
    python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 老陽 陽 老陰 陰 陽 陽
    
    # Using legacy format (1/0/o/x) - automatically extracts changing lines
    python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 x 0 0 o 1
    
    # Using legacy format with no changing lines (all 1 or 0)
    python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 1 1 1 1 1
    
    # Using ganzi format for date
    python test_liu_yao.py --bazi 甲子 乙丑 丙寅 丁卯 --yao 老陽 陽 老陰 陰 陽 陽
    
    # Using ganzi format with legacy format
    python test_liu_yao.py --bazi 乙巳 丁亥 甲子 甲戌 --yao 1 1 1 1 1 1
    
    # Run example tests
    python test_liu_yao.py --examples

Python API Usage:
    # Method 1: Specify hexagram code directly
    test_custom_divination(
        year=2025, month=11, day=25, hour=19,
        hexagram_code="111111",  # 6 digits: '1'=yang, '0'=yin (bottom to top)
        changing_lines=[1]  # Which lines are changing
    )
    
    # Method 2: Specify each yao individually
    test_with_individual_yao(
        year=2025, month=11, day=25, hour=19,
        yao1="1", yao2="1", yao3="1", yao4="1", yao5="1", yao6="1",
        changing_lines=[1]
    )
    
    # Method 3: Provide manual BaZi
    from ba_zi_base import Pillar, BaZi
    bazi = BaZi(Pillar("乙", "巳"), Pillar("丁", "亥"), Pillar("甲", "子"), Pillar("甲", "戌"))
    test_custom_divination(
        hexagram_code="111111",
        changing_lines=[1],
        manual_bazi=bazi
    )
"""

from liu_yao import (
    six_yao_divination, 
    HEXAGRAM_MAP, 
    bazi_from_date_string,
    display_shen_sha_definitions
)
from ba_zi_base import Pillar, BaZi
from gradio_ui.utils.formatting import format_divination_results_pc
import json
import argparse
import sys
import io
from typing import List, Optional

# Note: format_divination_results_pc is now imported from gradio_ui.utils.formatting
# This ensures the function is shared between test_liu_yao.py and gradio_ui.py


def test_custom_divination(
    year: int = 2025,
    month: int = 11,
    day: int = 25,
    hour: int = 19,
    minute: int = 0,
    second: int = 0,
    hexagram_code: str = "111111",
    changing_lines: List[int] = [1],
    manual_bazi: Optional[BaZi] = None,
    show_shen_sha: bool = True
):
    """Test divination with custom date and hexagram configuration
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59), default 0
        second: Second (0-59), default 0
        hexagram_code: Hexagram code as 6-digit string (e.g., "111111" for 乾为天)
                      Each digit: '1' = yang (阳), '0' = yin (阴)
                      Position 1 = bottom line, Position 6 = top line
        changing_lines: List of line positions (1-6) that are changing
                       Empty list [] means no changing lines
        manual_bazi: Optional BaZi object to use instead of calculating from date
                     If provided, date parameters are ignored
    
    Example:
        # Test 2025/11/25 19:00, hexagram 111111 with line 1 changing
        test_custom_divination(
            year=2025, month=11, day=25, hour=19,
            hexagram_code="111111",
            changing_lines=[1]
        )
        
        # Test with all 6 yao specified: 101010 (from bottom to top)
        test_custom_divination(
            year=2025, month=1, day=1, hour=12,
            hexagram_code="101010",  # bottom: yin, 2nd: yang, 3rd: yin, etc.
            changing_lines=[2, 4]  # lines 2 and 4 are changing
        )
    """
    
    # Create BaZi object
    if manual_bazi is not None:
        bazi = manual_bazi
        print("Using provided manual BaZi")
    else:
        try:
            # Use bazi_from_date_string() which provides better error messages
            date_str = f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}"
            if second > 0:
                date_str += f":{second:02d}"
            bazi = bazi_from_date_string(date_str)
            print(f"Using bazi_from_date_string() for date: {date_str}")
        except (NotImplementedError, ValueError) as e:
            # bazi_from_date_string() will provide detailed error messages
            raise
    
    # Validate hexagram code
    if len(hexagram_code) != 6:
        raise ValueError(f"Hexagram code must be 6 digits, got: {hexagram_code}")
    if not all(c in '01' for c in hexagram_code):
        raise ValueError(f"Hexagram code must contain only '0' (yin) or '1' (yang), got: {hexagram_code}")
    
    # Validate changing lines
    for line in changing_lines:
        if not (1 <= line <= 6):
            raise ValueError(f"Changing line must be between 1 and 6, got: {line}")
    
    # Check if hexagram exists
    if hexagram_code not in HEXAGRAM_MAP:
        print(f"Warning: Hexagram code '{hexagram_code}' not found in HEXAGRAM_MAP")
        print("Available hexagrams:", list(HEXAGRAM_MAP.keys())[:10], "...")
    
    print("=" * 70)
    print("Custom Divination Test")
    print("=" * 70)
    print(f"Date: {year}/{month}/{day} {hour}:{minute}:{second}")
    print(f"BaZi: {bazi.year.to_string()} {bazi.month.to_string()} {bazi.day.to_string()} {bazi.hour.to_string()}")
    print(f"Hexagram code: {hexagram_code}")
    print(f"  (from bottom to top: {hexagram_code[0]} {hexagram_code[1]} {hexagram_code[2]} {hexagram_code[3]} {hexagram_code[4]} {hexagram_code[5]})")
    if hexagram_code in HEXAGRAM_MAP:
        print(f"  Name: {HEXAGRAM_MAP[hexagram_code].name}")
    print(f"Changing line(s): {changing_lines if changing_lines else 'None'}")
    print()
    
    # Call the divination function
    yao_list, result_json = six_yao_divination(hexagram_code, bazi, changing_lines)
    
    # Display results using the shared formatting function
    # Function now returns (with_prompt, without_prompt), use with_prompt for test output
    formatted_output, _ = format_divination_results_pc(bazi, result_json, yao_list, show_shen_sha=show_shen_sha)
    print(formatted_output, end='')  # end='' because the function already includes all newlines
    
    return yao_list, result_json


def test_with_individual_yao(
    year: int = 2025,
    month: int = 11,
    day: int = 25,
    hour: int = 19,
    yao1: str = "1",  # Bottom line (position 1)
    yao2: str = "1",  # Position 2
    yao3: str = "1",  # Position 3
    yao4: str = "1",  # Position 4
    yao5: str = "1",  # Position 5
    yao6: str = "1",  # Top line (position 6)
    changing_lines: List[int] = [1],
    manual_bazi: Optional[BaZi] = None
):
    """Test divination by specifying each yao individually
    
    Args:
        year, month, day, hour: Date/time parameters
        yao1-yao6: Each yao state: "1" for yang (阳), "0" for yin (阴)
                   yao1 = bottom line, yao6 = top line
        changing_lines: Which lines are changing (1-6)
        manual_bazi: Optional BaZi object
    
    Example:
        # Create hexagram with pattern: yin-yang-yin-yang-yin-yang (from bottom)
        test_with_individual_yao(
            year=2025, month=11, day=25, hour=19,
            yao1="0", yao2="1", yao3="0", yao4="1", yao5="0", yao6="1",
            changing_lines=[2, 4]
        )
    """
    hexagram_code = yao1 + yao2 + yao3 + yao4 + yao5 + yao6
    return test_custom_divination(
        year=year, month=month, day=day, hour=hour,
        hexagram_code=hexagram_code,
        changing_lines=changing_lines,
        manual_bazi=manual_bazi
    )


def test_hexagram_111111_to_011111():
    """Test hexagram transition from 111111 to 011111
    
    Test case: 2025/11/25 19:00
    Main hexagram: 111111 (乾为天)
    Changing line: position 1 (first line from bottom)
    Expected changed hexagram: 011111 (天风姤)
    """
    
    # Create BaZi object for 2025/11/25 19:00
    # For 2025/11/25 19:00, use manual BaZi values
    # Note: These are approximate values - for accurate BaZi, use BaZi.from_solar() with lunar_python library
    # 2025 is 乙巳年, November 2025 is around 亥月, 19:00 is 戌时
    try:
        # Try to use from_solar if available
        bazi = BaZi.from_solar(2025, 11, 25, 19, 0, 0)
        print("Using BaZi.from_solar() for accurate calculation")
    except (NotImplementedError, ImportError, AttributeError):
        # Use manual values for 2025/11/25 19:00
        # WARNING: These are approximate values. For accurate BaZi calculation, install lunar_python library
        # or provide correct BaZi values manually
        year_pillar = Pillar("乙", "巳")   # 2025 is 乙巳年
        month_pillar = Pillar("丁", "亥")  # November 2025 is 亥月 (丁亥)
        # Note: Day and hour pillars need proper calculation - these are placeholders
        # You should calculate the actual day pillar based on the specific date
        # and hour pillar based on the exact time
        day_pillar = Pillar("甲", "子")    # PLACEHOLDER - needs actual calculation
        hour_pillar = Pillar("甲", "戌")   # 19:00-21:00 is 戌时 (but stem needs calculation)
        bazi = BaZi(year_pillar, month_pillar, day_pillar, hour_pillar)
        print("WARNING: Using manual BaZi values (approximate)")
        print("         For accurate BaZi, install 'lunar_python' library or provide correct values manually")
    
    # Test: hexagram "111111" (乾为天) with line 1 changing
    # This should result in "011111" (天风姤)
    main_hexagram_code = "111111"
    changing_line_indices = [1]  # First line changes from yang (1) to yin (0)
    
    print("=" * 70)
    print("Test: Hexagram transition from 111111 to 011111")
    print("=" * 70)
    print(f"Date: 2025/11/25 19:00")
    print(f"BaZi: {bazi.year.to_string()} {bazi.month.to_string()} {bazi.day.to_string()} {bazi.hour.to_string()}")
    print(f"Main hexagram: {main_hexagram_code} ({HEXAGRAM_MAP[main_hexagram_code].name})")
    print(f"Changing line(s): {changing_line_indices}")
    print()
    
    # Call the divination function
    yao_list, result_json = six_yao_divination(main_hexagram_code, bazi, changing_line_indices)
    
    # Expected result: hexagram should be "011111"
    expected_changed_code = "011111"
    
    # Verify the result
    print("Results:")
    print("-" * 70)
    
    # Display detailed hexagram information
    ben_gua_name = result_json.get('ben_gua_name', 'N/A')
    print(f"本卦: {ben_gua_name}")
    if 'ben_gua_info' in result_json:
        info = result_json['ben_gua_info']
        print(f"  宫位: {info.get('palace', 'N/A')}宫")
        print(f"  五行: {info.get('five_element', 'N/A')}")
    
    if 'bian_gua_name' in result_json:
        bian_gua_name = result_json.get('bian_gua_name', 'N/A')
        print(f"變卦: {bian_gua_name}")
        if 'bian_gua_info' in result_json:
            info = result_json['bian_gua_info']
            print(f"  宫位: {info.get('palace', 'N/A')}宫")
            print(f"  五行: {info.get('five_element', 'N/A')}")
    
    # Display all shen sha definitions
    if 'shen_sa' in result_json:
        display_shen_sha_definitions(result_json['shen_sa'])
    
    if 'bian_gua_name' in result_json:
        # Check if the changed hexagram matches expected
        if expected_changed_code in HEXAGRAM_MAP:
            expected_info = HEXAGRAM_MAP[expected_changed_code]
            if hasattr(expected_info, 'get_detailed_name'):
                expected_name = expected_info.get_detailed_name()
            else:
                expected_name = expected_info.name
            print(f"Expected changed hexagram: {expected_changed_code} ({expected_name})")
    
    print()
    print("=" * 70)
    
    # Verify hexagram transformation
    success = False
    if 'bian_gua_name' in result_json:
        changed_name = result_json['bian_gua_name']
        expected_name = HEXAGRAM_MAP[expected_changed_code].name
        expected_full_name = f"{HEXAGRAM_MAP[expected_changed_code].palace_type}宫: {expected_name}"
        
        print("Verification:")
        print(f"  Expected changed hexagram: {expected_changed_code} ({expected_full_name})")
        print(f"  Actual changed hexagram: {changed_name}")
        
        # Verify the hexagram code by checking which hexagram matches the name
        found_code = None
        for code, info in HEXAGRAM_MAP.items():
            full_name = f"{info.palace_type}宫: {info.name}"
            if full_name == changed_name:
                found_code = code
                break
        
        if found_code:
            print(f"  Found hexagram code: {found_code}")
            success = found_code == expected_changed_code
            print(f"  ✓ Code match: {success}")
        else:
            print(f"  ✗ Could not find hexagram code for: {changed_name}")
    else:
        print("  ✗ No changed hexagram found in result")
    
    print()
    print("=" * 70)
    if success:
        print("✓ TEST PASSED: Hexagram correctly changed from 111111 to 011111")
    else:
        print("✗ TEST FAILED: Hexagram change verification failed")
    print("=" * 70)
    
    return yao_list, result_json, success


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Test Liu Yao divination with custom date and hexagram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using traditional format (老陽/陽/老陰/陰) - automatically extracts changing lines
  python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 老陽 陽 老陰 陰 陽 陽
  
  # Using legacy format (1/0/o/x) - automatically extracts changing lines
  python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 x 0 0 o 1
  
  # Using legacy format with no changing lines (all 1 or 0)
  python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 1 1 1 1 1
  
  # Using ganzi format for date
  python test_liu_yao.py --bazi 甲子 乙丑 丙寅 丁卯 --yao 老陽 陽 老陰 陰 陽 陽
  
  # Using ganzi format with legacy format
  python test_liu_yao.py --bazi 乙巳 丁亥 甲子 甲戌 --yao 1 1 1 1 1 1
        """
    )
    
    # Date and time (mutually exclusive with --bazi)
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--date', type=str, help='Date in format YYYY/MM/DD (e.g., 2025/11/25)')
    date_group.add_argument('--bazi', nargs=4, type=str, metavar=('YEAR', 'MONTH', 'DAY', 'HOUR'),
                           help='BaZi in ganzi format: 4 pillars "天干地支" (e.g., 甲子 乙丑 丙寅 丁卯)')
    
    parser.add_argument('--time', type=str, help='Time in format HH:MM or HH:MM:SS (e.g., 19:00 or 19:00:00). Required when using --date. Ignored when using --bazi.')
    
    # Hexagram specification (using yao format)
    parser.add_argument('--yao', nargs=6, type=str, metavar=('YAO1', 'YAO2', 'YAO3', 'YAO4', 'YAO5', 'YAO6'),
                       help='Specify each yao: 6 values. Use 老陽/陽/老陰/陰 OR legacy format 1/0/o/x (1=yang, 0=yin, o=yang changing, x=yin changing, bottom to top). Required unless using --examples.')
    
    # Show/Hide Shen Sha
    parser.add_argument('--show-shen-sha', action='store_true', default=True,
                       help='Show shen sha markers in traditional format (default: True)')
    parser.add_argument('--hide-shen-sha', action='store_false', dest='show_shen_sha',
                       help='Hide shen sha markers in traditional format')
    
    # Run examples
    parser.add_argument('--examples', action='store_true',
                       help='Run example test cases instead of custom test')
    
    return parser.parse_args()


def parse_date(date_str: str) -> tuple:
    """Parse date string YYYY/MM/DD into (year, month, day)"""
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            raise ValueError("Date must be in format YYYY/MM/DD")
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError) as e:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY/MM/DD") from e


def parse_time(time_str: str) -> tuple:
    """Parse time string HH:MM or HH:MM:SS into (hour, minute, second)"""
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1]), 0
        elif len(parts) == 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        else:
            raise ValueError("Time must be in format HH:MM or HH:MM:SS")
    except (ValueError, IndexError) as e:
        raise argparse.ArgumentTypeError(f"Invalid time format: {time_str}. Use HH:MM or HH:MM:SS") from e


def parse_bazi(bazi_list: List[str]) -> BaZi:
    """Parse BaZi from list of 4 pillar strings"""
    if len(bazi_list) != 4:
        raise argparse.ArgumentTypeError("BaZi must have exactly 4 pillars")
    
    pillars = []
    for bazi_str in bazi_list:
        if len(bazi_str) != 2:
            raise argparse.ArgumentTypeError(f"Invalid pillar format: {bazi_str}. Each pillar must be 2 characters (天干地支)")
        stem = bazi_str[0]
        branch = bazi_str[1]
        pillars.append(Pillar(stem, branch))
    
    # Calculate xun_kong from day pillar
    xun_kong_1, xun_kong_2 = BaZi.calculate_xun_kong(pillars[2])  # pillars[2] is day pillar
    
    return BaZi(pillars[0], pillars[1], pillars[2], pillars[3], xun_kong_1, xun_kong_2)


def parse_yao_traditional(yao_list: List[str]) -> tuple:
    """Parse traditional yao format (老陽/陽/老陰/陰) to hexagram code and changing lines
    
    Args:
        yao_list: List of 6 yao values, each can be: 老陽, 陽, 老陰, 陰
        
    Returns:
        tuple: (hexagram_code: str, changing_lines: List[int])
        - hexagram_code: 6-digit string (1=yang, 0=yin)
        - changing_lines: List of line positions (1-6) that are changing
        
    Example:
        parse_yao_traditional(['老陽', '陽', '老陰', '陰', '陽', '老陽'])
        Returns: ('110010', [1, 3, 6])
    """
    valid_yao = {'老陽', '陽', '老陰', '陰'}
    
    if len(yao_list) != 6:
        raise ValueError(f"Must provide exactly 6 yao values, got {len(yao_list)}")
    
    hexagram_code = ""
    changing_lines = []
    
    for i, yao in enumerate(yao_list):
        yao = yao.strip()
        if yao not in valid_yao:
            raise ValueError(f"Invalid yao value: {yao}. Must be one of: {valid_yao}")
        
        line_num = i + 1  # Lines are numbered 1-6 from bottom to top
        
        if yao == '老陽':
            hexagram_code += '1'  # Yang
            changing_lines.append(line_num)  # Changing
        elif yao == '陽':
            hexagram_code += '1'  # Yang
            # Not changing
        elif yao == '老陰':
            hexagram_code += '0'  # Yin
            changing_lines.append(line_num)  # Changing
        elif yao == '陰':
            hexagram_code += '0'  # Yin
            # Not changing
    
    return hexagram_code, changing_lines


def parse_yao_legacy(yao_list: List[str]) -> tuple:
    """Parse legacy yao format (1/0/o/x) to hexagram code and changing lines
    
    Args:
        yao_list: List of 6 yao values, each can be: '1', '0', 'o', 'x'
        - '1' = yang, not changing
        - '0' = yin, not changing
        - 'o' = yang (1), changing
        - 'x' = yin (0), changing
        
    Returns:
        tuple: (hexagram_code: str, changing_lines: List[int])
        - hexagram_code: 6-digit string (1=yang, 0=yin)
        - changing_lines: List of line positions (1-6) that are changing
        
    Example:
        parse_yao_legacy(['1', 'x', '0', '0', 'o', '1'])
        Returns: ('101010', [2, 5])
    """
    valid_yao = {'0', '1', 'o', 'O', 'x', 'X'}
    
    if len(yao_list) != 6:
        raise ValueError(f"Must provide exactly 6 yao values, got {len(yao_list)}")
    
    hexagram_code = ""
    changing_lines = []
    
    for i, yao in enumerate(yao_list):
        yao = yao.strip()
        yao_lower = yao.lower()
        
        if yao_lower not in {'0', '1', 'o', 'x'}:
            raise ValueError(f"Invalid yao value: {yao}. Must be one of: 1, 0, o, x")
        
        line_num = i + 1  # Lines are numbered 1-6 from bottom to top
        
        if yao_lower == '1':
            hexagram_code += '1'  # Yang, not changing
        elif yao_lower == '0':
            hexagram_code += '0'  # Yin, not changing
        elif yao_lower == 'o':
            hexagram_code += '1'  # Yang
            changing_lines.append(line_num)  # Changing
        elif yao_lower == 'x':
            hexagram_code += '0'  # Yin
            changing_lines.append(line_num)  # Changing
    
    return hexagram_code, changing_lines


def test_san_he_ju():
    """
    测试三合局判断功能
    
    三合局有四种：
    - 巳酉丑（中神：酉）
    - 申子辰（中神：子）
    - 亥卯未（中神：卯）
    - 寅午戌（中神：午）
    
    条件：
    1. 必须是動爻(changing=True)，或是暗動(an_dong=True)，或是动之变爻，或是日、月
    2. 静爻不参加
    3. 中神必须为動爻，如果是动之变爻的话，必须跟動爻一起参加
    """
    print("=" * 70)
    print("测试三合局判断功能")
    print("=" * 70)
    
    # 测试案例1：巳酉丑三合局
    # 使用兑为泽卦（110110），纳甲地支：巳、卯、丑、亥、酉、未（从下往上）
    # 设置第5爻（酉，中神）为動爻
    # 设置日柱为丑，月柱为巳（或者让1爻和3爻为動爻/暗動）
    print("\n【测试案例1】巳酉丑三合局")
    print("-" * 70)
    print("卦象：兑为泽（110110）")
    print("纳甲地支（从下往上）：巳、卯、丑、亥、酉、未")
    print("设置：第5爻（酉，中神）为動爻，日柱为丑")
    print("-" * 70)
    
    # 创建八字：日柱为丑，月柱为巳
    # 乙巳年 丁亥月 己丑日 甲戌时
    bazi1 = BaZi(
        Pillar("乙", "巳"),  # 年柱
        Pillar("丁", "亥"),  # 月柱（亥，不是巳，但我们可以用日柱）
        Pillar("己", "丑"),  # 日柱（丑）
        Pillar("甲", "戌")   # 时柱
    )
    
    # 兑为泽：110110，第5爻（酉）为動爻
    yao_list1, result_json1 = test_custom_divination(
        hexagram_code="110110",  # 兑为泽
        changing_lines=[5],  # 第5爻（酉）为動爻
        manual_bazi=bazi1,
        show_shen_sha=True
    )
    
    # 檢查三合局结果
    if 'san_he_ju' in result_json1:
        san_he_ju = result_json1['san_he_ju']
        if san_he_ju:
            print(f"\n✓ 检测到三合局: {san_he_ju}")
        else:
            print("\n✗ 未检测到三合局")
            print("  提示：可能需要更多条件，如1爻（巳）或3爻（丑）为動爻/暗動")
    else:
        print("\n✗ 三合局字段不存在")
    
    # 测试案例2：申子辰三合局
    # 使用坎为水卦（010010），纳甲地支：寅、辰、午、申、戌、子（从下往上）
    # 设置第6爻（子，中神）为動爻
    # 设置日柱为辰，让2爻（辰）为動爻或暗動
    print("\n\n【测试案例2】申子辰三合局")
    print("-" * 70)
    print("卦象：坎为水（010010）")
    print("纳甲地支（从下往上）：寅、辰、午、申、戌、子")
    print("设置：第6爻（子，中神）为動爻，第2爻（辰）为動爻，日柱为申")
    print("-" * 70)
    
    # 创建八字：日柱为申
    bazi2 = BaZi(
        Pillar("甲", "子"),  # 年柱
        Pillar("丙", "寅"),  # 月柱
        Pillar("戊", "申"),  # 日柱（申）
        Pillar("庚", "戌")   # 时柱
    )
    
    # 坎为水：010010，第2爻（辰）和第6爻（子，中神）为動爻
    yao_list2, result_json2 = test_custom_divination(
        hexagram_code="010010",  # 坎为水
        changing_lines=[2, 6],  # 第2爻（辰）和第6爻（子，中神）为動爻
        manual_bazi=bazi2,
        show_shen_sha=True
    )
    
    # 檢查三合局结果
    if 'san_he_ju' in result_json2:
        san_he_ju = result_json2['san_he_ju']
        if san_he_ju:
            print(f"\n✓ 检测到三合局: {san_he_ju}")
        else:
            print("\n✗ 未检测到三合局")
    else:
        print("\n✗ 三合局字段不存在")
    
    # 测试案例3：亥卯未三合局
    # 使用坤为地卦（000000），纳甲地支：未、巳、卯、丑、亥、酉（从下往上）
    # 设置第3爻（卯，中神）为動爻
    print("\n\n【测试案例3】亥卯未三合局")
    print("-" * 70)
    print("卦象：坤为地（000000）")
    print("纳甲地支（从下往上）：未、巳、卯、丑、亥、酉")
    print("设置：第1爻（未）、第3爻（卯，中神）、第5爻（亥）为動爻")
    print("-" * 70)
    
    bazi3 = BaZi(
        Pillar("甲", "子"),  # 年柱
        Pillar("丙", "寅"),  # 月柱
        Pillar("戊", "午"),  # 日柱
        Pillar("庚", "申")   # 时柱
    )
    
    # 坤为地：000000，第1爻（未）、第3爻（卯，中神）、第5爻（亥）为動爻
    yao_list3, result_json3 = test_custom_divination(
        hexagram_code="000000",  # 坤为地
        changing_lines=[1, 3, 5],  # 第1爻（未）、第3爻（卯，中神）、第5爻（亥）为動爻
        manual_bazi=bazi3,
        show_shen_sha=True
    )
    
    # 檢查三合局结果
    if 'san_he_ju' in result_json3:
        san_he_ju = result_json3['san_he_ju']
        if san_he_ju:
            print(f"\n✓ 检测到三合局: {san_he_ju}")
        else:
            print("\n✗ 未检测到三合局")
    else:
        print("\n✗ 三合局字段不存在")
    
    print("\n" + "=" * 70)
    print("三合局测试完成")
    print("=" * 70)


if __name__ == "__main__":
    args = parse_args()
    
    # If --examples flag is set, run example tests
    if args.examples:
        print("Example 1: Original test case")
        print()
        test_hexagram_111111_to_011111()
        
        print("\n\n")
        
        print("Example 2: Custom test with specified date and hexagram")
        print()
        test_custom_divination(
            year=2025, month=11, day=25, hour=19,
            hexagram_code="111111",
            changing_lines=[1]
        )
        
        print("\n\n")
        
        print("Example 3: Custom test with different hexagram")
        print()
        test_custom_divination(
            year=2025, month=1, day=1, hour=12,
            hexagram_code="010010",
            changing_lines=[2, 5]
        )
        
        print("\n\n")
        
        print("Example 4: Specify each yao individually")
        print()
        test_with_individual_yao(
            year=2025, month=11, day=25, hour=19,
            yao1="1", yao2="0", yao3="1", yao4="0", yao5="1", yao6="0",
            changing_lines=[1, 3]
        )
        
        print("\n\n")
        
        print("Example 5: Test 三合局 (San He Ju)")
        print()
        test_san_he_ju()
    else:
        # Parse command-line arguments
        year, month, day = 2025, 11, 25  # defaults
        hour, minute, second = 19, 0, 0  # defaults
        manual_bazi = None
        
        # Parse date/time OR BaZi
        if args.bazi:
            # Use ganzi format (alternative to date/time)
            manual_bazi = parse_bazi(args.bazi)
            print(f"Using BaZi from ganzi format: {manual_bazi.year.to_string()} {manual_bazi.month.to_string()} {manual_bazi.day.to_string()} {manual_bazi.hour.to_string()}")
            # Set dummy date values for display purposes only (won't be used)
            year, month, day = 2025, 11, 25
            hour, minute, second = 19, 0, 0
        elif args.date:
            # Use date/time format
            year, month, day = parse_date(args.date)
            if not args.time:
                raise ValueError("--time is required when using --date")
            hour, minute, second = parse_time(args.time)
        else:
            # Default: use date/time defaults if neither specified
            pass  # use defaults
        
        # Parse yao (required unless using --examples)
        if not args.yao:
            raise ValueError("--yao is required. Specify 6 yao values using traditional format (老陽/陽/老陰/陰) or legacy format (1/0/o/x).")
        
        # Check if using traditional format (老陽/陽/老陰/陰) or legacy format (1/0/o/x)
        valid_yao_traditional = {'老陽', '陽', '老陰', '陰'}
        valid_yao_legacy = {'0', '1', 'o', 'O', 'x', 'X'}
        
        # Check if all values are in traditional format
        if all(y.strip() in valid_yao_traditional for y in args.yao):
            # Traditional format: extract hexagram code and changing lines
            hexagram_code, changing_lines = parse_yao_traditional(args.yao)
            print(f"Parsed traditional yao format: {args.yao}")
            print(f"  -> Hexagram code: {hexagram_code}")
            print(f"  -> Changing lines: {changing_lines}")
        # Check if all values are in legacy format (1/0/o/x)
        elif all(y.strip().lower() in {'0', '1', 'o', 'x'} for y in args.yao):
            # Legacy format: extract hexagram code and changing lines
            hexagram_code, changing_lines = parse_yao_legacy(args.yao)
            print(f"Parsed legacy yao format: {args.yao}")
            print(f"  -> Hexagram code: {hexagram_code}")
            print(f"  -> Changing lines: {changing_lines}")
        else:
            # Mixed format - error
            raise ValueError(f"Invalid yao format. Use either traditional format (老陽/陽/老陰/陰) or legacy format (1/0/o/x), not mixed. Got: {args.yao}")
        
        # Run the test
        test_custom_divination(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            hexagram_code=hexagram_code,
            changing_lines=changing_lines,
            manual_bazi=manual_bazi,
            show_shen_sha=args.show_shen_sha
        )
