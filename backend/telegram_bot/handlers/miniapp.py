from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.bot_db_fcn import check_account_type
from backend.telegram_bot.keyboards import get_master_main_keyboard
from backend.telegram_bot.bot_config import Config


async def callback_open_miniapp(callback: CallbackQuery, session: AsyncSession):
    """Открытие Mini App"""
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        await callback.answer("❌ Мастер не найден", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        "📱 Запускаю Mini App...",
        reply_markup=get_master_main_keyboard(str(master_id))
    )


async def handle_web_app_data(message: types.Message, session: AsyncSession):
    """Обработка данных от Mini App"""
    data = message.web_app_data.data
    chat_id = message.chat.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        return

    await message.answer(
        "✅ Данные получены от Mini App\n\n"
        f"Данные: {data}"
    )


def register_handlers(dp):
    """Регистрация хендлеров этого модуля"""
    dp.register_callback_query_handler(callback_open_miniapp, text="open_miniapp")
    dp.register_message_handler(
        handle_web_app_data,
        content_types=["web_app_data"]
    )