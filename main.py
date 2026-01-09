import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI

from config import BOT_TOKEN, WEB_APP_URL

logging.basicConfig(level=logging.INFO)

app = FastAPI()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def handle_start(message: Message):
    logging.info(f"recieved start command from user")
    await message.answer("here's gonna be a welcome message")


async def main():
    await dp.start_polling(bot)


if __name__ == "main":
    asyncio.run(main())

