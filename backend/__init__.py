import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from headband.backend import database as db

from headband.backend.database import AsyncSessionLocal
from headband.backend.telegram_bot import bot_main

app = FastAPI(
    title="Headband API",
    description="API для сервиса записи в салоны красоты",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "User",
            "description": "Операции для клиентов (пользователей)"
        },
        {
            "name": "Master",
            "description": "Операции для мастеров"
        },
        {
            "name": "Admin",
            "description": "Административные операции"
        }
    ]
)



logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)


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