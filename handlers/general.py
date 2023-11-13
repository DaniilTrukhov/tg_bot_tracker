from aiogram import types, Dispatcher

from create_bot import dp


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Handler for the '/start' and '/help' commands.
    This handler will be called when the user sends '/start' or '/help' command.
    """
    await message.reply("Hi!\nI am a bot tracking cryptomonets by request!\nTo start tracking, enter \n/tracking \nPowered by aiogram.")


def register_handlers_general(dp: Dispatcher):
    pass
