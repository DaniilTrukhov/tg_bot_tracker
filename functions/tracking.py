import requests
from data_base import sqlite_db


def track_the_cost(currency_name: str):
    key = "https://api.binance.com/api/v3/ticker/price?symbol="
    url = "".join([key, currency_name.upper(), "USDT"])
    print(url)
    data = requests.get(url).json()
    print(data)
    if data.get('price', None):
        return round(float(data['price']), 2)
    return None


def tracking_coin():
    data = sqlite_db.read_coins_names()
    g_data = dict()
    print(data)
    for element in data:
        print(element)
        g_data[element] = track_the_cost(element)
    print(g_data)