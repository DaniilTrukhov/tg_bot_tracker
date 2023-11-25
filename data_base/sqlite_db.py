import sqlite3

from typing import List, Tuple


def execute_query(query, parameters=None) -> None:
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
        print(f"Ошибка выполнения запроса\nexecute_query\n: {e}")


def start_bd() -> None:
    """
        Initializes the SQLite database and creates necessary tables if they don't exist.
    """
    first_query = '''
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id INTEGER PRIMARY KEY,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            is_prime BOOLEAN DEFAULT False,
            current_page_number INT DEFAULT 0
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
    try:
        query = "INSERT OR IGNORE INTO users (telegram_user_id, is_prime) VALUES (?, ?)"
        execute_query(query=query, parameters=(user_id, False))
    except Exception as e:
        print(f"Ошибка при чтении данных\ncreate_user\n: {e}")


async def create_tracking(user_id: int, data: dict) -> None:
    """
        Asynchronously inserts a tracking order into the 'orders' table.

        Args:
            user_id (int): The Telegram user ID.
            data (dict): A dictionary containing tracking order information.
    """
    try:
        coin_name = data["coin_name"]
        target_price = data["target_price"]
        if data["price_coin"] > data["target_price"]:
            uptrend = False
        else:
            uptrend = True
        query = "INSERT INTO orders (coin_name, target_price, uptrend, user_id) VALUES (?, ?, ?, ?)"
        execute_query(query=query, parameters=(coin_name, target_price, uptrend, user_id))
    except Exception as e:
        print(f"Ошибка при чтении данных\ncreate_tracking\n: {e}")


def read_user_tracking(user_id: int, page_number: int, count: int = 1) -> List[Tuple]:
    """
    Reads and returns a specified number of tracking orders for a given user and page.

    Args:
        user_id (int): The ID of the user whose orders are to be retrieved.
        page_number (int): The page number of orders to be retrieved.
        count (int, optional): The number of orders to retrieve (default is 1).

    Returns:
        List[Tuple]: A list of tuples representing tracking orders for the user.
    """
    try:
        with sqlite3.connect('tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute(
                "SELECT * "
                "FROM orders "
                "WHERE archived = FALSE AND user_id = {user_id} "
                "LIMIT {count} OFFSET {page_number}".format(user_id=user_id, count=count, page_number=page_number)
            )
            orders = cursor.fetchall()
            return orders
    except Exception as e:
        print(f"Ошибка при чтении данных\nread_user_tracking\n: {e}")


def read_tracked() -> List:
    """
        Reads and returns the active tracking orders from the 'orders' table.

        Returns:
            list: A list of tuples representing active tracking orders.
    """
    try:
        with sqlite3.connect('tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("SELECT * FROM orders WHERE archived = FALSE")
            orders = cursor.fetchall()
            return orders
    except Exception as e:
        print(f"Ошибка при чтении данных\nread_tracked\n: {e}")


def archived_order(user_id: int) -> None:
    """
        Updates the tracking order status to 'archived' with the end date.

        Args:
            user_id (int): The ID of the tracking order to be updated.
    """
    try:
        query = "UPDATE orders SET archived = TRUE, end_date = CURRENT_TIMESTAMP WHERE id = ?;"
        execute_query(query=query, parameters=(user_id,))
    except Exception as e:
        print(f"Ошибка выполнения запроса\nupdate_order\n: {e}")


async def count_tracking_user(user_id: int) -> int:
    """
    Asynchronously counts the number of active tracking orders for a given user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        int: The count of active tracking orders for the user.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = {user_id} AND archived = 0".format(
              user_id=user_id,
            ))
            count_tracking = cursor.fetchall()
            return int(count_tracking[0][0])
    except Exception as e:
        print(f"Ошибка выполнения запроса\ncount_tracking_user\n: {e}")


async def read_distinct_coin_name() -> dict:
    """
        Asynchronously reads distinct coin names from the 'orders' table.

        Returns:
            dict: A dictionary with distinct coin names as keys.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("SELECT DISTINCT coin_name FROM orders")
            distinct_coin_names = cursor.fetchall()
            current_names_coins = dict()
            for element in distinct_coin_names:
                current_names_coins[element[0]] = None
            return current_names_coins
    except Exception as e:
        print(f"Ошибка выполнения запроса\nread_distinct_coin_name\n: {e}")


async def get_page_number(user_id: int) -> int:
    """
        Asynchronously retrieves the current page number for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            int: The current page number for the user.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("SELECT current_page_number FROM users WHERE telegram_user_id = {user_id}".format(
              user_id=user_id,
            ))
            current_page_number = cursor.fetchall()
            return int(current_page_number[0][0])
    except Exception as e:
        print(f"Ошибка выполнения запроса\nget_page_number\n: {e}")


async def update_current_page_number(new_page_number: int, user_id: int) -> None:
    """
    Asynchronously updates the current page number for a user in the database.

    Args:
        new_page_number (int): The new page number to be set.
        user_id (int): The ID of the user.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("UPDATE users "
                           "SET current_page_number = {new_number} "
                           "WHERE telegram_user_id = {user_id}".format(new_number=new_page_number, user_id=user_id)
                           )
    except Exception as e:
        print(f"Ошибка выполнения запроса \nupdate_current_page_number\n: {e}")


async def update_price_order_in_db(order_id: int, current_price: float, new_price: float) -> None:
    """
    Asynchronously updates the target price of a tracking order in the database.

    Args:
        order_id (int): The ID of the order to be updated.
        current_price (float): The current price for coin this order.
        new_price (float): The new target price for the order.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            if current_price > new_price:
                uptrend = False
            else:
                uptrend = True
            cursor.execute(
                "UPDATE orders "
                "SET target_price = {new_price}, uptrend = {uptrend} WHERE id = {order_id}".format(
                    new_price=new_price,
                    uptrend=uptrend,
                    order_id=order_id,
                )
            )
    except Exception as e:
        print(f"Ошибка выполнения запроса на обновление записи: {e}")


async def delete_order_in_db(order_id: int) -> None:
    """
    Asynchronously deletes a tracking order from the database.

    Args:
        order_id (int): The ID of the order to be deleted.
    """
    try:
        with sqlite3.connect(database='tgb_base.db', isolation_level=None) as base:
            cursor = base.cursor()
            cursor.execute("DELETE FROM orders WHERE id = {order_id}".format(order_id=order_id))
    except Exception as e:
        print(f"Ошибка выполнения запроса на удаление записи: {e}")
