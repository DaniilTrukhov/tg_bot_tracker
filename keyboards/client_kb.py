from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data_base import sqlite_db
from handlers import crud

# Create button
tracking_button = KeyboardButton("/tracking")
view_button = KeyboardButton("/view")
cancel_button = KeyboardButton("/cancel")
yes_button = KeyboardButton("yes")
no_button = KeyboardButton("no")
next_button = KeyboardButton("/next")
update_button = KeyboardButton("/update")
delete_button = KeyboardButton("/delete")
price_btc = KeyboardButton("/price_btc")
return_to_main = KeyboardButton("/main_menu")

# Create keyboard
tracking_view_price_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True).add(tracking_button).insert(view_button).insert(price_btc)
tracking_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(tracking_button)
confirm_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(yes_button).insert(no_button)
next_keyboard = (ReplyKeyboardMarkup(resize_keyboard=True)
                 .add(update_button)
                 .insert(delete_button)
                 .add(return_to_main)
                 .insert(next_button)
                 )


async def create_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    Asynchronously creates a custom keyboard for user interaction in a Telegram bot.

    Args:
        user_id (int): The ID of the user for whom the keyboard is created.
    Returns:
        ReplyKeyboardMarkup: The custom keyboard with buttons representing order numbers.
    """
    page_number = await sqlite_db.get_page_number(user_id=user_id)
    count_orders = await sqlite_db.count_tracking_user(user_id=user_id)
    stop_range = crud.count_orders_in_page if (count_orders - page_number >=
                                               crud.count_orders_in_page) else (count_orders - page_number)
    choice_order_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(1, stop_range + 1):
        button_with_number = KeyboardButton(f"{index + page_number}")
        choice_order_keyboard.insert(button_with_number)
    return choice_order_keyboard
