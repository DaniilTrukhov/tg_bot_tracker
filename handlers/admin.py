from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import dp
from functions.tracking import track_the_cost
from data_base import sqlite_db


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


class FSMAdmin(StatesGroup):
    coin = State()
    price = State()


async def cm_start(message: types.Message):
    await FSMAdmin.coin.set()
    await message.answer("введите абривиатуру одной монеты(пример:btc)")


async def check_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        result = await track_the_cost(message.text)
        if result:
            data["price_coin"] = result
            print(result)
            coin_name = message.text.upper()
            data["coin_name"] = coin_name
            await FSMAdmin.next()
            await message.reply(f"Цена монеты {coin_name} = {result} Теперь введите нужную цену, до которой хочешь отслеживать")
        else:
            await state.finish()
            await message.reply(text="Неверный ввод абривиатуры монеты попробуйте снова, или введи cancel для отмены")
            await FSMAdmin.coin.set()
            await message.answer("введите абривиатуру одной монеты(пример:btc)")


async def write_answer(message: types.Message, state: FSMContext):
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
        await message.reply(text="Введены не только нкоректные данные. Можно ввести только цифры (1234567890) и один разделитель целых чисел от дробных (. или ,) или введи cancel для отмены")
        await FSMAdmin.coin.set()
        await message.answer("введите абривиатуру одной монеты(пример:btc)")



async def cancel_fsm(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Oперация отменена")



def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cancel_fsm, state="*", commands="cancel")
    dp.register_message_handler(cancel_fsm, Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(cm_start, commands=["tracking"], state=None)
    dp.register_message_handler(check_price, state=FSMAdmin.coin)
    dp.register_message_handler(write_answer, state=FSMAdmin.price)
