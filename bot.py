import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import BOT_TOKEN, WEB_APP_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def start(message: types.Message):
    webAppInfo = types.WebAppInfo(url="your-webapp-url") // TODO СДЕЛАТЬ САЙТ, ЗДЕСЬ URL
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Отправить данные', web_app=webAppInfo))
    
    await message.answer(text='Привет!', reply_markup=builder.as_markup())

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())