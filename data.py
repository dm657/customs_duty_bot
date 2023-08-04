RANGES = (1000, 1500, 1800, 2300, 3000)
STAVKI = {'менее 3': (2.5, 3.5, 5.5, 7.5, 15, 20),
          'от 3 до 5': (3.6, 3, 2.7, 2.5, 1.7, 1.5),
          'старше 5': (5.7, 5, 4.8, 3.5, 3.2, 3)}
T_ZONE = 'Asia/Vladivostok'

INIT_MSG = """Для начала
Укажите возраст а/м"""
RES_SAMPLE_RU = """Для а/м {} лет
с двигателем объемом {} См³
пошлина составит {} €
что по текущему курсу [1€={}]
составит {} ₽
"""

EXCHANGE_RATE_SAMPLE = {"Date": "2000-01-01T00:00:00+03:00",
                        "PreviousDate": "2000-01-01T00:00:00+03:00",
                        "PreviousURL": "//www.cbr-xml-daily.ru/archive/2023/08/02/daily_json.js",
                        "Timestamp": "2000-01-01T00:00:00+03:00",
                        "Valute": {"EUR": {
                            "ID": "R01239",
                            "NumCode": "978",
                            "CharCode": "EUR",
                            "Nominal": 1,
                            "Name": "Евро",
                            "Value": 0,
                            "Previous": 0
                        }
                        }
                        }

if __name__ == "__main__":
    pass
