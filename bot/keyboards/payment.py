from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_instructions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора платформы для инструкций"""
    keyboard = [
        [InlineKeyboardButton("📱 iOS", callback_data="help_ios")],
        [InlineKeyboardButton("🤖 Android", callback_data="help_android")],
        [InlineKeyboardButton("💻 Windows", callback_data="help_windows")],
        [InlineKeyboardButton("🍎 MacOS", callback_data="help_macos")],
        [InlineKeyboardButton("🐧 Linux", callback_data="help_linux")],
        [InlineKeyboardButton("🌐 Роутеры", callback_data="help_router")],
        [InlineKeyboardButton("« Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_support_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура меню поддержки"""
    keyboard = [
        [InlineKeyboardButton("📚 База знаний (FAQ)", callback_data="faq")],
        [InlineKeyboardButton("✉️ Создать обращение", callback_data="support_ticket")],
        [InlineKeyboardButton("👤 Связаться с оператором", callback_data="support_contact")],
        [InlineKeyboardButton("« Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_faq_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура категорий FAQ"""
    keyboard = [
        [InlineKeyboardButton("🔐 Безопасность", callback_data="faq_security")],
        [InlineKeyboardButton("⚡️ Проблемы со скоростью", callback_data="faq_speed")],
        [InlineKeyboardButton("🌐 Выбор сервера", callback_data="faq_servers")],
        [InlineKeyboardButton("💳 Оплата и возврат", callback_data="faq_payment")],
        [InlineKeyboardButton("📱 Проблемы с подключением", callback_data="faq_connection")],
        [InlineKeyboardButton("🔄 Продление и отмена", callback_data="faq_subscription")],
        [InlineKeyboardButton("« Назад", callback_data="support_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
