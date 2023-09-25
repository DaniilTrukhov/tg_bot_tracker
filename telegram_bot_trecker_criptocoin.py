import time, schedule, threading

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
    tracking.tracking_coin()



"""asfasdfasdfasdfasdfasdf"""
def mess():
   print("Вызов из потока каждую минуту")

def thr():
   while True:
      schedule.run_pending()
      time.sleep(5)

"""asdfasdfasdfasdfasdfasd"""

if __name__ == '__main__':
    schedule.every(30).seconds.do(mess)
    threading.Thread(target=thr).start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
