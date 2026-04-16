import logging
import uuid
from datetime import date
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery, LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import SubscriptionModel

from backend.telegram_bot.keyboards import get_subscription_keyboard, get_master_main_keyboard
from backend.telegram_bot.bot_config import Config


'''async def callback_subscription_info(callback: CallbackQuery, session: AsyncSession):
    """Информация о подписке"""
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        await callback.answer("❌ Мастер не найден", show_alert=True)
        return

    is_active, end_date = await get_subscription_status(master_id, session)

    if is_active:
        days_left = (end_date - date.today()).days
        text = (
            "💎 Ваша подписка активна!\n\n"
            f"📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n"
            f"⏳ Осталось дней: {days_left}"
        )
    else:
        text = (
            "❌ Подписка не активна\n\n"
            "Приобретите подписку для доступа ко всем функциям."
        )

    await callback.message.edit_text(text, reply_markup=get_subscription_keyboard())
    await callback.answer()


async def callback_subscription_buy(callback: CallbackQuery, session: AsyncSession):
    """Покупка подписки"""
    await callback.message.edit_text(
        "💎 Выберите тариф подписки:\n\n"
        "📅 Месяц - 990₽\n"
        "📆 Квартал - 2490₽ (выгода 15%)\n"
        "🗓️ Год - 7990₽ (выгода 30%)",
        reply_markup=get_subscription_keyboard()
    )
    await callback.answer()


async def callback_subscription_purchase(callback: CallbackQuery, session: AsyncSession):
    """Обработка покупки подписки"""
    tariff = callback.data.split("_")[-1]
    chat_id = callback.from_user.id
    master_id, _ = await check_account_type(chat_id, session)

    if not master_id:
        await callback.answer("❌ Мастер не найден", show_alert=True)
        return

    if tariff not in Config.SUBSCRIPTION_PRICES:
        await callback.answer("❌ Неверный тариф", show_alert=True)
        return

    tariff_info = Config.SUBSCRIPTION_PRICES[tariff]

    await callback.message.bot.send_invoice(
        chat_id=chat_id,
        title=f"Подписка на {tariff_info['days']} дней",
        description="Оплата подписки для мастера",
        payload=f"sub_{master_id}_{tariff}",
        provider_token="",
        currency="RUB",
        prices=[LabeledPrice(label="Подписка", amount=tariff_info['price'] * 100)],
        start_parameter=f"sub_{tariff}",
        need_name=True,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
    )
    await callback.answer()


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """Обработка предоплаты"""
    await pre_checkout_query.answer(ok=True)


async def process_successful_payment(message: types.Message, session: AsyncSession):
    """Обработка успешной оплаты"""
    payload = message.successful_payment.invoice_payload
    parts = payload.split("_")

    if len(parts) >= 3 and parts[0] == "sub":
        master_id = parts[1]
        tariff = parts[2]

        try:
            master_uuid = uuid.UUID(master_id)
            tariff_info = Config.SUBSCRIPTION_PRICES[tariff]

            result = await create_subscription(
                master_id=master_uuid,
                duration_days=tariff_info['days'],
                payment_amount=tariff_info['price'],
                session=session
            )

            if result == "success":
                await message.answer("✅ Оплата прошла успешно!\n\nВаша подписка активирована.")
            else:
                await message.answer("❌ Произошла ошибка при активации подписки.")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {str(e)}")
            logging.error(f"Ошибка оплаты: {e}")


def register_handlers(dp):
    """Регистрация хендлеров этого модуля"""
    dp.register_callback_query_handler(callback_subscription_info, text="subscription_info")
    dp.register_callback_query_handler(callback_subscription_buy, text="subscription_buy")
    dp.register_callback_query_handler(
        callback_subscription_purchase,
        lambda c: c.data.startswith("sub_buy_")
    )
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(
        process_successful_payment,
        content_types=["successful_payment"]
    )'''