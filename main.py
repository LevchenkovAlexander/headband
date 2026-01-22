import logging
import asyncio
import os
import database as db
from aiogram import Bot, Dispatcher
from aiogram.types import Message

'''from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI



BOT_TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

app = FastAPI()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def handle_start(message: Message):
    logging.info(f"recieved start command from user")
    await message.answer("here's gonna be a welcome message")

'''
logging.basicConfig(level=logging.INFO)


async def main():
    try:
        if await db.setup_database():
            logging.info("БД инициализирована")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        await db.close_connection()




if __name__ == "__main__":
    asyncio.run(main())



