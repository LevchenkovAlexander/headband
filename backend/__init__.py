import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from backend.telegram_bot import bot_main

import database as db

app = FastAPI(
    title="Headband API",
    description="API для сервиса записи в салоны красоты",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Master.Profile",
            "description": "Операции модуля мастера на странице профиля"
        },
        {
            "name": "Master.Schedule",
            "description": "Операции модуля мастера на странице расписания"
        },
        {
            "name": "Master.Welcome",
            "description": "Операции модуля мастера на первой странице"
        },
        {
            "name": "Master.Guide",
            "description": "Операции модуля мастера на странице гайдов"
        }
    ]
)

UPLOAD_DIR = Path("/var/uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)


def run_bot_process():
    """Импортируем функцию запуска бота"""
    from backend.telegram_bot.bot_main import run_bot_process as bot_runner
    bot_runner()


def run_server_process():
    """Запуск сервера в отдельном процессе"""
    async def start_server():
        if await db.setup_database():
            logging.info("База данных инициализирована")
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    asyncio.run(start_server())