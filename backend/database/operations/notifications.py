import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import MasterNotificationModel, MasterModel, AppointmentModel, GuidesModel


async def create_master_notification(
        master_id: uuid.UUID,
        session: AsyncSession
):
    """Создание настроек уведомлений для мастера"""
    return await MasterNotificationModel.create(session=session, master_id=master_id)


async def get_master_notification(
        master_id: uuid.UUID,
        session: AsyncSession
):
    """Получение настроек уведомлений мастера"""
    notification = await MasterNotificationModel.get_by_master_id(
        session=session,
        master_id=master_id
    )

    if not notification:
        return "notification not found", None

    resp = {
        "id": notification.id,
        "master_id": notification.master_id,
        "appointment_notification": notification.appointment_notification,
        "appointment_cancel_notification": notification.appointment_cancel_notification,
        "appointment_confirm_notification": notification.appointment_confirm_notification,
        "guide_approved_notification": notification.guide_approved_notification,
        "subscription_ending_notification": notification.subscription_ending_notification
    }

    return "success", resp


async def update_master_notification(
        master_id: uuid.UUID,
        update_data: dict,
        session: AsyncSession
):
    """Обновление настроек уведомлений мастера"""
    return await MasterNotificationModel.update(
        session=session,
        master_id=master_id,
        update_data=update_data
    )


async def send_notification(
        master_id: uuid.UUID,
        notification_type: str,
        bot,
        appo_id: Optional[uuid.UUID],
        guide_id: Optional[uuid.UUID],
        session: AsyncSession
):
    """Отправка уведомления мастеру согласно настройкам"""
    try:
        notification = await MasterNotificationModel.get_by_master_id(
            session=session,
            master_id=master_id
        )

        if not notification:
            return

        master = await MasterModel.get_by_id(session=session, master_id=master_id)
        if not master or not master.chat_id_tg:
            return

        # Проверяем тип уведомления и настройки
        should_send = False
        message = ""

        if notification_type == "appointment":
            appo = await AppointmentModel.get_by_id(session=session, appointment_id=appo_id)
            should_send = notification.appointment_notification
            message = f"📅 Новая запись на {appo.date}, {appo.start_time}"
        elif notification_type == "appointment_cancel":
            appo = await AppointmentModel.get_by_id(session=session, appointment_id=appo_id)
            should_send = notification.appointment_cancel_notification
            message = f"❌ Запись отменена {appo.date}, {appo.start_time}"
        elif notification_type == "guide_approved":
            guide = await GuidesModel.get_by_id(session=session, guide_id=guide_id)
            should_send = notification.guide_approved_notification
            message = "📚 Гайд одобрен!"
        elif notification_type == "subscription_ending":
            should_send = notification.subscription_ending_notification
            message = "⚠️ Подписка скоро заканчивается!"

        if should_send:
            await bot.send_message(chat_id=master.chat_id_tg, text=message)

    except Exception as e:
        logging.error(f"Ошибка отправки уведомления: {e}")