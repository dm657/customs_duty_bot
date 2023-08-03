import requests
import json
from datetime import datetime as dt, timedelta as td
from pytz import timezone
from aiogram.types import Message
from data import T_ZONE, EXCHANGE_RATE_SAMPLE

URL = "https://www.cbr-xml-daily.ru/daily_json.js"
# URL = 'https://yesno.wtf/api?force=yes'


def add_user(d: dict, update: Message):
    d[update.from_user.id] = {
        'volume': 0
        , 'y': ''
        , 'price': 0
        , 'status': 'w8_year'
        }
    return True


def get_exchange_rate(d: dict, currency='EUR', json_file='exchange_rate.json'):
    last_connect_try = d.get('last_connect_try', dt.fromisoformat("2000-01-01T00:00:00+03:00"))
    time_now = dt.now(timezone(zone=T_ZONE))
    if time_now - last_connect_try < td(hours=1):
        return d['Valute'][currency]['Value']
    else:
        try:
            data_from_http = requests.get(URL)
            assert data_from_http.status_code == 200
            print("Got data", data_from_http.status_code)
            print()
        except (Exception, ConnectionError, ConnectionRefusedError):
            pass
        else:
            # print(type(data_from_http.json()))
            d = data_from_http.json()
            d['last_connect_try'] = time_now
            with open(json_file, "w", encoding="utf8") as file:
                file.write(data_from_http.text)
                # json.dump(d, file)
            curr_exchange_rate = float(d['Valute'][currency]['Value'])
            return curr_exchange_rate
        try:
            with open(json_file, encoding='utf8') as file:
                d = json.load(file)
            return d['Valute'][currency]['Value']
        except FileNotFoundError:
            return 0


        # except FileNotFoundError:



        # if write_data() == 'OK':
        #     with open(json_file, encoding='utf8') as file:
        #         data = json.load(file)
        # else:
        #     return 0

    # last_update_on_server = dt.fromisoformat(data["Timestamp"])
    # now = dt.now(timezone(zone=T_ZONE))
    # if (delta := now - last_update_on_server) > td(hours=1, seconds=20):
    #     print(f"dt = {round(delta.seconds/3600, 2)} hours | updating")
    #     write_data()
    #     #
    #     with open(json_file, encoding='utf8') as file:
    #         data = json.load(file)
    # euro_exchange_rate = float(data['Valute'][currency]['Value'])
    # # print(data['Date'], data["Timestamp"], sep=' | ')
    # return euro_exchange_rate


def write_data(url=URL):
    try:
        data = requests.get(url)
        if data.status_code == 200:
            print("Getting data from server. last update at:",
                  f"{dt.fromisoformat(data.json()['Timestamp']):%d.%m %H:%M}")
            with open("exchange_rate.json", "w", encoding="utf8") as file:
                json.dump(data.json(), file)
            return 'OK'
    except (Exception, ConnectionError, ConnectionRefusedError):
        pass


if __name__ == '__main__':
    # print(write_data(URL))
    qwe = {}
    print(f"Курс евро равен {get_exchange_rate(qwe)}")
