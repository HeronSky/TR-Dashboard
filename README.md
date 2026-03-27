# TR-Dashboard 

[English](#english) | [中文](#中文)

---
<div id="english"></div>

TR-Dashboard is an interactive Taiwan Railway timetable visualization tool built with Streamlit. After selecting a date, users can click a station to view that station's timetable for the day. Timetable data is automatically updated through GitHub Actions and the TDX API. Different colors indicate the number of trains stopping at each station on the selected date.

## Map Legend
- **<font color=#FF4B4B>Red</font>**: More than 150 train stops at the station on that day
- **<font color=#FFAA00>Orange</font>**: 100 to 150 train stops at the station on that day
- **<font color=#FFD700>Green</font>**: 50 to 100 train stops at the station on that day
- **<font color=#E0E0E0>Gray</font>**: Fewer than 50 train stops at the station on that day

## File Structure
```text
├── main.py
├── api_tra.py
├── requirements.txt
├── data/
└── .github/workflows/
    └── update.yml
```

## Setup and Run
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app
   ```bash
   streamlit run main.py
   ```

## Notes
- The automation workflow and part of the code in this project were developed with AI assistance.

---

<div id="中文"></div>

# TR-Dashboard 臺鐵儀表板
是一個基於 Streamlit 的台鐵時刻表互動式視覺化工具。使用者在選擇日期後，可以點擊車站來顯示該車站的當日時刻表，時刻表資料是透過 GitHub Actions 與 TDX API 進行自動更新。不同的顏色代表該車站當日的停靠車輛數量。

## 地圖標示
- **<font color=#FF4B4B>紅色</font>**：該車站當日停靠的車輛數量大於150列
- **<font color=#FFAA00>橙色</font>**：該車站當日停靠的車輛數量在100列～150列
- **<font color=#FFD700>綠色</font>**：該車站當日停靠的車輛數量在50列～100列
- **<font color=#E0E0E0>灰色</font>**：該車站當日沒有停靠的車輛小於50列

## 檔案結構
```text
├── main.py
├── api_tra.py
├── requirements.txt
├── data/
└── .github/workflows/
    └── update.yml
```

## 執行與安裝
1. 安裝套件
   ```bash
   pip install -r requirements.txt
   ```
2. 執行應用程式
   ```bash
   streamlit run main.py
   ```

## 備註
- 本專案的自動化邏輯與部分程式碼是在 AI 的協助下完成開發。