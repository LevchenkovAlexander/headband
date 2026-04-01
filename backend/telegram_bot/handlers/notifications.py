from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import MasterNotificationModel, MasterModel
from backend.database.bot_db_fcn import check_account_type
from backend.telegram_bot.keyboards import get_notification_settings_keyboard, get_master_main_keyboard


async def callback_notification_settings(callback: CallbackQuery, session: AsyncSession):
    """Настройки уведомлений"""
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        await callback.answer("❌ Мастер не найден", show_alert=True)
        return

    notification = await MasterNotificationModel.get_by_master_id(
        session=session,
        master_id=master_id
    )

    if not notification:
        await MasterNotificationModel.create(
            session=session,
            master_id=master_id
        )
        notification = await MasterNotificationModel.get_by_master_id(
            session=session,
            master_id=master_id
        )

    settings = {
        'appointment_notification': notification.appointment_notification,
        'appointment_cancel_notification': notification.appointment_cancel_notification,
        'appointment_confirm_notification': notification.appointment_confirm_notification
    }

    await callback.message.edit_text(
        "🔔 Настройки уведомлений\n\nВключите или выключите нужные уведомления:",
        reply_markup=get_notification_settings_keyboard(settings)
    )
    await callback.answer()


async def callback_notification_toggle(callback: CallbackQuery, session: AsyncSession):
    """Переключение уведомлений"""
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        await callback.answer("❌ Мастер не найден", show_alert=True)
        return

    notification_type = callback.data.split("_")[-1]

    notification = await MasterNotificationModel.get_by_master_id(
        session=session,
        master_id=master_id
    )

    if not notification:
        await callback.answer("❌ Настройки не найдены", show_alert=True)
        return

    field_map = {
        'appointment': 'appointment_notification',
        'cancel': 'appointment_cancel_notification',
        'confirm': 'appointment_confirm_notification'
    }

    field = field_map.get(notification_type)
    if not field:
        await callback.answer("❌ Неверный тип уведомления", show_alert=True)
        return

    current_value = getattr(notification, field)
    update_data = {field: not current_value}

    await MasterNotificationModel.update(
        session=session,
        master_id=master_id,
        update_data=update_data
    )

    await callback_notification_settings(callback, session)
    await callback.answer(f"✅ Уведомление {'включено' if not current_value else 'выключено'}")


def register_handlers(dp):
    """Регистрация хендлеров этого модуля"""
    dp.register_callback_query_handler(
        callback_notification_settings,
        text="notification_settings"
    )
    dp.register_callback_query_handler(
        callback_notification_toggle,
        lambda c: c.data.startswith("notif_toggle_")
    )