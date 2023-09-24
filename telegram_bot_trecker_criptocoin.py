from aiogram import executor

from data_base import sqlite_db
from create_bot import dp
from handlers import admin, other

admin.register_handlers_admin(dp=dp)
other.register_handlers_other(dp=dp)


async def on_startup(_):
    sqlite_db.start_bd()
    print("db is connect")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
