from pathlib import Path
from datetime import date, timedelta
import json
import requests
import os
import time

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
TRA_BASE = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA"

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return value

def get_access_token(client_id: str, client_secret: str) -> str:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def get_json(url: str, token: str, retries: int = 3, sleep_sec: int = 2):
    headers = {"authorization": f"Bearer {token}"}
    last_err: Exception | None = None

    for _ in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
            time.sleep(sleep_sec)

    if last_err is not None:
        raise last_err
    raise RuntimeError("Request failed without captured exception")

def save_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done. File saved: {path.as_posix()}")

def fetch_static_files(token: str):
    station_url = f"{TRA_BASE}/Station?$format=JSON"
    train_type_url = f"{TRA_BASE}/TrainType?$format=JSON"
    timetable_url = f"{TRA_BASE}/GeneralTimetable?$format=JSON"

    station_data = get_json(station_url, token)
    train_type_data = get_json(train_type_url, token)
    timetable_data = get_json(timetable_url, token)

    save_json(DATA_DIR / "台鐵車站.json", station_data)
    save_json(DATA_DIR / "台鐵車種.json", train_type_data)
    save_json(DATA_DIR / "台鐵定期時刻表.json", timetable_data)

def prune_expired_daily_files(start_date: date, end_date: date):
    keep = {
        f"台鐵每日時刻表_{(start_date + timedelta(days=i)):%Y-%m-%d}.json"
        for i in range((end_date - start_date).days + 1)
    }
    for f in DATA_DIR.glob("台鐵每日時刻表_*.json"):
        if f.name not in keep:
            f.unlink()
            print(f"Removed expired file: {f.as_posix()}")

def fetch_daily_files(token: str, start_date: date, end_date: date):
    print(f"Downloading TRA daily timetables from {start_date} to {end_date}...")
    for i in range((end_date - start_date).days + 1):
        d = start_date + timedelta(days=i)
        daily_file = DATA_DIR / f"台鐵每日時刻表_{d:%Y-%m-%d}.json"
        if daily_file.exists():
            print(f"Skip existing file: {daily_file.as_posix()}")
            continue
        url = f"{TRA_BASE}/DailyTrainTimetable/TrainDate/{d:%Y-%m-%d}?$format=JSON"
        payload = get_json(url, token)
        save_json(daily_file, payload)

def main():
    client_id = get_required_env("TDX_CLIENT_ID")
    client_secret = get_required_env("TDX_CLIENT_SECRET")
    token = get_access_token(client_id, client_secret)

    fetch_static_files(token)

    start = date.today()
    end = start + timedelta(days=6)
    prune_expired_daily_files(start, end)
    fetch_daily_files(token, start, end)

if __name__ == "__main__":
    main()