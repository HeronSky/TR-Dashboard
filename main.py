import json,folium,branca.colormap as cm,streamlit as st,pandas as pd
from streamlit_folium import st_folium

st.set_page_config(page_title="TR MAP",layout="wide")
st.sidebar.title("地圖設定")
days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
selected_day = st.sidebar.selectbox("選擇日期", days)
st.title(f"TR MAP ({selected_day})")

m = folium.Map(location=[23.5,121.0],zoom_start=7,tiles="CartoDB positron")

with open("data/台鐵全部時刻表.json",'r',encoding='utf-8') as f:
    schedule_data = json.load(f)

TimeTables = {}
StationInfo = {}
id_name_map = {}

for timetable in schedule_data['TrainTimetables']:
    if timetable['ServiceDay'][selected_day] == 0:
        continue

    train_info = timetable['TrainInfo']
    train_no = train_info['TrainNo']
    terminal_station = train_info['EndingStationName']['Zh_tw']
    direction = train_info['Direction']
    train_type = train_info['TrainTypeName']['Zh_tw']

    if "柴聯" in train_type:
        train_type = "柴聯自強號"
    elif "推拉式" in train_type:
        train_type = "PP自強號"
    else :
        train_type = train_type.replace("(3000)", "3000")
        train_type = train_type.split("(")[0]
    


    if direction == 0 or direction == "0":
        direction_text = "順行"
    else:
        direction_text = "逆行"

    for stop in timetable['StopTimes']:
        time = time = stop.get('DepartureTime', stop.get('ArrivalTime'))
        station_name = stop['StationName']['Zh_tw']
        station_id = stop['StationID']
        id_name_map[station_name] = station_id
        TimeTables[station_name] = TimeTables.get(station_name,0)+1
        
        if station_id not in StationInfo:
            StationInfo[station_id] = []
        
        info_dict = {
            "時間": time,"車種": train_type,"車次": train_no,"終點站": terminal_station,"方向": direction_text
        }
        StationInfo[station_id].append(info_dict)
        
print(TimeTables)


with open('data/車站基本資料.json','r',encoding='utf-8') as f:
    station_data = json.load(f)

for station in station_data:
    station_name = station['StationName']['Zh_tw']
    lat = station['StationPosition']['PositionLat']
    lon = station['StationPosition']['PositionLon']

    freq = TimeTables.get(station_name,0)
    if freq >= 150:
        color = 'red'
        radius = 6
    elif freq >= 100:
        color = 'orange'
        radius = 5
    elif freq >= 50:
        color = 'yellow'
        radius = 4
    elif freq > 0:
        color = 'green'
        radius = 3
    else: 
        continue
        
    folium.CircleMarker(
        location=[lat,lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        tooltip=station_name,
        popup=f"{station_name}: {freq} trains"
    ).add_to(m)


with open('data/台鐵線型.json','r',encoding='utf-8') as f:
    shape_data = json.load(f)

for shape in shape_data['Shapes']:
    wkt = shape['Geometry']
    wkt = wkt.replace('MULTILINESTRING','').replace('LINESTRING','')
    segments = wkt.split('), (')

    for segment in segments:
        clean_segment = segment.replace('(','').replace(')','')
        track_path = []

        for p in clean_segment.split(','):
            coords = p.strip().split()
            if len(coords) != 2:
                continue

            lon = float(coords[0])
            lat = float(coords[1])
            track_path.append([lat,lon])

        if len(track_path) >= 2:
            folium.PolyLine(
                locations=track_path,
                color='red',
                weight=2,
                opacity=0.5,
            ).add_to(m)

col1, col2 = st.columns([2, 1])
with col1:
    map_data = st_folium(m, width=700, height=500)
with col2:
    user_clicked_station = None

    if map_data and map_data.get("last_object_clicked_tooltip"):
        user_clicked_station = map_data["last_object_clicked_tooltip"]
    
    if user_clicked_station and user_clicked_station in id_name_map:
        clicked = id_name_map[user_clicked_station]
        if clicked in StationInfo:
            info_list = StationInfo[clicked]
            
            schedule_table = pd.DataFrame(info_list)
            schedule_table = schedule_table.sort_values(by="時間")
            st.write(f"### {user_clicked_station}站 時刻表")
            st.dataframe(schedule_table, hide_index=True, use_container_width=True, height=500)
    



