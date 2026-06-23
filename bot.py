import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import admin, user
from utils.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(user.router)

    # Avtomatik joylash scheduleri
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler ishga tushdi.")

    logger.info("Bot ishga tushdi ✅")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
