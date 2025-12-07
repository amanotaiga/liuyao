# 六爻排盤系統 (Liu Yao Divination System)

一個全面的 Python 實作六爻排盤系統，提供命令列介面和現代化的 Gradio 網頁介面。本系統執行傳統中國占卜計算，包括卦象分析、動爻、伏神，以及各種神煞標記。

## 目錄

- [功能特色](#功能特色)
- [安裝說明](#安裝說明)
- [快速開始](#快速開始)
- [專案結構](#專案結構)
- [架構說明](#架構說明)
- [模組文件](#模組文件)
- [使用範例](#使用範例)
- [API 參考](#api-參考)
- [開發指南](#開發指南)
- [注意事項與限制](#注意事項與限制)

## 功能特色

- **完整的六爻計算**：完整實作傳統六爻卦象占卜
- **多種輸入方式**： 
  - 西曆日期輸入
  - 干支曆日期輸入
  - 卦名搜尋
  - 點擊卦象線輸入
- **全面分析**：
  - 卦象生成與轉換
  - 動爻檢測
  - 伏神計算
  - 神煞標記包括：
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
  - 三合局檢測
  - 旺衰分析
  - 六親關係
  - 六神配置
- **現代網頁介面**：美觀的 Gradio 介面，支援即時視覺化
- **響應式設計**：支援行動裝置的緊湊檢視選項，針對不同螢幕尺寸優化格式
- **模組化架構**：組織良好的程式碼，易於維護，關注點分離
- **多種輸出格式**：支援文字、HTML 和圖片渲染

## 安裝說明

### 需求

- **Python**：3.11 或更高版本
- **外部相依套件**：
  - `gradio` - 用於網頁介面
  - `lunar_python` - 選用，用於從西曆日期自動計算八字

### 安裝步驟

1. 複製或下載本儲存庫

2. 安裝必要套件：

**選項 A：使用 requirements.txt（推薦）**
```bash
pip install -r requirements.txt
```

**選項 B：手動安裝**
```bash
pip install gradio>=4.0.0
pip install lunar_python>=0.0.9  # 選用，用於從西曆日期自動計算八字
```

**注意**：如果未安裝 `lunar_python`，您仍可使用系統，只需透過干支曆輸入方式手動提供八字資訊。

## 快速開始

### 網頁介面（推薦）

使用以下任一方式啟動 Gradio 網頁介面：

**方法 1：使用便利腳本（推薦）**
```bash
python run_gradio_ui.py
```

**方法 2：使用 Python 模組**
```bash
python -m gradio_ui.main
```

**方法 3：從 gradio_ui 目錄執行**
```bash
cd gradio_ui
python main.py
```

**方法 4：使用 app.py（用於 Hugging Face Spaces 部署）**
```bash
python app.py
```

這會啟動本地網頁伺服器（通常在 `http://127.0.0.1:7860`）。在瀏覽器中開啟該網址以存取介面。

### 命令列介面

使用測試腳本進行命令列操作：

```bash
# 使用傳統格式（老陽/陽/老陰/陰）
python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 老陽 陽 老陰 陰 陽 陽

# 使用卦象代碼格式
python test_liu_yao.py --date 2025/11/25 --time 19:00 --yao 1 1 1 1 1 1
```

### Python API

```python
from liu_yao import six_yao_divination_from_date

# 執行占卜
yao_list, result = six_yao_divination_from_date(
    "111111",  # 卦象代碼（6 位數字：'1'=陽，'0'=陰，由下往上）
    "2025/12/01 19:00",  # 日期字串
    [1]  # 動爻位置（1-6）
)

# 顯示結果
from liu_yao import format_liu_yao_display
print(format_liu_yao_display(yao_list, show_shen_sha=True))
```

## 專案結構

```
liuyao/
├── app.py                    # Hugging Face Spaces 進入點
├── gradio_ui/                # Gradio UI 套件（已重構）
│   ├── __init__.py
│   ├── main.py               # 主進入點
│   ├── ui_builder.py         # UI 組裝
│   ├── config.py             # 配置與常數
│   ├── components/           # UI 元件
│   │   ├── __init__.py
│   │   ├── date_inputs.py    # 日期輸入元件
│   │   ├── hexagram_inputs.py # 卦象輸入元件
│   │   └── result_display.py  # 結果顯示元件
│   ├── handlers/             # 事件處理器
│   │   ├── __init__.py
│   │   ├── date_handlers.py   # 日期輸入處理器
│   │   ├── hexagram_handlers.py # 卦象處理器
│   │   └── divination_handlers.py # 占卜處理
│   ├── utils/                # 工具模組
│   │   ├── __init__.py
│   │   ├── formatting.py     # 結果格式化
│   │   ├── hexagram_utils.py  # 卦象工具
│   │   ├── html_generator.py  # HTML 生成
│   │   ├── static_loader.py   # 靜態資源載入器
│   │   └── validation.py      # 輸入驗證
│   └── static/               # 靜態資源
│       ├── styles.css        # CSS 樣式
│       └── scripts.js         # JavaScript
├── run_gradio_ui.py          # 執行 UI 的便利腳本
├── requirements.txt          # Python 相依套件
├── gradio_ui.py              # 舊版 UI（保留供參考）
├── liu_yao.py                # 核心占卜引擎
├── ba_zi_base.py             # 柱和八字資料結構
├── ganzhi.py                 # 干支系統工具
├── wu_xing_utils.py          # 五行工具
├── test_liu_yao.py           # 測試腳本與格式化工具
├── README.md                 # 本文件（英文版）
├── README_zh_TW.md           # 本文件（繁體中文版）
└── old/                      # 舊版檔案（供參考）
```

## 架構說明

本專案採用模組化架構，清楚分離關注點：

### 核心模組

- **`liu_yao.py`**：核心占卜計算引擎
- **`ba_zi_base.py`**：八字和柱的資料結構
- **`ganzhi.py`**：干支系統工具
- **`wu_xing_utils.py`**：五行計算

### Gradio UI 套件（`gradio_ui/`）

UI 已重構為組織良好的套件：

#### 元件（`gradio_ui/components/`）
- **`date_inputs.py`**：西曆和干支曆日期輸入標籤頁
- **`hexagram_inputs.py`**：卦象名稱搜尋和點擊輸入標籤頁
- **`result_display.py`**：結果表格顯示元件

#### 處理器（`gradio_ui/handlers/`）
- **`date_handlers.py`**：日期輸入處理工具
- **`hexagram_handlers.py`**：卦象選擇與處理工具
- **`divination_handlers.py`**：使用資料類別的占卜處理

#### 工具（`gradio_ui/utils/`）
- **`formatting.py`**：結果格式化函數（PC 和行動裝置格式）
- **`hexagram_utils.py`**：卦象搜尋與計算工具
- **`html_generator.py`**：卦象視覺化的 HTML 生成
- **`static_loader.py`**：CSS 和 JavaScript 檔案載入
- **`validation.py`**：輸入驗證函數

#### 靜態資源（`gradio_ui/static/`）
- **`styles.css`**：響應式 CSS 樣式，支援行動裝置
- **`scripts.js`**：互動式 UI 功能的 JavaScript

#### 配置（`gradio_ui/config.py`）
- 常數與配置設定
- 錯誤訊息
- UI 配置（顏色、樣式等）

## 模組文件

### 核心模組：liu_yao.py

**用途**：六爻排盤系統的核心計算引擎。

#### 主要函數

##### `six_yao_divination(main_hexagram_code, bazi, changing_line_indices)`

執行所有計算的主要占卜函數。

**參數**：
- `main_hexagram_code` (str)：6 位數卦象代碼（'1'=陽，'0'=陰，由下往上）
- `bazi` (BaZi)：包含年月日時四柱的八字物件
- `changing_line_indices` (List[int])：動爻位置清單（1-6）

**回傳值**：
- `Tuple[List[YaoDetails], dict]`：YaoDetails 物件清單和結果 JSON 字典

##### `six_yao_divination_from_date(main_hexagram_code, date_str, changing_line_indices)`

從日期字串建立八字並執行占卜的便利函數。

**參數**：
- `main_hexagram_code` (str)：6 位數卦象代碼
- `date_str` (str)：日期字串，支援格式：
  - `"YYYY/MM/DD HH:MM"`（例如：`"2025/12/01 19:00"`）
  - `"YYYY/MM/DD HH:MM:SS"`
  - `"YYYY-MM-DD HH:MM"`
  - `"YYYY-MM-DD HH:MM:SS"`
- `changing_line_indices` (List[int])：動爻位置清單

##### `format_liu_yao_display(yao_list, show_shen_sha=True, for_gradio=False)`

將占卜結果格式化為傳統表格顯示。

**參數**：
- `yao_list` (List[YaoDetails])：六個 YaoDetails 物件清單
- `show_shen_sha` (bool)：是否顯示神煞（預設：True）
- `for_gradio` (bool)：是否為 Gradio 格式化（使用 5 字元陽爻）或終端機（6 字元）

### Gradio UI 套件

#### 進入點

**`app.py`**：Hugging Face Spaces 和雲端部署的進入點。

**`run_gradio_ui.py`**：從專案根目錄啟動 UI 的便利腳本。

**`gradio_ui/main.py`**：可直接執行或作為模組匯入的主進入點。

**`gradio_ui/ui_builder.py`**：協調所有 UI 元件以建立完整的 Gradio 介面。

#### 主要元件

**日期輸入**（`gradio_ui/components/date_inputs.py`）：
- 西曆日期選擇
- 干支曆互動式四柱建立
- 日期輸入的狀態管理

**卦象輸入**（`gradio_ui/components/hexagram_inputs.py`）：
- 帶下拉選單的名稱搜尋
- 點擊切換卦象線
- 即時卦象視覺化

**結果顯示**（`gradio_ui/components/result_display.py`）：
- 格式化結果表格
- 可滾動輸出區域
- 支援行動裝置響應式格式化

#### 處理器

**占卜處理器**（`gradio_ui/handlers/divination_handlers.py`）：
- `DivinationRequest`：占卜請求的資料類別
- `process_divination_request()`：主要處理函數
- `process_divination()`：向後相容的舊版包裝器
- 用於建立八字和提取卦象的輔助函數

### 相依模組

#### ba_zi_base.py

提供干支柱和八字的基本資料結構。

**類別**：
- `Pillar`：表示干支柱（天干地支組合）
- `BaZi`：表示包含年月日時的四柱八字

#### ganzhi.py

提供天干（Heavenly Stems）和地支（Earthly Branches）的核心定義。

**類別**：
- `DiZhi`：十二地支的列舉
- `Mapper`：中文名稱轉換的靜態類別

#### wu_xing_utils.py

提供五行系統的資料映射與工具函數。

**函數**：
- `getWangShuai()`：計算旺衰狀態
- `getElementalRelationship()`：判斷五行關係
- `checkLinRiRiFu()`：檢查日扶關係
- `checkRiShengRiKe()`：檢查日生/日克

## 使用範例

### 範例 1：基本占卜

```python
from liu_yao import six_yao_divination_from_date, format_liu_yao_display

# 執行占卜
yao_list, result = six_yao_divination_from_date(
    "111111",  # 乾為天
    "2025/12/01 19:00",
    [1]  # 第一爻為動爻
)

# 顯示結果
print(format_liu_yao_display(yao_list, show_shen_sha=True))
```

### 範例 2：手動八字輸入

```python
from liu_yao import six_yao_divination, format_liu_yao_display
from ba_zi_base import Pillar, BaZi

# 手動建立八字
bazi = BaZi(
    Pillar("乙", "巳"),  # 年：乙巳
    Pillar("丁", "亥"),  # 月：丁亥
    Pillar("甲", "子"),  # 日：甲子
    Pillar("甲", "戌")   # 時：甲戌
)

# 執行占卜
yao_list, result = six_yao_divination(
    "011111",  # 天風姤
    bazi,
    [1, 3]  # 第 1 和第 3 爻為動爻
)

# 顯示結果
print(format_liu_yao_display(yao_list))
```

### 範例 3：網頁介面

```python
from gradio_ui.ui_builder import create_ui

demo = create_ui()
demo.launch(share=True)  # 使用公開網址啟動
```

或使用便利腳本：

```bash
python run_gradio_ui.py
```

### 範例 4：使用新的模組化結構

```python
from gradio_ui.handlers.divination_handlers import (
    DivinationRequest,
    WesternDateInput,
    GanzhiDateInput,
    NameMethodInput,
    process_divination_request
)

# 使用資料類別建立占卜請求
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

# 處理請求
result = process_divination_request(request)
print(result)
```

## API 參考

### 核心函數

#### `six_yao_divination(main_hexagram_code: str, bazi: BaZi, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]`

執行完整的六爻占卜計算。

**參數**：
- `main_hexagram_code`：6 位數字串（'1'=陽，'0'=陰，由下往上）
- `bazi`：包含四柱的八字物件
- `changing_line_indices`：動爻位置清單（1-6）

**回傳值**：
- `yao_list`：6 個 `YaoDetails` 物件清單（位置 1-6，由下往上）
- `result_json`：包含卦象資訊與計算結果的字典

#### `six_yao_divination_from_date(main_hexagram_code: str, date_str: str, changing_line_indices: List[int]) -> Tuple[List[YaoDetails], dict]`

從日期字串建立八字並執行占卜的便利包裝器。

#### `format_liu_yao_display(yao_list: List[YaoDetails], show_shen_sha: bool = True, for_gradio: bool = False) -> str`

將結果格式化為傳統表格。

### 卦象代碼格式

卦象代碼是 6 位數字串，表示由下往上的爻線：
- `'1'` = 陽爻 - 實線
- `'0'` = 陰爻 - 虛線

範例：`"111111"` = 乾為天（全部陽爻）

### 動爻

動爻指定為位置清單（1-6）：
- `[1]` = 第一爻（最下方）為動爻
- `[1, 3, 5]` = 第 1、3、5 爻為動爻

當爻變化時：
- 陽 (1) → 陰 (0)
- 陰 (0) → 陽 (1)

## 開發指南

### 專案結構

本專案已重構以提升可維護性：

- **元件**：自包含的 UI 元件，各自管理狀態
- **處理器**：業務邏輯與 UI 元件分離
- **工具**：可重複使用的工具函數
- **配置**：集中化的配置與常數
- **靜態資源**：獨立的 CSS 和 JavaScript 檔案

### 執行測試

```bash
# 執行測試腳本
python test_liu_yao.py --date 2025/12/01 --time 19:00 --yao 1 1 1 1 1 1
```

### 程式碼風格

本專案遵循 Python PEP 8 風格指南。全程使用型別提示以提升程式碼清晰度和 IDE 支援。

## 注意事項與限制

### 選用相依套件

- **lunar_python**：僅在從西曆日期自動計算八字時需要。如未安裝，可使用干支曆手動輸入八字。

### 已知限制

1. **日期範圍**：從日期計算八字可能受限於 `lunar_python` 函式庫的能力。

2. **卦象映射**：目前支援標準易經系統的所有 64 卦。

3. **顯示格式化**：終端機顯示假設使用等寬字型以正確對齊。部分終端機可能無法正確渲染中文字元。

### 從舊版程式碼遷移

原始的 `gradio_ui.py`（2332 行）已重構為模組化套件結構。舊版檔案保留在儲存庫中供參考。新結構提供：

- 更好的可維護性
- 更容易測試
- 更清楚的關注點分離
- 可重複使用的元件

要使用新結構，請從 `gradio_ui` 套件匯入：

```python
# 舊方式（仍可使用但已棄用）
from gradio_ui import create_ui

# 新方式（推薦）
from gradio_ui.ui_builder import create_ui
```

## 授權

本專案僅供教育和研究用途。

## 貢獻

歡迎貢獻！請確保程式碼遵循現有風格並包含適當的文件。

## 致謝

本實作基於傳統六爻排盤原理，並從 C++23 模組實作轉換而來。

