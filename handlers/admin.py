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
        data["price_coin"] = await track_the_cost(message.text)
        print(type(data["price_coin"]))
        data["coin_name"] = message.text
    await FSMAdmin.next()
    await message.reply("Теперь введите нужную цену")


async def write_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["target_price"] = float(message.text)
        print(type(data["target_price"]))
    async with state.proxy() as data:
        print(message.from_user.id, type(message.from_user.id))
        await sqlite_db.create_user(user_id=message.from_user.id)
        await sqlite_db.create_tracking(message.from_user.id, state)
    await state.finish()


async def cancel_fsm(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Oперация отменена")


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cancel_fsm, state="*", commands="cancel")
    dp.register_message_handler(cancel_fsm, custom_filters=Text(equals='cancel', ignore_case=True), state="*")
    dp.register_message_handler(cm_start, commands=["tracking"], state=None)
    dp.register_message_handler(check_price, state=FSMAdmin.coin)
    dp.register_message_handler(write_answer, state=FSMAdmin.price)

