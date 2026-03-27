import datetime,json,time,os
from pathlib import Path
from urllib import error,parse,request

CLIENT_ID = os.environ.get('TDX_CLIENT_ID','')
CLIENT_SECRET = os.environ.get('TDX_CLIENT_SECRET','')

AUTH_URL = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
GENERAL_TIMETABLE_URL = 'https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/GeneralTrainTimetable?%24format=JSON'
DAILY_TIMETABLE_URL_TEMPLATE = 'https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/DailyTrainTimetable/TrainDate/{train_date}?%24format=JSON'
DATA_DIR = Path('data')


def fetch_token() -> str | None:
    form_data = parse.urlencode(
        {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
    ).encode('utf-8')

    req = request.Request(AUTH_URL,data=form_data,method='POST')
    req.add_header('Content-Type','application/x-www-form-urlencoded')

    try:
        with request.urlopen(req,timeout=15) as resp:
            payload = resp.read().decode('utf-8')
            token_payload = json.loads(payload)
            access_token = token_payload.get('access_token')
            if not access_token:
                print({'error': 'Missing access_token','detail': token_payload})
                return None
            return access_token
    except error.HTTPError as e:
        detail = e.read().decode('utf-8',errors='ignore')
        print({'error': f'HTTP {e.code}','detail': detail})
        return None
    except error.URLError as e:
        print({'error': 'Network error','detail': str(e.reason)})
        return None


def fetch_json(
    url: str,
    headers: dict[str,str],
    timeout: int = 60,
    max_retries: int = 3,
) -> dict | list | None:
    for attempt in range(max_retries + 1):
        req = request.Request(url,headers=headers,method='GET')
        try:
            with request.urlopen(req,timeout=timeout) as resp:
                payload = resp.read().decode('utf-8')
                return json.loads(payload)
        except error.HTTPError as e:
            detail = e.read().decode('utf-8',errors='ignore')
            if e.code == 429 and attempt < max_retries:
                retry_after = e.headers.get('Retry-After')
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else (attempt + 1) * 2
                print({'warning': 'Rate limit hit','url': url,'wait_seconds': wait_seconds,'attempt': attempt + 1})
                time.sleep(wait_seconds)
                continue
            print({'error': f'HTTP {e.code}','url': url,'detail': detail})
            return None
        except error.URLError as e:
            print({'error': 'Network error','url': url,'detail': str(e.reason)})
            return None
        except json.JSONDecodeError as e:
            print({'error': 'Invalid JSON response','url': url,'detail': str(e)})
            return None

    return None


def download_timetable(access_token: str,days: int = 7) -> None:
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept': 'application/json',
    }
    DATA_DIR.mkdir(parents=True,exist_ok=True)

    print('Downloading TRA general timetable...')
    general_data = fetch_json(GENERAL_TIMETABLE_URL,headers)
    if general_data is not None:
        general_file = DATA_DIR / '台鐵定期時刻表.json'
        with general_file.open('w',encoding='utf-8') as f:
            json.dump(general_data,f,ensure_ascii=False,indent=2)
        print(f'Done. File saved: {general_file.as_posix()}')

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=days - 1)
    print(f'Downloading TRA daily timetables from {start_date} to {end_date}...')

    failed_dates: list[str] = []
    for offset in range(days):
        target_date = start_date + datetime.timedelta(days=offset)
        target_date_str = target_date.strftime('%Y-%m-%d')
        daily_url = DAILY_TIMETABLE_URL_TEMPLATE.format(train_date=target_date_str)

        if daily_file.exists():
            continue

        daily_data = fetch_json(daily_url,headers)
        if daily_data is None:
            failed_dates.append(target_date_str)
            continue

        daily_file = DATA_DIR / f'{target_date_str}.json'
        with daily_file.open('w',encoding='utf-8') as f:
            json.dump(daily_data,f,ensure_ascii=False,indent=2)
        print(f'Done. File saved:{daily_file.as_posix()}')

        if offset < days - 1:
            time.sleep(15)

    if failed_dates:
        print({'warning': 'Some daily timetable downloads failed','dates': failed_dates})
    else:
        print('All daily timetable files downloaded successfully.')


if __name__ == '__main__':
    token = fetch_token()
    if token:
        download_timetable(token)