import json,folium
from datetime import date,timedelta
import networkx as nx
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="TR Dashboard",layout="wide",initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        [data-testid="stSidebar"] {
            min-width: 350px;
            max-width: 350px;
        }
        [data-testid="stAppViewContainer"],[data-testid="stMainBlockContainer"] {
            overflow: hidden !important;
        }
        [data-testid="collapsedControl"] {
        display: none !important;
        }
        section[data-testid="stSidebar"] {
        transform: translateX(0) !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(0) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def get_lang_value(name_obj,lang_key):
    if not isinstance(name_obj,dict):
        return ""
    return name_obj.get(lang_key) or name_obj.get("Zh_tw") or ""

def fix_name(name):
    return (name or "").replace("臺","台").replace("-環島","")

def sort_by_train_no(df,train_no_col):
    sorted_df = df.copy()
    sorted_df["__train_no_num"] = pd.to_numeric(sorted_df[train_no_col],errors="coerce")
    sorted_df = sorted_df.sort_values(by=["__train_no_num",train_no_col],na_position="last")
    return sorted_df.drop(columns=["__train_no_num"])

segment_freq = {}
segment_train_info = {}
segment_label_to_key = {}

st.sidebar.title("TR Dashboard")
if "use_english_data" not in st.session_state:
    st.session_state.use_english_data = False

st.sidebar.markdown("**Settings**" if st.session_state.use_english_data else "**設定**",)
lang_col1,lang_col2=st.sidebar.columns([1,1])
with lang_col1:
    st.write("Language:" if st.session_state.use_english_data else "語言：")
with lang_col2:
    lang=st.sidebar.radio("Lang",["中文","English"],horizontal=True,label_visibility="collapsed")
st.session_state.use_english_data=(lang=="English")

name_key = "En" if st.session_state.use_english_data else "Zh_tw"
today = date.today()
max_selectable_date = today + timedelta(days=6)
date_label = "Date:" if st.session_state.use_english_data else "日期："
selected_date = st.sidebar.date_input(
    date_label,
    value=today,
    min_value=today,
    max_value=max_selectable_date,
    format="YYYY/MM/DD",
)
selected_day = DAYS[selected_date.weekday()]
st.sidebar.divider()

PALETTE = {
    "line": "#3A3B4C",
    "station_border": "none",
    "tier_high": "#FF4B4B",
    "tier_mid_high": "#FFAA00",
    "tier_mid": "#FFD700",
    "tier_low": "#E0E0E0",
}

m = folium.Map(location=[23.5,121.0],zoom_start=9,tiles="CartoDB dark_matter nolabels")

map_name = m.get_name()
zoom_on_blank_click_js = f"""
<script>
(function() {{
    var map = {map_name};
    map.on('click',function(e) {{
        if (e.sourceTarget && e.sourceTarget instanceof L.Map) {{
            var maxZoom = map.getMaxZoom ? map.getMaxZoom() : 18;
            var nextZoom = Math.min(map.getZoom() + 1,maxZoom || 18);
            map.setView(e.latlng,nextZoom,{{animate: true}});
        }}
    }});
}})();
</script>
"""
m.get_root().add_child(folium.Element(zoom_on_blank_click_js))

date_str = selected_date.strftime("%Y-%m-%d")
file_path = f"data/{date_str}.json"

try:
    with open(file_path,"r",encoding="utf-8") as f:
        schedule_data = json.load(f)
except FileNotFoundError:
    warning_msg = f"Data error: No timetable found for {date_str}.Displaying regular timetable :/" if st.session_state.use_english_data else f"資料錯誤，查無{date_str}的時刻表：/ 將顯示定期時刻表。"
    st.warning(warning_msg)
    with open("data/台鐵定期時刻表.json","r",encoding="utf-8") as f:
        schedule_data = json.load(f)

if not isinstance(schedule_data,dict) or "TrainTimetables" not in schedule_data:
    warning_msg2 = f"Timetable format error for {date_str}. Displaying regular timetable " if st.session_state.use_english_data else f"{date_str}時刻表格式異常：/ 將顯示定期時刻表。"
    st.warning(warning_msg2)
    with open("data/台鐵定期時刻表.json","r",encoding="utf-8") as f:
        schedule_data = json.load(f)

time_tables = {}
station_info = {}
id_name_map = {}
path_cache = {}

G = nx.Graph()
with open("data/路線車站資料.json","r",encoding="utf-8") as f:
    line_data = json.load(f)

for line in line_data.get("StationOfLines",[]):
    stations = line.get("Stations",[])
    for i in range(len(stations)-1):
        sta1 = fix_name(stations[i]["StationName"]["Zh_tw"])
        sta2 = fix_name(stations[i+1]["StationName"]["Zh_tw"])
        if sta1 and sta2 and sta1 != sta2:
            G.add_edge(sta1,sta2)

for timetable in schedule_data.get("TrainTimetables",[]):
    train_info = timetable["TrainInfo"]
    train_no = train_info["TrainNo"]
    terminal_station = get_lang_value(train_info.get("EndingStationName",{}),name_key)
    direction = train_info["Direction"]
    train_type = get_lang_value(train_info.get("TrainTypeName",{}),name_key)

    if not st.session_state.use_english_data:
        if "柴聯" in train_type:
            train_type = "柴聯自強號"
        elif "推拉式" in train_type:
            train_type = "PP自強號"
        else:
            train_type = train_type.replace("(3000)","3000")
            train_type = train_type.split("(")[0]
    else:
        train_type = train_type.replace("(3000)","3000").split("(")[0]

    if direction == 0 or direction == "0":
        direction_text = "Forward" if st.session_state.use_english_data else "順行"
    else:
        direction_text = "Reverse" if st.session_state.use_english_data else "逆行"

    stops = timetable.get("StopTimes",[])

    for stop in stops:
        time = stop.get("DepartureTime",stop.get("ArrivalTime"))
        station_name = get_lang_value(stop.get("StationName",{}),name_key)
        station_id = stop["StationID"]

        id_name_map[station_name] = station_id
        time_tables[station_name] = time_tables.get(station_name,0) + 1

        if station_id not in station_info:
            station_info[station_id] = []

        info = {
            "時間" if not st.session_state.use_english_data else "Time": time,
            "車種" if not st.session_state.use_english_data else "TrainType": train_type,
            "車次" if not st.session_state.use_english_data else "TrainNo": train_no,
            "終點站" if not st.session_state.use_english_data else "Terminal": terminal_station,
            "方向" if not st.session_state.use_english_data else "Direction": direction_text,
        }
        station_info[station_id].append(info)

    # 線段密度：用路網最短路徑展開，處理快慢車跳站
    for i in range(len(stops)-1):
        a = fix_name(stops[i]["StationName"]["Zh_tw"])
        b = fix_name(stops[i+1]["StationName"]["Zh_tw"])
        if not a or not b or a == b:
            continue

        pair_key = tuple(sorted([a,b]))
        if pair_key not in path_cache:
            try:
                path_cache[pair_key] = nx.shortest_path(G,source=a,target=b)
            except (nx.NetworkXNoPath,nx.NodeNotFound):
                path_cache[pair_key] = None

        path = path_cache[pair_key]
        if not path:
            continue

        for j in range(len(path)-1):
            seg = tuple(sorted([path[j],path[j+1]]))
            segment_freq[seg] = segment_freq.get(seg,0) + 1

            row = {
                "車次" if not st.session_state.use_english_data else "TrainNo": train_no,
                "車種" if not st.session_state.use_english_data else "TrainType": train_type,
                "終點站" if not st.session_state.use_english_data else "Terminal": terminal_station,
                "方向" if not st.session_state.use_english_data else "Direction": direction_text,
            }
            if seg not in segment_train_info:
                segment_train_info[seg] = []
            segment_train_info[seg].append(row)

with open("data/台鐵線型.json","r",encoding="utf-8") as f:
    shape_data = json.load(f)

for shape in shape_data["Shapes"]:
    wkt = shape["Geometry"]
    wkt = wkt.replace("MULTILINESTRING","").replace("LINESTRING","")
    segments = wkt.split("), (")

    for segment in segments:
        clean_segment = segment.replace("(","").replace(")","")
        track_path = []

        for p in clean_segment.split(","):
            coords = p.strip().split()
            if len(coords) != 2:
                continue

            lon = float(coords[0])
            lat = float(coords[1])
            track_path.append([lat,lon])

        if len(track_path) >= 2:
            folium.PolyLine(
                locations=track_path,
                color=PALETTE["line"],
                weight=2.2,
                opacity=0.55,
            ).add_to(m)

with open("data/車站基本資料.json","r",encoding="utf-8") as f:
    station_data = json.load(f)

station_display_map = {}
for station in station_data:
    zh = fix_name(station["StationName"]["Zh_tw"])
    en = station.get("StationName",{}).get("En","")
    station_display_map[zh] = {
    "zh": zh,
    "en": en if en else zh,
    }

station_coords_zh = {}
for station in station_data:
    zh = fix_name(station["StationName"]["Zh_tw"])
    lat = station["StationPosition"]["PositionLat"]
    lon = station["StationPosition"]["PositionLon"]
    station_coords_zh[zh] = [lat,lon]

for (s1,s2),freq in segment_freq.items():
    if s1 not in station_coords_zh or s2 not in station_coords_zh:
        continue

    if freq >= 150:
        color,weight = "#e74c3c",5
    elif freq >= 100:
        color,weight = "#e67e22",4
    elif freq >= 50:
        color,weight = "#f1c40f",3
    else:
        color,weight = "#2ecc71",2

    station1 = station_display_map.get(s1,{}).get("en" if st.session_state.use_english_data else "zh",s1)
    station2 = station_display_map.get(s2,{}).get("en" if st.session_state.use_english_data else "zh",s2)
    trains = "trains" if st.session_state.use_english_data else "班"
    tooltip_text = f"{station1} ＝ {station2} : {freq} {trains}"
    segment_label_to_key[tooltip_text] = (s1,s2)

    folium.PolyLine(
        locations=[station_coords_zh[s1],station_coords_zh[s2]],
        color=color,
        weight=weight,
        opacity=0.75,
        tooltip=tooltip_text,
    ).add_to(m)

for station in station_data:
    station_name = get_lang_value(station.get("StationName",{}),name_key)
    lat = station["StationPosition"]["PositionLat"]
    lon = station["StationPosition"]["PositionLon"]

    freq = time_tables.get(station_name,0)

    if freq >= 150:
        color,vis_radius = PALETTE["tier_high"],4.5
    elif freq >= 100:
        color,vis_radius = PALETTE["tier_mid_high"],4.0
    elif freq >= 50:
        color,vis_radius = PALETTE["tier_mid"],3.5
    elif freq > 0:
        color,vis_radius = PALETTE["tier_low"],3.0
    else:
        continue

    folium.CircleMarker(
        location=[lat,lon],
        radius=vis_radius,
        color=color,
        weight=0,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        interactive=False,
    ).add_to(m)

    folium.CircleMarker(
        location=[lat,lon],
        radius=17,
        color="none",
        weight=0,
        fill=True,
        fill_color="white",
        fill_opacity=0.0,
        tooltip=station_name,
    ).add_to(m)

clicked_tooltip = None
map_data = st_folium(m,use_container_width=True,height=900)
if map_data and map_data.get("last_object_clicked_tooltip"):
    clicked_tooltip = map_data["last_object_clicked_tooltip"]

if clicked_tooltip and clicked_tooltip in id_name_map:
    with st.sidebar:
        clicked = id_name_map[clicked_tooltip]
        if clicked in station_info:
            info_list = station_info[clicked]

            schedule_table = pd.DataFrame(info_list)
            col_time = "Time" if st.session_state.use_english_data else "時間"
            col_direction = "Direction" if st.session_state.use_english_data else "方向"
            all_option = "All" if st.session_state.use_english_data else "全部"
            option_forward = "Forward" if st.session_state.use_english_data else "順行"
            option_reverse = "Reverse" if st.session_state.use_english_data else "逆行"
            
            st.markdown(f"## {clicked_tooltip}")
            st.markdown(
                f"**{len(info_list)} trains**" if st.session_state.use_english_data else f"**{len(info_list)} 班列車**"
            )
            choice = st.selectbox(
                "Direction:" if st.session_state.use_english_data else "方向：",
                [all_option,option_forward,option_reverse],
            )
            if choice != all_option:
                schedule_table = schedule_table[schedule_table[col_direction] == choice]
            schedule_table = schedule_table.sort_values(by=col_time)
            st.dataframe(schedule_table,hide_index=True,width="stretch",height=500)
elif clicked_tooltip and clicked_tooltip in segment_label_to_key:
    with st.sidebar:
        seg = segment_label_to_key[clicked_tooltip]
        rows = segment_train_info.get(seg,[])

        st.markdown(f"## {clicked_tooltip}")
        st.markdown(
            f"**{len(rows)} trains**" if st.session_state.use_english_data else f"**{len(rows)} 班列車**"
        )
        if rows:
            df_seg = pd.DataFrame(rows)
            sort_col = "TrainNo" if st.session_state.use_english_data else "車次"
            st.dataframe(sort_by_train_no(df_seg,sort_col),hide_index=True,width="stretch",height=500)





