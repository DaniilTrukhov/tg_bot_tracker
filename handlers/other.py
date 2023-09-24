from aiogram import types, Dispatcher

from create_bot import dp


async def echo(message: types.Message):
    await message.answer(f"{message.text} sdf")


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo)
