import requests, asyncio

from data_base import sqlite_db
from create_bot import dp, bot


async def return_answer_user(element):
    sqlite_db.update_order(id=element[0])
    print(element)
    await asyncio.create_task(bot.send_message(chat_id=element[7], text=f"Mонета {element[1]} достигла уровня цены в {element[2]} USD"))


def track_the_cost(currency_name: str):
    key = "https://api.binance.com/api/v3/ticker/price?symbol="
    url = "".join([key, currency_name.upper(), "USDT"])
    data = requests.get(url).json()
    print(data)
    if data.get('price', None):
        return round(float(data['price']), 2)
    return None


async def tracking_coin():
    response_data = sqlite_db.read_distinct_coin_name()
    data_with_current_price = sqlite_db.read_coins_names(response_data)
    data = sqlite_db.read_tracking()
    for element in data:
        print(data_with_current_price[element[1]], element[2], element[3])
        if data_with_current_price[element[1]] >= element[2] and element[3]:
            await return_answer_user(element=element)
        if data_with_current_price[element[1]] <= element[2] and not element[3]:
            await return_answer_user(element=element)
