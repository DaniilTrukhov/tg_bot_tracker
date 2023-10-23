from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import AllSettings


# Memory storage for FSM (Finite State Machine) persistence
storage = MemoryStorage()

# Create a Bot instance using the API token from the AllSettings class
bot = Bot(token=AllSettings.api_token)

# Create a Dispatcher instance with the specified bot and storage
dp = Dispatcher(bot=bot, storage=storage)
