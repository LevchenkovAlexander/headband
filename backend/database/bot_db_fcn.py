import logging
import uuid
from datetime import date, timedelta
from typing import Optional

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import MasterNotificationModel, MasterModel, MasterReferralModel, UserModel, SubscriptionModel
from backend.database.requests import MasterCreateRequest, UserCreateRequest


async def create_master_from_deeplink(
        chat_id: int,
        username: str,
        full_name: str,
        referrer_master_id: Optional[uuid.UUID],
        session: AsyncSession
):
    """Создание мастера по диплинку с отслеживанием реферала"""
    try:
        # Генерируем персональные реферальные ссылки для нового мастера
        new_master_link_id = uuid.uuid4()  # для приглашения мастеров
        new_user_link_id = uuid.uuid4()  # для приглашения клиентов

        master_data = MasterCreateRequest(
            chat_id_tg=chat_id,
            username_tg=username,
            full_name=full_name,
            master_link_id=new_master_link_id,
            user_link_id=new_user_link_id
        )
        master_dict = master_data.model_dump()

        if referrer_master_id:
            master_dict["referrer_id"] = referrer_master_id
            master_dict["referral_counted"] = False

        master_id = await MasterModel.create(session=session, data=master_dict)

        await MasterNotificationModel.create(session=session, master_id=master_id)

        await MasterReferralModel.create(session=session, master_id=master_id)

        return "success", master_id
    except Exception as e:
        logging.error(f"Ошибка создания мастера: {e}")
        return f"error: {str(e)}", uuid.UUID(int=0)


"""async def create_user_from_deeplink(
        chat_id: int,
        username: str,
        referrer_master_id: Optional[uuid.UUID],
        session: AsyncSession
):
    try:
        user_data = UserCreateRequest(
            chat_id=chat_id,
            username=username
        )
        user_id = await UserModel.create(session=session, data=user_data.model_dump())

        # Для пользователей реферал засчитывается сразу (если нужно)
        if referrer_master_id:
            referrer = await MasterModel.get_by_id(session=session, master_id=referrer_master_id)
            if referrer:
                await MasterReferralModel.increment_users(
                    session=session,
                    master_id=referrer_master_id
                )

        return "success", user_id
    except Exception as e:
        logging.error(f"Ошибка создания пользователя: {e}")
        return f"error: {str(e)}", uuid.UUID(int=0)"""


async def create_subscription(
        master_id: uuid.UUID,
        duration_days: int,
        payment_amount: int,
        session: AsyncSession
):
    """
    Создание/продление подписки для мастера.
    Возвращает: (status, subscription_id, is_referral_counted)
    """
    try:
        start_date = date.today()
        end_date = start_date + timedelta(days=duration_days)

        is_first = await SubscriptionModel.is_first_subscription(
            session=session,
            master_id=master_id
        )

        existing = await SubscriptionModel.get_by_master_id(
            session=session,
            master_id=master_id
        )

        referral_counted = False

        if existing:
            if existing.end_date > start_date:
                end_date = existing.end_date + timedelta(days=duration_days)

            update_data = {
                "end_date": end_date,
                "is_active": True,
                "payment_amount": payment_amount
            }
            await SubscriptionModel.update(
                session=session,
                subscription_id=existing.id,
                update_data=update_data
            )
            subscription_id = existing.id
        else:
            data = {
                "master_id": master_id,
                "start_date": start_date,
                "end_date": end_date,
                "is_active": True,
                "payment_amount": payment_amount,
                "is_first_subscription": is_first
            }
            subscription_id = await SubscriptionModel.create(session=session, data=data)

        if is_first:
            referrer_id = await MasterModel.get_referrer_id(
                session=session,
                master_id=master_id
            )

            if referrer_id:
                master = await MasterModel.get_by_id(session=session, master_id=master_id)
                if master and not master.referral_counted:
                    # Засчитываем реферал
                    await MasterReferralModel.increment_masters(
                        session=session,
                        master_id=referrer_id
                    )

                    # Отмечаем, что реферал засчитан
                    await MasterModel.mark_referral_counted(
                        session=session,
                        master_id=master_id
                    )
        return "success"
    except Exception as e:
        logging.error(f"Ошибка создания подписки: {e}")
        return f"error: {str(e)}", uuid.UUID(int=0), False


