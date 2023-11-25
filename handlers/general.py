from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards import client_kb
from functions import tracking
from data_base import sqlite_db


# Number of orders to display on each page
count_orders_in_page = 4


async def send_welcome(message: types.Message):
    """
    Handler for the '/start' and '/help' commands.
    This handler will be called when the user sends '/start' or '/help' command.
    """
    await message.reply(text="Hi!\nI am a bot tracking cryptomonets by request!"
                        "\nPowered by aiogram.",
                        reply_markup=client_kb.tracking_view_price_keyboard)


async def check_price_btc(message: types.Message):
    result = await tracking.check_the_cost("BTC")
    await message.reply(text=f"{result}", reply_markup=client_kb.tracking_view_price_keyboard)


async def return_to_main(message: types.Message, state: FSMContext):
    """
        Handler for canceling the FSM operation.
    """
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply(text="Вы в главном меню.", reply_markup=client_kb.tracking_view_price_keyboard)


async def view_user_orders(message: types.Message):
    """ Handler for viewing user orders """
    try:
        user_id = message.from_user.id
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=0, count=count_orders_in_page)
        await sqlite_db.update_current_page_number(new_page_number=0, user_id=user_id)
        if user_orders:
            answer_string = ""
            for index, element in enumerate(user_orders, start=1):
                answer_string = "\n\n".join([answer_string, f"{index}. Для {element[1]} ожидается {element[2]}"])
            await message.answer(text=answer_string, reply_markup=client_kb.next_keyboard)
        else:
            await message.reply(text="У вас еще нет отслеживаний монет", reply_markup=client_kb.tracking_keyboard)
    except Exception as e:
        print(f"Ошибка view_user_orders: {e}")


async def next_page_view_orders(message: types.Message):
    """ Handler for navigating to the next page of user orders """
    try:
        message_string = ""
        user_id = message.from_user.id
        page_number = await sqlite_db.get_page_number(user_id=user_id)
        count_orders = await sqlite_db.count_tracking_user(user_id=user_id)
        if count_orders <= page_number + count_orders_in_page:
            new_page_number = 0
        else:
            new_page_number = page_number + count_orders_in_page
        if ((count_orders <= page_number + (count_orders_in_page * 2) and new_page_number != 0)
                or count_orders <= count_orders_in_page):
            message_string = "Конец списка отслеживаний"
        await sqlite_db.update_current_page_number(new_page_number=new_page_number, user_id=user_id)
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=new_page_number,
                                                   count=count_orders_in_page)
        if user_orders:
            answer_string = ""
            for index, element in enumerate(user_orders, start=new_page_number + 1):
                answer_string = "\n\n".join([
                    answer_string, f"{index}. Для {element[1]} ожидается {element[2]}"
                ])
            if message_string:
                answer_string = "\n\n".join([answer_string, message_string])
            await message.answer(text=answer_string, reply_markup=client_kb.next_keyboard)
        else:
            await message.reply(text="У вас еще нет отслеживаний монет")
    except Exception as e:
        print(f"Ошибка view_user_orders: {e}")


# Handler for finishing the deletion of a tracked order
def register_handler_crud(dp: Dispatcher):
    """
        # Register all the handlers with the dispatcher
    """
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(check_price_btc, commands=["price_btc"])
    dp.register_message_handler(return_to_main, commands=["main_menu"])
    dp.register_message_handler(view_user_orders, commands=['view'])
    dp.register_message_handler(next_page_view_orders, commands=['next'])
