# TR-Dashboard 

[English](#english) | [中文](#中文)

---
<div id="english"></div>

TR-Dashboard is a tool based on Streamlit, making the timetable of Taiwan Railways more visualize and interactive.After selecting the date, user can click on any station on the map to display the timetable of that day

The timetable data is automatically update with GitHub Actions and TDX API. Different colors on the map represent the number of train stops at the station on that day.

## How to use?
Click station for station timetable, click segment for trains on that segment.

## Route Density  
- **<font color=#e74c3c>Red</font>**: More than 150 train stops on the route on that day
- **<font color=#e67e22>Orange</font>**: 100 ~ 150 train stops on the route on that day
- **<font color=#f1c40f>Yellow</font>**: 50 ~ 100 train stops on the route on that day
- **<font color=#2ecc71>Green</font>**: Fewer than 50 train stops on the route on that day

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

## 互動方式
點擊車站可看該站列車，點擊路段可看該路段通過列車。

## 路段車流量
- **<font color=#e74c3c>紅色</font>**：該路段當日停靠的車輛數量大於150列
- **<font color=#e67e22>橙色</font>**：該路段當日停靠的車輛數量在100列～150列
- **<font color=#f1c40f>黃色</font>**：該路段當日停靠的車輛數量在50列～100列
- **<font color=#2ecc71>綠色</font>**：該路段當日停靠的車輛數量小於50列

## 地圖標示
- **<font color=#FF4B4B>紅色</font>**：該車站當日停靠的車輛數量大於150列
- **<font color=#FFAA00>橙色</font>**：該車站當日停靠的車輛數量在100列～150列
- **<font color=#FFD700>綠色</font>**：該車站當日停靠的車輛數量在50列～100列
- **<font color=#E0E0E0>灰色</font>**：該車站當日停靠的車輛小於50列

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