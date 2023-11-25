import requests
import asyncio
import aiohttp
import time

from data_base import sqlite_db
from create_bot import bot

data_with_names = dict()
key = "https://api.binance.com/api/v3/ticker/price?symbol="


async def install_names_dict() -> None:
    """
        Asynchronously fetches distinct coin names from the database and updates the global data_with_names dictionary.
    """
    global data_with_names
    new_data_with_names = await sqlite_db.read_distinct_coin_name()
    if len(new_data_with_names) != len(data_with_names):
        data_with_names = new_data_with_names


async def return_answer_user(element) -> None:
    """
        Asynchronously updates the order in the database and sends a message
        to the user about the coin reaching a specified price level.

        Args:
            element (tuple): A tuple representing the order information.
    """
    sqlite_db.archived_order(user_id=element[0])
    await asyncio.create_task(bot.send_message(
        chat_id=element[7],
        text=f"Mонета {element[1]} достигла уровня цены в {element[2]} USD")
    )


async def check_the_cost(currency_name: str) -> float or None:
    """
        Asynchronously tracks the cost of a cryptocurrency using synchronous requests.

        Args:
            currency_name (str): The abbreviation of the cryptocurrency.

        Returns:
            float: The current price of the cryptocurrency.
    """
    url = "".join([key, currency_name.upper(), "USDT"])
    data = requests.get(url).json()
    if data.get('price', None):
        return float(data['price'])
    return None


async def check_cost(currency_name: str) -> float:
    """
        Asynchronously tracks the cost of a cryptocurrency using aiohttp for better concurrency.

        Args:
            currency_name (str): The abbreviation of the cryptocurrency.

        Returns:
            float: The current price of the cryptocurrency.
    """
    url = "".join([key, currency_name.upper(), "USDT"])
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        async with session.get(url) as response:
            data = await response.json()
            return float(data['price']) if 'price' in data else None


async def check_price(coin_dict: dict) -> dict:
    """
        Asynchronously checks the current price of multiple cryptocurrencies.

        Args:
            coin_dict (dict): A dictionary containing cryptocurrency abbreviations.

        Returns:
            dict: A dictionary containing cryptocurrency abbreviations as keys and their corresponding current prices.
    """
    start_time = time.time()
    for coin_name in coin_dict:
        coin_dict[coin_name] = await check_cost(coin_name)
    print(round(time.time() - start_time, 2), "sec", sep="")
    return coin_dict


async def tracking_coin() -> None:
    """
        Asynchronously tracks the prices of tracked cryptocurrencies
        and sends messages to users if specified price levels are reached.
    """
    global data_with_names
    data_with_current_price = await check_price(data_with_names)
    data = sqlite_db.read_tracked()
    for element in data:
        if data_with_current_price[element[1]] >= element[2] and element[3]:
            await return_answer_user(element=element)
        if data_with_current_price[element[1]] <= element[2] and not element[3]:
            await return_answer_user(element=element)
