# TR-Dashboard 

[English](#english) | [中文](#中文)

---
<div id="english"></div>

TR-Dashboard is a tool based on Streamlit, making the timetable of Taiwan Railways more visualize and interactive.After selecting the date, user can click on any station on the map to display the timetable of that day

The timetable data is automatically update with GitHub Actions and TDX API. Different colors on the map represent the number of train stops at the station on that day.

## Map Legend
- **<font color=#FF4B4B>Red</font>**: More than 150 train stops at the station on that day
- **<font color=#FFAA00>Orange</font>**: 100 ~ 150 train stops at the station on that day
- **<font color=#FFD700>Green</font>**: 50 ~ 100 train stops at the station on that day
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

TR-Dashboard 是一個基於 Streamlit 的互動式台鐵時刻表。使用者在選擇日期後並且在地圖上點擊車站，側邊欄將會顯示當日的時刻表，時刻表資料是透過 GitHub Actions 取得 TDX平台 的資料進行自動更新。地圖上的不同的顏色代表該車站當日的停靠車輛的數量。

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