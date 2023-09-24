from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import AllSettings


storage = MemoryStorage()

bot = Bot(token=AllSettings.api_token)
dp = Dispatcher(bot=bot, storage=storage)
