from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup

# from create_bot import dp
from data_base import sqlite_db


async def view_user_orders(message: types.Message):
    try:
        user_id = message.from_user.id
        page_number = await sqlite_db.get_page_number(user_id=user_id)
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=page_number)
        count_orders = await sqlite_db.count_tracking_user(user_id=user_id)
        if count_orders <= page_number + 6:
            new_page_number = 0
        else:
            new_page_number = page_number + 5
        await sqlite_db.update_current_page_number(new_page_number=new_page_number, user_id=user_id)
        print(f"page_number = {page_number}, count_orders = {count_orders}")
        if user_orders:
            for index, element in enumerate(user_orders):
                await message.answer(text=f"{index}, {element}")
        else:
            await message.reply(text="У вас еще нет отслеживаний монет")
    except Exception as e:
        print(f"Ошибка view_user_orders: {e}")


async def next_page_view_orders(message: types.Message):
    pass


def register_handler_crud(dp: Dispatcher):
    dp.register_message_handler(view_user_orders, commands=['view'])
