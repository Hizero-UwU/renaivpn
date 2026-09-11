#!/usr/bin/env python3
"""
VPN Bot - Telegram бот для продажи VPN подписок
"""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from database import init_db
from bot.handlers import (
    start_command,
    main_menu_callback,
    view_plans_callback,
    buy_plan_callback,
    my_subscriptions_callback,
    pay_card_callback,
    check_payment_callback,
    cancel_order_callback,
    download_config_callback,
    show_qr_callback,
    help_instructions_callback,
    help_platform_callback,
    admin_command,
    admin_stats_command
)
from services.remnwave import remnwave_client
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def setup_handlers(application: Application) -> None:
    """Настройка обработчиков команд и callback"""

    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("admin_stats", admin_stats_command))

    # Главное меню и навигация
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    # Тарифы и подписки
    application.add_handler(CallbackQueryHandler(view_plans_callback, pattern="^view_plans$"))
    application.add_handler(CallbackQueryHandler(view_plans_callback, pattern="^buy_subscription$"))
    application.add_handler(CallbackQueryHandler(buy_plan_callback, pattern="^buy_plan_"))
    application.add_handler(CallbackQueryHandler(my_subscriptions_callback, pattern="^my_subscriptions$"))

    # Платежи
    application.add_handler(CallbackQueryHandler(pay_card_callback, pattern="^pay_card_"))
    application.add_handler(CallbackQueryHandler(check_payment_callback, pattern="^check_payment_"))
    application.add_handler(CallbackQueryHandler(cancel_order_callback, pattern="^cancel_order_"))

    # Управление подпиской
    application.add_handler(CallbackQueryHandler(download_config_callback, pattern="^download_config_"))
    application.add_handler(CallbackQueryHandler(show_qr_callback, pattern="^show_qr_"))

    # Инструкции
    application.add_handler(CallbackQueryHandler(help_instructions_callback, pattern="^help_instructions$"))
    application.add_handler(CallbackQueryHandler(help_platform_callback, pattern="^help_(ios|android|windows|macos|linux|router)$"))

    logger.info("Handlers registered successfully")


async def post_init(application: Application) -> None:
    """Инициализация после запуска бота"""
    logger.info("Bot started successfully")
    logger.info(f"Bot username: @{application.bot.username}")


async def post_shutdown(application: Application) -> None:
    """Очистка ресурсов при остановке"""
    logger.info("Shutting down bot...")
    await remnwave_client.close()
    logger.info("Bot stopped")


def main():
    """Точка входа в приложение"""
    try:
        # Инициализация базы данных
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized")

        # Создание приложения
        logger.info("Starting bot application...")
        application = (
            Application.builder()
            .token(settings.BOT_TOKEN)
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .build()
        )

        # Настройка обработчиков
        setup_handlers(application)

        # Запуск бота
        logger.info("Bot is polling for updates...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
