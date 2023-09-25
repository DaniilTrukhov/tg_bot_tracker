from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
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


# @dp.message_handler(commands=['tracking'])
async def cm_start(message: types.Message):
    await FSMAdmin.coin.set()
    await message.answer("введите абривиатуру одной монеты(пример:btc)")


# @dp.message_handler(state=FSMAdmin.coin)
async def check_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price_coin"] = track_the_cost(message.text)
        print(type(data["price_coin"]))
        data["coin_name"] = message.text
    await FSMAdmin.next()
    await message.reply("Теперь введите нужную цену")


# @dp.message_handler(state=FSMAdmin.price)
async def write_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["target_price"] = float(message.text)
        print(type(data["target_price"]))
    async with state.proxy() as data:
        print(message.from_user.id, type(message.from_user.id))
        await sqlite_db.create_user(message=message)
        await sqlite_db.create_tracking(message.from_user.id, state)
        await sqlite_db.read_tracking(message.from_user.id)
        # await message.reply(str(data))
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=["tracking"], state=None)
    dp.register_message_handler(check_price, state=FSMAdmin.coin)
    dp.register_message_handler(write_answer, state=FSMAdmin.price)
