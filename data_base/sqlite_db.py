import sqlite3

from typing import List


def execute_query(query, parameters=None)  -> None:
    """
        Executes a SQL query on the SQLite database.

        Args:
            query (str): The SQL query to be executed.
            parameters (tuple): Optional parameters to be passed to the query.

        Raises:
            Exception: An exception is raised in case of an error during query execution.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
    finally:
        base.close()


def start_bd()  -> None:
    """
        Initializes the SQLite database and creates necessary tables if they don't exist.
    """
    first_query = '''
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id INTEGER PRIMARY KEY,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            is_prime BOOLEAN DEFAULT False
        )
    '''
    execute_query(query=first_query)
    sesond_query = '''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_name TEXT NOT NULL,
            target_price REAL NOT NULL,
            uptrend BOOLEAN NOT NULL,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_date DATETIME DEFAULT NULL,
            archived BOOLEAN DEFAULT FALSE,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )'''
    execute_query(query=sesond_query)


async def create_user(user_id) -> None:
    """
        Asynchronously inserts or ignores the user into the 'users' table.

        Args:
            user_id (int): The Telegram user ID.
    """
    query = "INSERT OR IGNORE INTO users (telegram_user_id, is_prime) VALUES (?, ?)"
    execute_query(query=query, parameters=(user_id, False))


async def create_tracking(user_id: int, data: dict)  -> None:
    """
        Asynchronously inserts a tracking order into the 'orders' table.

        Args:
            user_id (int): The Telegram user ID.
            data (dict): A dictionary containing tracking order information.
    """
    coin_name = data["coin_name"]
    target_price = data["target_price"]
    if data["price_coin"] > data["target_price"]:
        uptrend = False
    else:
        uptrend = True
    query = "INSERT INTO orders (coin_name, target_price, uptrend, user_id) VALUES (?, ?, ?, ?)"
    execute_query(query=query, parameters=(coin_name, target_price, uptrend, user_id))


def read_tracked() -> List:
    """
        Reads and returns the active tracking orders from the 'orders' table.

        Returns:
            list: A list of tuples representing active tracking orders.
    """
    try:
        base = sqlite3.connect('tgb_base.db', isolation_level=None)
        cursor = base.cursor()
        cursor.execute("SELECT * FROM orders WHERE archived = FALSE")
        orders = cursor.fetchall()
        return orders
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
    finally:
        base.close()


def update_order(id: int) -> None:
    """
        Updates the tracking order status to 'archived' with the end date.

        Args:
            id (int): The ID of the tracking order to be updated.
    """
    query = "UPDATE orders SET archived = TRUE, end_date = CURRENT_TIMESTAMP WHERE id = ?;"
    execute_query(query=query, parameters=(id,))


async def read_distinct_coin_name() -> dict:
    """
        Asynchronously reads distinct coin names from the 'orders' table.

        Returns:
            dict: A dictionary with distinct coin names as keys.
    """
    base = sqlite3.connect('tgb_base.db', isolation_level=None)
    cursor = base.cursor()
    cursor.execute("SELECT DISTINCT coin_name FROM orders")
    distinct_coin_names = cursor.fetchall()
    base.close()
    current_names_coins = dict()
    for element in distinct_coin_names:
        current_names_coins[element[0]] = None
    return current_names_coins
