import requests
import json
from datetime import datetime as dt, timedelta as td
from pytz import timezone

URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def get_exchange_rate(currency='EUR'):
    while True:
        with open('exchange_rate.json', encoding='utf8') as file:
            data = json.load(file)
        last_update = dt.fromisoformat(data["Timestamp"])
        now = dt.now(timezone(zone='Asia/Vladivostok'))
        if now - last_update > td(hours=1, seconds=20):
            print(f"dt = {now - last_update} | updating")
            write_data()
            #
            with open('exchange_rate.json', encoding='utf8') as file:
                data = json.load(file)
        euro_exchange_rate = float(data['Valute'][currency]['Value'])
        print(data['Date'], data["Timestamp"], sep=' | ')
        return euro_exchange_rate


def write_data():
    data = requests.get(URL)
    if data.status_code == 200:
        print("Getting data from server. last update at:",
              f"{dt.fromisoformat(data.json()['Timestamp']):%d.%m %H:%M}")
        with open("exchange_rate.json", "w", encoding="utf8") as file:
            json.dump(data.json(), file)


if __name__ == '__main__':
    print(f"Курс евро равен {get_exchange_rate()}")