async def get_subscription_status(
        master_id: uuid.UUID,
        session: AsyncSession
):
    """Проверка статуса подписки"""
    subscription = await SubscriptionModel.get_by_master_id(
        session=session,
        master_id=master_id
    )

    if not subscription:
        return False, None

    if subscription.end_date < date.today():
        return False, subscription.end_date

    return True, subscription.end_date


async def get_referral_stats(
        master_id: uuid.UUID,
        session: AsyncSession
) -> Optional[dict]:
    """Получение статистики рефералов мастера"""
    return await MasterReferralModel.get_stats(
        session=session,
        master_id=master_id
    )


async def get_master_referral_links(
        master_id: uuid.UUID,
        session: AsyncSession,
        bot_username: str
):
    """Получение реферальных ссылок мастера"""
    master = await MasterModel.get_by_id(session=session, master_id=master_id)

    if not master:
        return None, None

    # Формируем ссылки для бота
    master_link = f"https://t.me/{bot_username}?start={master.master_link_id}"
    user_link = f"https://t.me/{bot_username}?start={master.user_link_id}"

    return master_link, user_link


async def check_account_type(
        chat_id: int,
        session: AsyncSession
):
    """Проверка наличия аккаунтов мастера и пользователя"""
    master = await MasterModel.get_by_chat_id(session=session, chat_id=chat_id)
    user = await UserModel.get_by_chat_id(session=session, chat_id=chat_id)

    master_id = master.id if master else None
    user_id = user.id if user else None

    return master_id, user_id

async def send_notification(
        master_id: uuid.UUID,
        notification_type: str,
        bot,
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
            should_send = notification.appointment_notification
            message = "📅 Новая запись!"
        elif notification_type == "appointment_cancel":
            should_send = notification.appointment_cancel_notification
            message = "❌ Запись отменена"
        elif notification_type == "appointment_confirm":
            should_send = notification.appointment_confirm_notification
            message = "✅ Запись подтверждена"
        elif notification_type == "guide_approved":
            should_send = notification.guide_approved_notification
            message = "📚 Гайд одобрен!"
        elif notification_type == "subscription_ending":
            should_send = notification.subscription_ending_notification
            message = "⚠️ Подписка скоро заканчивается!"

        if should_send:
            await bot.send_message(chat_id=master.chat_id_tg, text=message)

    except Exception as e:
        logging.error(f"Ошибка отправки уведомления: {e}")

# Функция для отправки уведомлений о записи
async def notify_master_appointment(
    master_id: uuid.UUID,
    notification_type: str,
    bot: Bot,
    session: AsyncSession
):
    """Отправка уведомления мастеру о записи"""
    from backend.database.bot_db_fcn import send_notification
    await send_notification(
        master_id=master_id,
        notification_type=notification_type,
        bot=bot,
        session=session
    )

# Пример использования при создании записи
async def on_appointment_created(
    appointment_id: uuid.UUID,
    master_id: uuid.UUID,
    bot: Bot,
    session: AsyncSession
):
    """Вызывается при создании новой записи"""
    await notify_master_appointment(
        master_id=master_id,
        notification_type="appointment",
        bot=bot,
        session=session
    )

# Пример использования при отмене записи
async def on_appointment_cancelled(
    appointment_id: uuid.UUID,
    master_id: uuid.UUID,
    bot: Bot,
    session: AsyncSession
):
    """Вызывается при отмене записи"""
    await notify_master_appointment(
        master_id=master_id,
        notification_type="appointment_cancel",
        bot=bot,
        session=session
    )