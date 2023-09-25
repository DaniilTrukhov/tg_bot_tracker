import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext

from functions import tracking


def start_bd():
    global base, cursor
    base = sqlite3.connect('tgb_base.db')
    cursor = base.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id INTEGER PRIMARY KEY,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            is_prime BOOLEAN DEFAULT False
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_name TEXT NOT NULL,
            target_price REAL NOT NULL,
            uptrend BOOLEAN NOT NULL,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_date DATETIME DEFAULT NULL,
            archived BOOLEAN DEFAULT FALSE,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    base.commit()


async def create_user(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (telegram_user_id, is_prime) VALUES (?, ?)", (message.from_user.id, False))
    base.commit()


async def create_tracking(user_id: int, state: FSMContext):
    async with state.proxy() as data:
        coin_name = data["coin_name"]
        target_price = data["target_price"]
        if data["price_coin"] > data["target_price"]:
            uptrend = False
        else:
            uptrend = True
    cursor.execute("INSERT INTO orders (coin_name, target_price, uptrend, user_id) VALUES (?, ?, ?, ?)",
                   (coin_name, target_price, uptrend, user_id))
    base.commit()


def read_tracking(user_id):
    cursor.execute("SELECT * FROM orders WHERE user_id = ? AND archived = FALSE", (user_id,))
    orders = cursor.fetchall()

    for order in orders:
        print(order)


def read_coins_names():
    cursor.execute("SELECT DISTINCT coin_name FROM orders")
    distinct_coin_names = cursor.fetchall()
    coin_dict = dict()
    for coin_name in distinct_coin_names:
        coin_dict[coin_name[0]] = tracking.track_the_cost(coin_name[0])
    return coin_dict