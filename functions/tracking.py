import requests


def track_the_cost(currency_name: str):
    key = "https://api.binance.com/api/v3/ticker/price?symbol="
    url = "".join([key, currency_name.upper(), "USDT"])
    print(url)
    data = requests.get(url).json()
    print(data)
    if data.get('price', None):
        return round(float(data['price']), 2)
    return None
