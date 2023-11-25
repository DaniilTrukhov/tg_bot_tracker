import asyncio
import schedule

from aiogram import executor
from data_base import sqlite_db
from create_bot import dp
from handlers import other, general
from functions import tracking
from states import crud_states

# Register general, crud and other handlers
crud_states.register_handler_general(dp=dp)
general.register_handler_general(dp=dp)
other.register_handlers_other(dp=dp)


async def on_startup(_):
    """
    Function to be executed on startup.

    Args:
        _ (Any): Placeholder parameter.
    """
    sqlite_db.start_bd()
    print("Database is connected")


async def scheduler():
    """
        Scheduler function for periodic tasks.

        This function schedules two tasks to run every 15 and 30 seconds, respectively.
        The tasks involve tracking coin prices and updating the names dictionary.

        Note:
            This function runs in an infinite loop and is intended to be executed as a separate task.
        """
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
