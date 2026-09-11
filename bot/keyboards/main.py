from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [InlineKeyboardButton("💳 Купить подписку", callback_data="buy_subscription")],
        [InlineKeyboardButton("📊 Мои подписки", callback_data="my_subscriptions")],
        [InlineKeyboardButton("💰 Тарифы", callback_data="view_plans")],
        [InlineKeyboardButton("📱 Инструкции", callback_data="help_instructions")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("« Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
