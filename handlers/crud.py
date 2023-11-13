from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_base import sqlite_db
from functions.tracking import track_the_cost


class FSMCreate(StatesGroup):
    coin = State()
    price = State()


class FSMUpdate1(StatesGroup):
    update_price = State()


class FSMUpdate2(StatesGroup):
    update_price = State()


class FSMDelete(StatesGroup):
    confirm_delete = State()


async def cm_start(message: types.Message):
    """
        Command handler for the '/tracking' command.
        Initiates the process of tracking a cryptocurrency price.
    """
    await FSMCreate.coin.set()
    await message.answer("введите абривиатуру одной монеты(пример:btc)")


async def check_price(message: types.Message, state: FSMContext):
    """
        Handler for checking the price of a cryptocurrency and prompting the user to enter the desired price.
    """
    async with state.proxy() as data:
        result = await track_the_cost(message.text)
        if result:
            data["price_coin"] = result
            coin_name = message.text.upper()
            data["coin_name"] = coin_name
            await FSMCreate.next()
            await message.reply(f"Цена монеты {coin_name} = {result} Теперь введите нужную цену, до которой хочешь отслеживать")
        else:
            await state.finish()
            await message.reply(text="Неверный ввод абривиатуры монеты попробуйте снова, или введи cancel для отмены")
            await FSMCreate.coin.set()
            await message.answer("введите абривиатуру одной монеты(пример:btc)")


async def write_answer(message: types.Message, state: FSMContext):
    """
        Handler for processing the user's input and registering the tracking of a cryptocurrency.
    """
    try:
        async with state.proxy() as data:
            data["target_price"] = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            await sqlite_db.create_user(user_id=message.from_user.id)
            await sqlite_db.create_tracking(message.from_user.id, data)
        await state.finish()
        await message.reply(text="Oтслеживание успешно зарегистрированно")
    except ValueError as e:
        await state.finish()
        await message.reply(text="Введены не только коректные данные. Можно ввести только цифры (1234567890) и один разделитель целых чисел от дробных (. или ,) или введи cancel для отмены")
        await FSMCreate.coin.set()
        await message.answer("введите абривиатуру одной монеты(пример:btc)")


async def cancel_fsm(message: types.Message, state: FSMContext):
    """
        Handler for canceling the FSM operation.
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Oперация отменена")


async def view_user_orders(message: types.Message):
    try:
        user_id = message.from_user.id
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=0, count=2)
        count_orders = await sqlite_db.count_tracking_user(user_id=user_id)
        await sqlite_db.update_current_page_number(new_page_number=0, user_id=user_id)
        print(f"page_number = 0, count_orders = {count_orders}")
        if user_orders:
            for index, element in enumerate(user_orders):
                await message.answer(text=f"{index}, {element}")
        else:
            await message.reply(text="У вас еще нет отслеживаний монет")
    except Exception as e:
        print(f"Ошибка view_user_orders: {e}")


async def next_page_view_orders(message: types.Message):
    try:
        message_string = ""
        user_id = message.from_user.id
        page_number = await sqlite_db.get_page_number(user_id=user_id)
        count_orders = await sqlite_db.count_tracking_user(user_id=user_id)
        if count_orders <= page_number + 2:
            new_page_number = 0
        else:
            new_page_number = page_number + 2
        if count_orders <= page_number + 4 and new_page_number != 0:
            message_string = "Конец списка отслеживаний"
        await sqlite_db.update_current_page_number(new_page_number=new_page_number, user_id=user_id)
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=new_page_number, count=2)
        print(f"page_number = {page_number}, count_orders = {count_orders}")
        if user_orders:
            for index, element in enumerate(user_orders):
                await message.answer(text=f"{index}, {element}")
            if message_string:
                await message.answer(text=message_string)
        else:
            await message.reply(text="У вас еще нет отслеживаний монет")
    except Exception as e:
        print(f"Ошибка view_user_orders: {e}")


async def update_users_order_1(message: types.Message):
    try:
        await FSMUpdate1.update_price.set()
        user_id = message.from_user.id
        page_number = await sqlite_db.get_page_number(user_id=user_id)
        user_order = sqlite_db.read_user_tracking(user_id=user_id, page_number=page_number, count=1)
        await message.answer(text=f"Обновить ордер, \nid={user_order[0][0]}\ncoin_name={user_order[0][1]}\ncoin_price={user_order[0][2]}?\nКакую цену установим?")
    except Exception as e:
        print(f"Ошибка update_users_orders_1: {e}")


async def update_price_order_1(message: types.Message, state: FSMContext):
    """

    """
    user_id = message.from_user.id
    page_number = await sqlite_db.get_page_number(user_id=user_id)
    user_order = sqlite_db.read_user_tracking(user_id=user_id, page_number=page_number, count=1)
    new_price = float(message.text.replace(',', '.'))
    await sqlite_db.update_price_order_in_db(order_id=user_order[0][0], new_price=new_price)
    await state.finish()
    await message.answer(text=f"Ордер успешно обновлен, \nМонета {user_order[0][1]}\nотслеживается до цены {new_price}")


async def update_users_order_2(message: types.Message):
    try:
        await FSMUpdate2.update_price.set()
        user_id = message.from_user.id
        page_number = await sqlite_db.get_page_number(user_id=user_id) + 1
        user_order = sqlite_db.read_user_tracking(user_id=user_id, page_number=page_number, count=1)
        await message.answer(text=f"Обновить ордер, \nid={user_order[0][0]}\ncoin_name={user_order[0][1]}\ncoin_price={user_order[0][2]}?\nКакую цену установим?")
    except Exception as e:
        print(f"Ошибка update_users_orders_2: {e}")


async def update_price_order_2(message: types.Message, state: FSMContext):
    """

    """
    user_id = message.from_user.id
    page_number = await sqlite_db.get_page_number(user_id=user_id) + 1
    user_order = sqlite_db.read_user_tracking(user_id=user_id, page_number=page_number, count=1)
    new_price = float(message.text.replace(',', '.'))
    await sqlite_db.update_price_order_in_db(order_id=user_order[0][0], new_price=new_price)
    await state.finish()
    await message.answer(text=f"Ордер успешно обновлен, \nМонета {user_order[0][1]}\nотслеживается до цены {new_price}")


def register_handler_crud(dp: Dispatcher):
    dp.register_message_handler(cancel_fsm, state="*", commands="cancel")
    dp.register_message_handler(cancel_fsm, Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(view_user_orders, commands=['view'])
    dp.register_message_handler(next_page_view_orders, commands=['next'])
    dp.register_message_handler(cm_start, commands=["tracking"], state=None)
    dp.register_message_handler(check_price, state=FSMCreate.coin)
    dp.register_message_handler(write_answer, state=FSMCreate.price)
    dp.register_message_handler(update_users_order_1, commands=["update1"], state=None)
    dp.register_message_handler(update_price_order_1, state=FSMUpdate1.update_price)
    dp.register_message_handler(update_users_order_2, commands=["update2"], state=None)
    dp.register_message_handler(update_price_order_2, state=FSMUpdate2.update_price)
