from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_base import sqlite_db
from functions.tracking import check_the_cost
from keyboards import client_kb


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


async def start_create(message: types.Message):
    """
        Command handler for the '/tracking' command.
        Initiates the process of tracking a cryptocurrency price.
    """
    await FSMCreate.coin.set()
    await message.answer("Введите абривиатуру одной монеты(пример:btc), или нажмите\n/cancel для отмены",
                         reply_markup=types.ReplyKeyboardRemove())


async def check_price(message: types.Message, state: FSMContext):
    """
        Handler for checking the price of a cryptocurrency and prompting the user to enter the desired price.
    """
    async with state.proxy() as data:
        result = await check_the_cost(message.text)
        if result:
            data["price_coin"] = result
            coin_name = message.text.upper()
            data["coin_name"] = coin_name
            await FSMCreate.next()
            await message.reply(f"Цена монеты {coin_name} = {result} Теперь введите нужную цену, "
                                f"до которой хочешь отслеживать цену или нажмите\n/cancel для отмены")
        else:
            await state.finish()
            await message.reply(text="Данная монета не найдена\nНужно вводит абривиатуру в формате "
                                     "BTC, ETH, SOL(регистр не важен). Можно ввести 1 наименование за раз")
            await FSMCreate.coin.set()
            await message.answer("Введите абривиатуру одной монеты(пример:btc), или нажмите\n/cancel для отмены")


async def finish_create(message: types.Message, state: FSMContext):
    """
        Handler for processing the user's input and registering the tracking of a cryptocurrency.
    """
    try:
        async with state.proxy() as data:
            data["target_price"] = float(message.text.replace(',', '.').replace(' ', ''))
        async with state.proxy() as data:
            await sqlite_db.create_user(user_id=message.from_user.id)
            await sqlite_db.create_tracking(message.from_user.id, data)
        await state.finish()
        await message.reply(text="Oтслеживание успешно зарегистрированно",
                            reply_markup=client_kb.tracking_view_price_keyboard)
    except ValueError:
        await state.finish()
        await message.reply(text="Введены не только коректные данные. Можно ввести только цифры (1234567890)"
                                 " и один разделитель целых чисел от дробных (. или ,)")
        await FSMCreate.coin.set()
        await message.answer("введите абривиатуру одной монеты(пример:btc), или нажмите\n/cancel для отмены")
    except Exception as e:
        print(f"Ошибка finish_create: {e}")


async def cancel_fsm(message: types.Message, state: FSMContext):
    """
        Handler for canceling the FSM operation.
    """
    current_state = await state.get_state()
    answer_string = "Вы в главном меню."
    if current_state is not None:
        await state.finish()
        answer_string = "\n".join(["Oперация отменена", answer_string])
    await message.reply(text=answer_string, reply_markup=client_kb.tracking_view_price_keyboard)


async def choice_order(message: types.Message, state):
    """ Common logic for setting the state and prompting the user to enter the order number """
    try:
        await state.set()
        choice_order_keyboard = await client_kb.create_keyboard(user_id=message.from_user.id)
        await message.answer(text="Введите номер отслеживания,\nили нажмите\n/cancel для отмены",
                             reply_markup=choice_order_keyboard)
    except Exception as e:
        print(f"Ошибка choice_update_order: {e}")


async def get_id(message: types.Message, state: FSMContext, first_part: str,
                 second_part: str, delete_flag: bool = False):
    """ Common logic for getting the order ID and displaying relevant information """
    try:
        async with state.proxy() as data:
            page_number = int(message.text) - 1
            user_order = sqlite_db.read_user_tracking(user_id=message.from_user.id, page_number=page_number, count=1)
            data["order_id"] = user_order[0][0]
            answer_string = f"Монета {user_order[0][1]} цена {user_order[0][2]}"
            if delete_flag:
                await message.answer(text='\n'.join([first_part, answer_string, second_part]),
                                     reply_markup=client_kb.confirm_keyboard)
            else:
                data["coin_name"] = user_order[0][1]
                await message.answer(text='\n'.join([first_part, answer_string, second_part]),
                                     reply_markup=types.ReplyKeyboardRemove())
            return True
    except ValueError as e:
        print(f"ValueError in get_id {e}")
        return False
    except Exception as e:
        print(f"Ошибка get_id: {e}")


async def choice_update_order(message: types.Message):
    await choice_order(message=message, state=FSMUpdate.index_in_page)


# Handler for initiating the update of a tracked order
async def update_price_order(message: types.Message, state: FSMContext):
    if await get_id(
            message=message,
            state=state,
            first_part="Вы обновляете ордер",
            second_part="Введите новую цену, или нажмите\n/cancel для отмены"
    ):
        await FSMUpdate.next()


# Handler for updating the price of a tracked order
async def finish_update(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            new_price = float(message.text.replace(',', '.').replace(' ', ''))
            current_price = await check_the_cost(data["coin_name"])
            await sqlite_db.update_price_order_in_db(order_id=data["order_id"],
                                                     current_price=current_price,
                                                     new_price=new_price)
            await state.finish()
            await message.answer(text="Ордер обновлен", reply_markup=client_kb.tracking_view_price_keyboard)
    except ValueError:
        await message.reply(text="Введены не только коректные данные. Можно ввести только цифры (1234567890)"
                                 " и один разделитель целых чисел от дробных (. или ,)")
    except Exception as e:
        print(f"Ошибка finish_update: {e}")


# Handler for finishing the update of a tracked order
async def choice_delete_order(message: types.Message):
    await choice_order(message=message, state=FSMDelete.index_in_page)


# Handler for initiating the deletion of a tracked order
async def confirm_delete_order(message: types.Message, state: FSMContext):
    if await get_id(
            message=message,
            state=state,
            first_part="Вы хотите удалить отслеживание",
            second_part="Вы действительно хотите удалить это отслеживание?",
            delete_flag=True
    ):
        await FSMDelete.next()


# Handler for confirming the deletion of a tracked order
async def finish_delete(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text.lower() == "yes":
                await sqlite_db.delete_order_in_db(order_id=data["order_id"])
                await message.reply(text="Ордер удален", reply_markup=client_kb.tracking_view_price_keyboard)
            else:
                await message.reply(text="Вы не стали удалять ордер, он все еще в работе",
                                    reply_markup=client_kb.tracking_view_price_keyboard)
            await state.finish()
    except Exception as e:
        print(f"Ошибка finish_delete: {e}")


# Handler for finishing the deletion of a tracked order
def register_handler_general(dp: Dispatcher):
    """
        # Register all the handlers with the dispatcher
    """
    dp.register_message_handler(cancel_fsm, state="*", commands="cancel")
    dp.register_message_handler(cancel_fsm, Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(start_create, commands=["track"], state=None)
    dp.register_message_handler(check_price, state=FSMCreate.coin)
    dp.register_message_handler(finish_create, state=FSMCreate.price)
    dp.register_message_handler(choice_update_order, commands=["update"], state=None)
    dp.register_message_handler(update_price_order, state=FSMUpdate.index_in_page)
    dp.register_message_handler(finish_update, state=FSMUpdate.new_price)
    dp.register_message_handler(choice_delete_order, commands=["delete"], state=None)
    dp.register_message_handler(confirm_delete_order, state=FSMDelete.index_in_page)
    dp.register_message_handler(finish_delete, state=FSMDelete.confirm_delete)
