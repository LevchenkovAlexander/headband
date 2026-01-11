import logging
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI

import database

BOT_TOKEN = os.getenv("BOT_TOKEN")


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


