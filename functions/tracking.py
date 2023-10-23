import requests, asyncio, aiohttp, time

from data_base import sqlite_db
from create_bot import bot

data_with_names = dict()


async def install_names_dict():
    global data_with_names
    new_data_with_names = await sqlite_db.read_distinct_coin_name()
    if len(new_data_with_names) != len(data_with_names):
        data_with_names = new_data_with_names


async def return_answer_user(element):
    sqlite_db.update_order(id=element[0])
    print(element)
    await asyncio.create_task(bot.send_message(chat_id=element[7], text=f"Mонета {element[1]} достигла уровня цены в {element[2]} USD"))


async def track_the_cost(currency_name: str):
    key = "https://api.binance.com/api/v3/ticker/price?symbol="
    url = "".join([key, currency_name.upper(), "USDT"])
    data = requests.get(url).json()
    print(data)
    if data.get('price', None):
        return float(data['price'])
    return None


async def track_cost(currency_name: str):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={currency_name.upper()}USDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            print(data)
            return float(data['price']) if 'price' in data else None


async def check_price(coin_dict):
    start_time = time.time()
    for coin_name in coin_dict:
        coin_dict[coin_name] = await track_cost(coin_name)
    print(time.time() - start_time)
    return coin_dict


async def tracking_coin():
    global data_with_names
    data_with_current_price = await check_price(data_with_names)
    data = sqlite_db.read_tracked()
    for element in data:
        if data_with_current_price[element[1]] >= element[2] and element[3]:
            await return_answer_user(element=element)
        if data_with_current_price[element[1]] <= element[2] and not element[3]:
            await return_answer_user(element=element)
