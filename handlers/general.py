from aiogram import types, Dispatcher

from create_bot import dp
from keyboards import client_kb
from functions import tracking


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Handler for the '/start' and '/help' commands.
    This handler will be called when the user sends '/start' or '/help' command.
    """
    await message.reply(text="Hi!\nI am a bot tracking cryptomonets by request!"
                        "\nPowered by aiogram.",
                        reply_markup=client_kb.tracking_view_price_keyboard)


@dp.message_handler(commands=["price_btc"])
async def check_price_btc(message: types.Message):
    result = await tracking.track_the_cost("BTC")
    await message.reply(text=f"{result}", reply_markup=client_kb.tracking_view_price_keyboard)


def register_handlers_general(dp: Dispatcher):
    pass
