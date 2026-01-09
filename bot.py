import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import BOT_TOKEN, WEB_APP_URL

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def start(message: types.Message):
    # Создаём объект WebAppInfo с URL из конфига
    web_app_info = types.WebAppInfo(url=WEB_APP_URL)
    
    # Создаём клавиатуру
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Открыть Mini-App", web_app=web_app_info))
    builder.adjust(1)  # 1 кнопка в строке (опционально, но делает layout чище)
    
    # Отправляем приветствие с клавиатурой
    await message.answer(
        text="Привет! Нажми кнопку ниже, чтобы открыть Mini-App.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Основная асинхронная функция
async def main():
    # Удаляем webhook и сбрасываем накопленные обновления
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())