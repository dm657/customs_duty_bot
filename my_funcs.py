import requests
import json
from datetime import datetime as dt, timedelta as td
from pytz import timezone
from aiogram.types import Message
from aiogram import F

URL = "https://www.cbr-xml-daily.ru/daily_json.js"
# URL = 'https://yesno.wtf/api?force=yes'


def add_user(d: dict, update: Message):
    if update.from_user.id not in d:
        d[update.from_user.id] = {
            'volume': 0
            , 'y': ''
            , 'price': 0
            # , 'status': None
            }
        return True


def get_exchange_rate(currency='EUR'):
    try:
        with open('exchange_rate.json', encoding='utf8') as file:
            data = json.load(file)
    except FileNotFoundError:
        if write_data() == 'OK':
            with open('exchange_rate.json', encoding='utf8') as file:
                data = json.load(file)
        else:
            return 0

    last_update_on_server = dt.fromisoformat(data["Timestamp"])
    now = dt.now(timezone(zone='Asia/Vladivostok'))
    if (delta := now - last_update_on_server) > td(hours=1, seconds=20):
        print(f"dt = {round(delta.seconds/3600, 2)} hours | updating")
        write_data()
        #
        with open('exchange_rate.json', encoding='utf8') as file:
            data = json.load(file)
    euro_exchange_rate = float(data['Valute'][currency]['Value'])
    # print(data['Date'], data["Timestamp"], sep=' | ')
    return euro_exchange_rate


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
    print(write_data(URL))
    print(f"Курс евро равен {get_exchange_rate('EUR')}")
