from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from backend.telegram_bot.bot_config import Config


def get_master_main_keyboard(master_id: str) -> InlineKeyboardMarkup:
    """Главное меню мастера"""
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Mini-app кнопка
    keyboard.add(
        InlineKeyboardButton(
            text="📱 Открыть Mini App",
            web_app=WebAppInfo(url=f"{Config.MINI_APP_URL}?master_id={master_id}")
        )
    )

    # Подписка
    keyboard.add(
        InlineKeyboardButton(text="💎 Моя подписка", callback_data="subscription_info"),
        InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="subscription_buy")
    )

    # Настройки уведомлений
    keyboard.add(
        InlineKeyboardButton(text="🔔 Настройки уведомлений", callback_data="notification_settings")
    )

    # Рефералы
    keyboard.add(
        InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals")
    )

    # Профиль
    keyboard.add(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")
    )

    return keyboard


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для покупки подписки"""
    keyboard = InlineKeyboardMarkup(row_width=1)

    for key, value in Config.SUBSCRIPTION_PRICES.items():
        emoji = "📅" if key == "month" else "📆" if key == "quarter" else "🗓️"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{emoji} {value['days']} дней - {value['price']}₽",
                callback_data=f"sub_buy_{key}"
            )
        )

    keyboard.add(
        InlineKeyboardButton(text="← Назад", callback_data="main_menu")
    )

    return keyboard


def get_notification_settings_keyboard(current_settings: dict) -> InlineKeyboardMarkup:
    """Клавиатура настроек уведомлений"""
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Уведомление о записи
    status_new = "✅" if current_settings.get('appointment_notification', True) else "❌"
    keyboard.add(
        InlineKeyboardButton(
            text=f"{status_new} Новая запись",
            callback_data="notif_toggle_appointment"
        )
    )

    # Уведомление об отмене
    status_cancel = "✅" if current_settings.get('appointment_cancel_notification', True) else "❌"
    keyboard.add(
        InlineKeyboardButton(
            text=f"{status_cancel} Отмена записи",
            callback_data="notif_toggle_cancel"
        )
    )

    # Уведомление о подтверждении
    status_confirm = "✅" if current_settings.get('appointment_confirm_notification', True) else "❌"
    keyboard.add(
        InlineKeyboardButton(
            text=f"{status_confirm} Подтверждение записи",
            callback_data="notif_toggle_confirm"
        )
    )

    keyboard.add(
        InlineKeyboardButton(text="← Назад", callback_data="main_menu")
    )

    return keyboard


def get_referral_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для рефералов"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(text="🔗 Ссылка (Мастера)", callback_data="ref_copy_master"),
        InlineKeyboardButton(text="🔗 Ссылка (Клиенты)", callback_data="ref_copy_user")
    )

    keyboard.add(
        InlineKeyboardButton(text="📊 Статистика", callback_data="ref_stats"),
        InlineKeyboardButton(text="← Назад", callback_data="main_menu")
    )

    return keyboard


def get_become_master_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для становления мастером"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="✅ Стать мастером", callback_data="become_master"),
        InlineKeyboardButton(text="❌ Остаться клиентом", callback_data="stay_client")
    )
    return keyboard