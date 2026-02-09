import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv

from headband.backend import database as db
from headband.backend.api import app
from headband.backend.database import AsyncSessionLocal
from headband.backend.telegram_bot import bot_main

load_dotenv()

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
@asynccontextmanager
async def get_db_session():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def start_db():
    if await db.setup_database():
        logging.info("БД запущена")
        return True
    return False

def run_bot_process():
    """Запуск бота в отдельном процессе"""
    asyncio.run(bot_main.start_bot())

def run_server_process():
    """Запуск сервера в отдельном процессе"""
    async def start_server():
        if await db.setup_database():
            logging.info("База данных инициализирована")
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    asyncio.run(start_server())