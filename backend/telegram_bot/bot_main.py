import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.executor import start_polling
from sqlalchemy.ext.asyncio import AsyncSession

from backend.telegram_bot import dp
from backend.telegram_bot.bot_config import Config
from backend.database import setup_database, close_connection, AsyncSessionLocal
from backend.telegram_bot.handlers import start, subscription, notifications, miniapp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для сессии базы данных"""

    def __init__(self):
        super(DatabaseMiddleware, self).__init__()

    async def on_pre_process_message(self, message, data: dict):
        """Перед обработкой сообщения"""
        session = AsyncSessionLocal()
        data['session'] = session
        data['session_should_close'] = True

    async def on_pre_process_callback_query(self, callback_query, data: dict):
        """Перед обработкой callback"""
        session = AsyncSessionLocal()
        data['session'] = session
        data['session_should_close'] = True

    async def on_pre_process_pre_checkout_query(self, pre_checkout_query, data: dict):
        """Перед обработкой pre_checkout"""
        session = AsyncSessionLocal()
        data['session'] = session
        data['session_should_close'] = True

    async def on_post_process_message(self, message, response, data: dict):
        """После обработки сообщения"""
        session = data.get('session')
        if session and data.get('session_should_close'):
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка БД: {e}")
            finally:
                await session.close()

    async def on_post_process_callback_query(self, callback_query, response, data: dict):
        """После обработки callback"""
        session = data.get('session')
        if session and data.get('session_should_close'):
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка БД: {e}")
            finally:
                await session.close()

    async def on_post_process_pre_checkout_query(self, pre_checkout_query, response, data: dict):
        """После обработки pre_checkout"""
        session = data.get('session')
        if session and data.get('session_should_close'):
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка БД: {e}")
            finally:
                await session.close()


async def on_startup(dp):
    """При запуске бота"""
    await setup_database()
    logger.info("База данных инициализирована")
    logger.info("Бот запущен!")


async def on_shutdown(dp):
    """При остановке бота"""
    await close_connection()
    logger.info("Бот остановлен")


def register_all_handlers(dp: Dispatcher):
    """Регистрация всех хендлеров"""
    start.register_handlers(dp)
    subscription.register_handlers(dp)
    notifications.register_handlers(dp)
    miniapp.register_handlers(dp)


async def run_bot():
    """Запуск бота"""
    bot = Bot(token=Config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    # ✅ Регистрация middleware
    dp.middleware.setup(DatabaseMiddleware())

    # Регистрация хендлеров
    register_all_handlers(dp)

    await start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )


def run_bot_process():
    """Функция для запуска в отдельном процессе"""
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")