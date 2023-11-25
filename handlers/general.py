from aiogram import types
from aiogram.dispatcher import FSMContext

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
    result = await tracking.check_the_cost("BTC")
    await message.reply(text=f"{result}", reply_markup=client_kb.tracking_view_price_keyboard)


@dp.message_handler(commands=["main_menu"])
async def return_to_main(message: types.Message, state: FSMContext):
    """
        Handler for canceling the FSM operation.
    """
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply(text="Вы в главном меню.", reply_markup=client_kb.tracking_view_price_keyboard)
