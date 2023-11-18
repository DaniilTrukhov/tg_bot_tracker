from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_base import sqlite_db
from functions.tracking import track_the_cost

# Number of orders to display on each page
count_orders_in_page = 4


# Define the FSM states for creating, updating, and deleting orders
class FSMCreate(StatesGroup):
    coin = State()
    price = State()


class FSMUpdate(StatesGroup):
    index_in_page = State()
    new_price = State()


class FSMDelete(StatesGroup):
    index_in_page = State()
    confirm_delete = State()


async def cm_start(message: types.Message):
    """
        Command handler for the '/tracking' command.
        Initiates the process of tracking a cryptocurrency price.
    """
    await FSMCreate.coin.set()
    await message.answer("Введите абривиатуру одной монеты(пример:btc)")


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
    """ Handler for viewing user orders """
    try:
        user_id = message.from_user.id
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=0, count=count_orders_in_page)
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
        if count_orders <= page_number + (count_orders_in_page * 2) and new_page_number != 0:
            message_string = "Конец списка отслеживаний"
        await sqlite_db.update_current_page_number(new_page_number=new_page_number, user_id=user_id)
        user_orders = sqlite_db.read_user_tracking(user_id=user_id, page_number=new_page_number, count=count_orders_in_page)
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


async def choice_order(message: types.Message, state):
    """ Common logic for setting the state and prompting the user to enter the order number """
    try:
        await state.set()
        await message.answer(text="Введите номер отслеживания")
    except Exception as e:
        print(f"Ошибка choice_update_order: {e}")


async def get_id(message: types.Message, state: FSMContext, first_part, second_part):
    """ Common logic for getting the order ID and displaying relevant information """
    try:
        async with state.proxy() as data:
            page_number = await sqlite_db.get_page_number(user_id=message.from_user.id)
            page_number += int(message.text)
            user_order = sqlite_db.read_user_tracking(user_id=message.from_user.id, page_number=page_number, count=1)
            data["order_id"] = user_order[0][0]
            await message.answer(text='\n'.join([first_part, f"{user_order}", second_part]))
    except Exception as e:
        print(f"Ошибка get_id: {e}")


# Handler for initiating the update of a tracked order
async def choice_update_order(message: types.Message):
    await choice_order(message=message, state=FSMUpdate.index_in_page)


# Handler for updating the price of a tracked order
async def update_price_order(message: types.Message, state: FSMContext):
    await get_id(message=message, state=state, first_part="Вы обновляете ордер", second_part="Введите новую цену")
    await FSMUpdate.next()


# Handler for finishing the update of a tracked order
async def finish_update(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            new_price = float(message.text.replace(',', '.'))
            await sqlite_db.update_price_order_in_db(order_id=data["order_id"], new_price=new_price)
            await state.finish()
            await message.answer(text="Ордер обновлен")
    except Exception as e:
        print(f"Ошибка finish_update: {e}")


# Handler for initiating the deletion of a tracked order
async def choice_delete_order(message: types.Message):
    await choice_order(message=message, state=FSMDelete.index_in_page)


# Handler for confirming the deletion of a tracked order
async def confirm_delete_order(message: types.Message, state: FSMContext):
    await get_id(message=message, state=state, first_part="Вы хотите удалить отслеживание", second_part="Вы действительно хотите удалить это отслеживание?")
    await FSMDelete.next()


# Handler for finishing the deletion of a tracked order
async def finish_delete(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text.lower() == "yes":
                await sqlite_db.delete_order_in_db(order_id=data["order_id"])
                await message.reply(text="Ордер удален")
            else:
                await message.reply(text="Вы не стали удалять ордер, он все еще в работе")
            await state.finish()
    except Exception as e:
        print(f"Ошибка finish_delete: {e}")


def register_handler_crud(dp: Dispatcher):
    """
        # Register all the handlers with the dispatcher
    """
    dp.register_message_handler(cancel_fsm, state="*", commands="cancel")
    dp.register_message_handler(cancel_fsm, Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(view_user_orders, commands=['view'])
    dp.register_message_handler(next_page_view_orders, commands=['next'])
    dp.register_message_handler(cm_start, commands=["tracking"], state=None)
    dp.register_message_handler(check_price, state=FSMCreate.coin)
    dp.register_message_handler(write_answer, state=FSMCreate.price)
    dp.register_message_handler(choice_update_order, commands=["update"], state=None)
    dp.register_message_handler(update_price_order, state=FSMUpdate.index_in_page)
    dp.register_message_handler(finish_update, state=FSMUpdate.new_price)
    dp.register_message_handler(choice_delete_order, commands=["delete"], state=None)
    dp.register_message_handler(confirm_delete_order, state=FSMDelete.index_in_page)
    dp.register_message_handler(finish_delete, state=FSMDelete.confirm_delete)
