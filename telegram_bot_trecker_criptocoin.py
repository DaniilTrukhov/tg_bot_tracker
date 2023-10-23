import asyncio, schedule

from aiogram import executor
from data_base import sqlite_db
from create_bot import dp
from handlers import admin, other
from functions import tracking

admin.register_handlers_admin(dp=dp)
other.register_handlers_other(dp=dp)


async def on_startup(_):
    sqlite_db.start_bd()
    print("db is connect")


async def scheduler():
    schedule.every(15).seconds.do(lambda: asyncio.run_coroutine_threadsafe(tracking.tracking_coin(), loop))
    schedule.every(30).seconds.do(lambda: asyncio.run_coroutine_threadsafe(tracking.install_names_dict(), loop))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tracking.install_names_dict())

    # Create tasks for thr and scheduler
    tasks = [
        asyncio.ensure_future(scheduler()),
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup),
    ]

    # Start the loop to run the tasks
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
