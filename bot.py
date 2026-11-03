import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import get_settings
from database.database import init_db, make_session_factory
from handlers import games, management, start, statistics, wishlists


async def main():
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    engine, session_factory = make_session_factory(settings.database_url)
    await init_db(engine)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start.router, wishlists.router, games.router, statistics.router, management.router)
    dp["session_factory"] = session_factory
    await bot.set_my_commands([BotCommand(command="start", description="Главное меню"), BotCommand(command="cancel", description="Отмена")])
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

