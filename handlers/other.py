from aiogram import types, Dispatcher


async def echo(message: types.Message):
    """
        A simple echo handler that responds with the received message text.

        Args:
            message (types.Message): The incoming message object.
        """
    await message.answer(f"{message.text}")


def register_handlers_other(dp: Dispatcher):
    """
        Register other handlers with the provided Dispatcher.

        This function registers the `echo` handler for processing incoming messages.

        Args:
            dp (Dispatcher): The Dispatcher instance to register handlers with.
        """
    dp.register_message_handler(echo)
