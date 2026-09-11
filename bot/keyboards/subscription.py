from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from database.models import Plan


def get_plans_keyboard(plans: List[Plan]) -> InlineKeyboardMarkup:
    """Клавиатура с тарифными планами"""
    keyboard = []

    for plan in plans:
        # Форматируем цену
        price_text = f"{int(plan.price)}₽"

        # Добавляем эмодзи для популярных планов
        emoji = ""
        if "годовой" in plan.name.lower() or "год" in plan.name.lower():
            emoji = "🔥 "

        button_text = f"{emoji}{plan.name} ({price_text})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"buy_plan_{plan.id}")
        ])

    keyboard.append([InlineKeyboardButton("« Назад в меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_payment_methods_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    keyboard = [
        [InlineKeyboardButton("💳 Банковская карта", callback_data=f"pay_card_{plan_id}")],
        [InlineKeyboardButton("🔐 Telegram Stars", callback_data=f"pay_telegram_{plan_id}")],
        [InlineKeyboardButton("₿ Криптовалюта", callback_data=f"pay_crypto_{plan_id}")],
        [InlineKeyboardButton("« Назад к тарифам", callback_data="view_plans")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_keyboard(order_id: str, payment_url: str) -> InlineKeyboardMarkup:
    """Клавиатура для оплаты заказа"""
    keyboard = [
        [InlineKeyboardButton("💳 Перейти к оплате", url=payment_url)],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"check_payment_{order_id}")],
        [InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_order_{order_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscription_details_keyboard(subscription_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для управления подпиской"""
    keyboard = [
        [InlineKeyboardButton("📥 Скачать конфиг", callback_data=f"download_config_{subscription_id}")],
        [InlineKeyboardButton("📷 QR-код", callback_data=f"show_qr_{subscription_id}")],
        [InlineKeyboardButton("🔄 Продлить", callback_data=f"renew_subscription_{subscription_id}")],
        [InlineKeyboardButton("🗑 Отменить подписку", callback_data=f"cancel_subscription_{subscription_id}")],
        [InlineKeyboardButton("« Назад", callback_data="my_subscriptions")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_no_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура когда нет активных подписок"""
    keyboard = [
        [InlineKeyboardButton("💳 Купить подписку", callback_data="buy_subscription")],
        [InlineKeyboardButton("💰 Посмотреть тарифы", callback_data="view_plans")],
        [InlineKeyboardButton("« Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
