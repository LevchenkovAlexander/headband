import logging
import uuid
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import MasterModel, UserModel
from backend.database.bot_db_fcn import (
    create_master_from_deeplink,
    check_account_type,
    get_master_referral_links
)
from backend.telegram_bot import dp
from backend.telegram_bot.keyboards import get_master_main_keyboard, get_become_master_keyboard
from backend.telegram_bot.bot_config import Config


async def cmd_start(message: types.Message, session: AsyncSession):
    """Обработчик команды /start"""
    chat_id = message.chat.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    args = message.text.split()
    referrer_master_id = None

    if len(args) > 1:
        ref_code = args[1]
        try:
            referrer_master_id = uuid.UUID(ref_code)
        except ValueError:
            referrer_master_id = None

    master_id, user_id = await check_account_type(chat_id, session)

    if master_id:
        await message.answer(
            "👋 Добро пожаловать обратно!\n\nВы уже зарегистрированы как мастер.",
            reply_markup=get_master_main_keyboard(str(master_id))
        )
        return

    result, master_id = await create_master_from_deeplink(
        chat_id=chat_id,
        username=username,
        full_name=full_name,
        referrer_master_id=referrer_master_id,
        session=session
    )

    if result == "success":
        bot_info = await message.bot.get_me()
        master_link, user_link = await get_master_referral_links(
            master_id=master_id,
            session=session,
            bot_username=bot_info.username
        )

        await message.answer(
            f"🎉 Добро пожаловать, {full_name}!\n\n"
            "Вы успешно зарегистрированы как мастер.\n\n"
            f"🔗 Ваши реферальные ссылки:\n"
            f"• Для мастеров: {master_link}\n"
            f"• Для клиентов: {user_link}\n\n"
            "Используйте меню ниже для управления аккаунтом.",
            reply_markup=get_master_main_keyboard(str(master_id))
        )
    else:
        await message.answer("❌ Произошла ошибка при регистрации. Попробуйте позже.")
        logging.error(f"Ошибка регистрации мастера: {result}")


async def callback_main_menu(callback: CallbackQuery, session: AsyncSession):
    """Возврат в главное меню"""
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if master_id:
        await callback.message.edit_text(
            "🏠 Главное меню",
            reply_markup=get_master_main_keyboard(str(master_id))
        )
    await callback.answer()


def register_handlers(dp):
    """Регистрация хендлеров этого модуля"""
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_callback_query_handler(callback_main_menu, text="main_menu")