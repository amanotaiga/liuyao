# 六爻排盤系統 (Liu Yao Divination System)

A comprehensive Python implementation of the Liu Yao (六爻) divination system, featuring both a command-line interface and a modern web-based Gradio interface. This system performs traditional Chinese divination calculations including hexagram analysis, changing lines, hidden gods, and various divine markers (神煞).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Module Documentation](#module-documentation)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Development](#development)
- [Notes and Limitations](#notes-and-limitations)

## Features

- **Complete Liu Yao Calculations**: Full implementation of traditional six-line hexagram divination
- **Multiple Input Methods**: 
  - Western calendar date input
  - Gan-Zhi (干支) calendar input
  - Hexagram name search
  - Clickable hexagram line input
- **Comprehensive Analysis**:
  - Hexagram generation and transformation
  - Changing lines (動爻) detection
  - Hidden gods (伏神) calculation
  - Divine markers (神煞) including:
    - 旬空 (Xun Kong - Void)
    - 月破 (Yue Peng - Month Break)
    - 日沖 (Ri Chong - Day Clash)
    - 月合/日合 (Yue He/Ri He - Month/Day Harmony)
    - 臨日/日扶 (Lin Ri/Ri Fu - Day Support)
    - 日生/日克 (Ri Sheng/Ri Ke - Day Generation/Control)
    - 暗動/日破 (An Dong/Ri Peng - Hidden Movement/Day Break)
    - 桃花 (Tao Hua - Peach Blossom)
    - 驛馬 (Yi Ma - Traveling Horse)
    - 貴人 (Gui Ren - Noble Person)
  - Three combinations (三合局) detection
  - Strength/weakness (旺衰) analysis
  - Six relatives (六親) relationships
  - Six spirits (六神) assignment
- **Modern Web Interface**: Beautiful Gradio-based UI with real-time visualization
- **Responsive Design**: Mobile-friendly compact view option with optimized formatting for different screen sizes
- **Modular Architecture**: Well-organized, maintainable codebase with separation of concerns
- **Multiple Output Formats**: Text, HTML, and image rendering support

## Installation

### Requirements

- **Python**: 3.11 or higher
- **External Dependencies**:
  - `gradio` - For web interface
  - `lunar_python` - Optional, for automatic BaZi calculation from solar dates

### Installation Steps

1. Clone or download this repository

2. Install required packages:

**Option A: Using requirements.txt (Recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Manual installation**
```bash
pip install gradio>=4.0.0
pip install lunar_python>=0.0.9  # Optional, for automatic BaZi calculation from dates
```

**Note**: If `lunar_python` is not installed, you can still use the system by providing BaZi information manually using the Gan-Zhi calendar input method.

## Quick Start

### Web Interface (Recommended)

Launch the Gradio web interface using one of these methods:

**Method 1: Using the convenience script (Recommended)**
```bash
python run_gradio_ui.py
```

**Method 2: Using Python module**
```bash
python -m gradio_ui.main
```

**Method 3: From gradio_ui directory**
```bash
cd gradio_ui
python main.py
```

**Method 4: Using app.py (for Hugging Face Spaces deployment)**
```bash
python app.py
```

This will start a local web server (typically at `http://127.0.0.1:7860`). Open the URL in your browser to access the interface.

### Command-Line Interface

Use the test script for command-line operations:

```bash
# Using traditional format (老陽/陽/老陰/陰)
python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 老陽 陽 老陰 陰 陽 陽

# Using hexagram code format
python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 1 1 1 1 1
```

### Python API

```python
from liu_yao import six_yao_divination_from_date

# Perform divination
yao_list, result = six_yao_divination_from_date(
    "111111",  # Hexagram code (6 digits: '1'=yang, '0'=yin, bottom to top)
    "2025/12/01 19:00",  # Date string
    [1]  # Changing line positions (1-6)
)

# Display results
from liu_yao import format_liu_yao_display
print(format_liu_yao_display(yao_list, show_shen_sha=True))
```

## Project Structure

```
liuyao/
├── app.py                    # Hugging Face Spaces entry point
├── gradio_ui/                # Gradio UI package (refactored)
│   ├── __init__.py
│   ├── main.py               # Main entry point
│   ├── ui_builder.py         # UI orchestration
│   ├── config.py             # Configuration and constants
│   ├── components/           # UI components
│   │   ├── __init__.py
│   │   ├── date_inputs.py    # Date input components
│   │   ├── hexagram_inputs.py # Hexagram input components
│   │   └── result_display.py  # Result display component
│   ├── handlers/             # Event handlers
│   │   ├── __init__.py
│   │   ├── date_handlers.py   # Date input handlers
│   │   ├── hexagram_handlers.py # Hexagram handlers
│   │   └── divination_handlers.py # Divination processing
│   ├── utils/                # Utility modules
│   │   ├── __init__.py
│   │   ├── formatting.py     # Result formatting
│   │   ├── hexagram_utils.py  # Hexagram utilities
│   │   ├── html_generator.py  # HTML generation
│   │   ├── static_loader.py   # Static asset loader
│   │   └── validation.py      # Input validation
│   └── static/               # Static assets
│       ├── styles.css        # CSS styles
│       └── scripts.js        # JavaScript
├── run_gradio_ui.py          # Convenience script to run UI
├── requirements.txt          # Python dependencies
├── gradio_ui.py              # Legacy UI (kept for reference)
├── liu_yao.py                # Core divination engine
├── ba_zi_base.py             # Pillar and BaZi data structures
├── ganzhi.py                 # Gan-Zhi system utilities
├── wu_xing_utils.py          # Five Elements utilities
├── test_liu_yao.py           # Test script and formatting utilities
├── README.md                 # This file
└── old/                      # Legacy versions (for reference)
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Modules

- **`liu_yao.py`**: Core divination calculation engine
- **`ba_zi_base.py`**: BaZi (八字) and Pillar data structures
- **`ganzhi.py`**: Gan-Zhi (干支) system utilities
- **`wu_xing_utils.py`**: Five Elements (五行) calculations

### Gradio UI Package (`gradio_ui/`)

The UI has been refactored into a well-organized package:

#### Components (`gradio_ui/components/`)
- **`date_inputs.py`**: Western and Gan-Zhi calendar input tabs
- **`hexagram_inputs.py`**: Hexagram name search and clickable input tabs
- **`result_display.py`**: Result table display component

#### Handlers (`gradio_ui/handlers/`)
- **`date_handlers.py`**: Date input processing utilities
- **`hexagram_handlers.py`**: Hexagram selection and processing utilities
- **`divination_handlers.py`**: Main divination processing with data classes

#### Utils (`gradio_ui/utils/`)
- **`formatting.py`**: Result formatting functions (PC and mobile formats)
- **`hexagram_utils.py`**: Hexagram search and calculation utilities
- **`html_generator.py`**: HTML generation for hexagram visualization
- **`static_loader.py`**: CSS and JavaScript file loading
- **`validation.py`**: Input validation functions

#### Static Assets (`gradio_ui/static/`)
- **`styles.css`**: Responsive CSS styles with mobile support
- **`scripts.js`**: JavaScript for interactive UI features

#### Configuration (`gradio_ui/config.py`)
- Constants and configuration settings
- Error messages
- UI configuration (colors, styling, etc.)

## Module Documentation

### Core Module: liu_yao.py

**Purpose**: Core calculation engine for Liu Yao divination system.

#### Main Functions

##### `six_yao_divination(main_hexagram_code, bazi, changing_line_indices)`

Main divination function that performs all calculations.

**Parameters**:
- `main_hexagram_code` (str): 6-digit hexagram code ('1'=yang, '0'=yin, from bottom to top)
- `bazi` (BaZi): Four Pillars object containing year, month, day, hour pillars
- `changing_line_indices` (List[int]): List of changing line positions (1-6)

**Returns**:
- `Tuple[List[YaoDetails], dict]`: List of YaoDetails objects and result JSON dictionary

##### `six_yao_divination_from_date(main_hexagram_code, date_str, changing_line_indices)`

Convenience function that creates BaZi from date string and performs divination.

**Parameters**:
- `main_hexagram_code` (str): 6-digit hexagram code
- `date_str` (str): Date string in formats:
  - `"YYYY/MM/DD HH:MM"` (e.g., `"2025/12/01 19:00"`)
  - `"YYYY/MM/DD HH:MM:SS"`
  - `"YYYY-MM-DD HH:MM"`
  - `"YYYY-MM-DD HH:MM:SS"`
- `changing_line_indices` (List[int]): List of changing line positions

##### `format_liu_yao_display(yao_list, show_shen_sha=True, for_gradio=False)`

Formats divination results as a traditional table display.

**Parameters**:
- `yao_list` (List[YaoDetails]): List of six YaoDetails objects
- `show_shen_sha` (bool): Whether to show divine markers (default: True)
- `for_gradio` (bool): Whether formatting for Gradio (uses 5 chars for yang) vs terminal (6 chars)

### Gradio UI Package

#### Entry Points

**`app.py`**: Entry point for Hugging Face Spaces and cloud deployments.

**`run_gradio_ui.py`**: Convenience script to launch the UI from project root.

**`gradio_ui/main.py`**: Main entry point that can be run directly or imported as a module.

**`gradio_ui/ui_builder.py`**: Orchestrates all UI components to create the complete Gradio interface.

#### Key Components

**Date Inputs** (`gradio_ui/components/date_inputs.py`):
- Western calendar date selection
- Gan-Zhi calendar interactive pillar building
- State management for date inputs

**Hexagram Inputs** (`gradio_ui/components/hexagram_inputs.py`):
- Name search with dropdown selection
- Clickable hexagram line toggling
- Real-time hexagram visualization

**Result Display** (`gradio_ui/components/result_display.py`):
- Formatted result table
- Scrollable output area
- Mobile-responsive formatting support

#### Handlers

**Divination Handlers** (`gradio_ui/handlers/divination_handlers.py`):
- `DivinationRequest`: Data class for divination requests
- `process_divination_request()`: Main processing function
- `process_divination()`: Legacy wrapper for backward compatibility
- Helper functions for BaZi creation and hexagram extraction

### Dependency Modules

#### ba_zi_base.py

Provides fundamental data structures for Gan-Zhi pillars and BaZi.

**Classes**:
- `Pillar`: Represents a Gan-Zhi pillar (天干地支 combination)
- `BaZi`: Represents Four Pillars (八字) with year, month, day, and hour

#### ganzhi.py

Provides core definitions for TianGan (Heavenly Stems) and DiZhi (Earthly Branches).

**Classes**:
- `DiZhi`: Enumeration of 12 earthly branches
- `Mapper`: Static class for Chinese name conversion

#### wu_xing_utils.py

Provides data mappings and utility functions for the Five Elements (五行) system.

**Functions**:
- `getWangShuai()`: Calculates strength/weakness (旺衰) state
- `getElementalRelationship()`: Determines five-element relationships
- `checkLinRiRiFu()`: Checks day support relationships
- `checkRiShengRiKe()`: Checks day generation/control

## Usage Examples

### Example 1: Basic Divination

```python
from liu_yao import six_yao_divination_from_date, format_liu_yao_display

# Perform divination
yao_list, result = six_yao_divination_from_date(
    "111111",  # 乾為天 (Heaven)
    "2025/12/01 19:00",
    [1]  # First line is changing
)

# Display results
print(format_liu_yao_display(yao_list, show_shen_sha=True))
```

### Example 2: Manual BaZi Input

```python
from liu_yao import six_yao_divination, format_liu_yao_display
from ba_zi_base import Pillar, BaZi

# Create BaZi manually
bazi = BaZi(
    Pillar("乙", "巳"),  # Year: 乙巳
    Pillar("丁", "亥"),  # Month: 丁亥
    Pillar("甲", "子"),  # Day: 甲子
    Pillar("甲", "戌")   # Hour: 甲戌
)

# Perform divination
yao_list, result = six_yao_divination(
    "011111",  # 天風姤
    bazi,
    [1, 3]  # Lines 1 and 3 are changing
)

# Display results
print(format_liu_yao_display(yao_list))
```

### Example 3: Web Interface

```python
from gradio_ui.ui_builder import create_ui

demo = create_ui()
demo.launch(share=True)  # Launch with public URL
```

Or use the convenience script:

```bash
python run_gradio_ui.py
```

### Example 4: Using the New Modular Structure

```python
from gradio_ui.handlers.divination_handlers import (
    DivinationRequest,
    WesternDateInput,
    GanzhiDateInput,
    NameMethodInput,
    process_divination_request
)

# Create a divination request using data classes
request = DivinationRequest(
    use_western_date=True,
    western_date=WesternDateInput(year=2025, month=12, day=1, hour=19),
    ganzhi_date=None,
    use_button_method=False,
    button_method=None,
    name_method=NameMethodInput(
        hexagram_name_query="乾為天",
        selected_hexagram_code="111111",
        changing_lines=[True, False, False, False, False, False]
    )
)

# Process the request
result = process_divination_request(request)
print(result)
```

## API Reference

### Core Functions

#### `six_yao_divination(main_hexagram_code: str, bazi: BaZi, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]`

Performs complete Liu Yao divination calculation.

**Parameters**:
- `main_hexagram_code`: 6-digit string ('1'=yang, '0'=yin, from bottom to top)
- `bazi`: BaZi object with four pillars
- `changing_line_indices`: List of line numbers (1-6) that are changing

**Returns**:
- `yao_list`: List of 6 `YaoDetails` objects (position 1-6, bottom to top)
- `result_json`: Dictionary containing hexagram information and calculations

#### `six_yao_divination_from_date(main_hexagram_code: str, date_str: str, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]`

Convenience wrapper that creates BaZi from date string.

#### `format_liu_yao_display(yao_list: List[YaoDetails], show_shen_sha: bool = True, for_gradio: bool = False) -> str`

Formats results as traditional table.

### Hexagram Code Format

Hexagram codes are 6-digit strings representing lines from bottom to top:
- `'1'` = yang line (陽爻) - solid line
- `'0'` = yin line (陰爻) - broken line

Example: `"111111"` = 乾為天 (all yang lines)

### Changing Lines

Changing lines (動爻) are specified as a list of line numbers (1-6):
- `[1]` = First line (bottom) is changing
- `[1, 3, 5]` = Lines 1, 3, and 5 are changing

When a line changes:
- Yang (1) → Yin (0)
- Yin (0) → Yang (1)

## Development

### Project Structure

The project has been refactored for better maintainability:

- **Components**: Self-contained UI components with their own state management
- **Handlers**: Business logic separated from UI components
- **Utils**: Reusable utility functions
- **Config**: Centralized configuration and constants
- **Static Assets**: CSS and JavaScript in separate files

### Running Tests

```bash
# Run the test script
python test_liu_yao.py --date 2025/12/01 --time 19:00 --yao 1 1 1 1 1 1
```

### Code Style

The project follows Python PEP 8 style guidelines. Type hints are used throughout for better code clarity and IDE support.

## Notes and Limitations

### Optional Dependencies

- **lunar_python**: Required only for automatic BaZi calculation from solar dates. If not installed, use manual BaZi input via Gan-Zhi calendar.

### Known Limitations

1. **Date Range**: BaZi calculation from dates may have limitations depending on `lunar_python` library capabilities.

2. **Hexagram Map**: Currently supports all 64 hexagrams in the standard I Ching system.

3. **Display Formatting**: Terminal display assumes monospace font for proper alignment. Some terminals may not render Chinese characters correctly.

### Migration from Legacy Code

The original `gradio_ui.py` (2332 lines) has been refactored into a modular package structure. The legacy file is kept in the repository for reference. The new structure provides:

- Better maintainability
- Easier testing
- Clearer separation of concerns
- Reusable components

To use the new structure, import from `gradio_ui` package:

```python
# Old way (still works but deprecated)
from gradio_ui import create_ui

# New way (recommended)
from gradio_ui.ui_builder import create_ui
```

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please ensure code follows the existing style and includes appropriate documentation.

## Acknowledgments

This implementation is based on traditional Liu Yao divination principles and converted from a C++23 module implementation.
