from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import uuid

from database import SessionLocal
from database.crud import get_user_by_telegram_id, get_subscription_by_id
from bot.keyboards import get_instructions_keyboard, get_main_menu_keyboard
from services.remnwave import remnwave_client
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def download_config_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправить конфигурационный файл"""
    query = update.callback_query
    await query.answer()

    # Извлекаем subscription_id из callback_data
    subscription_id = query.data.split('_')[-1]
    db: Session = SessionLocal()

    try:
        subscription = get_subscription_by_id(db, uuid.UUID(subscription_id))

        if not subscription:
            await query.answer("Подписка не найдена.", show_alert=True)
            return

        text = (
            "📥 Конфигурационный файл\n\n"
            f"🔗 Ссылка для скачивания:\n{subscription.config_url}\n\n"
            "Скопируйте ссылку и откройте в вашем VPN приложении."
        )

        await query.edit_message_text(text=text)

    except Exception as e:
        logger.error(f"Error in download_config_callback: {e}")
        await query.answer("Ошибка при получении конфигурации.", show_alert=True)
    finally:
        db.close()


async def show_qr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать QR-код для подключения"""
    query = update.callback_query
    await query.answer()

    # Извлекаем subscription_id из callback_data
    subscription_id = query.data.split('_')[-1]
    db: Session = SessionLocal()

    try:
        subscription = get_subscription_by_id(db, uuid.UUID(subscription_id))

        if not subscription:
            await query.answer("Подписка не найдена.", show_alert=True)
            return

        # TODO: Отправить QR-код как изображение
        # Здесь нужно декодировать base64 и отправить как фото
        text = (
            "📷 QR-код для быстрого подключения\n\n"
            "QR-код будет отправлен отдельным сообщением."
        )

        await query.edit_message_text(text=text)

    except Exception as e:
        logger.error(f"Error in show_qr_callback: {e}")
        await query.answer("Ошибка при получении QR-кода.", show_alert=True)
    finally:
        db.close()


async def help_instructions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню инструкций"""
    query = update.callback_query
    await query.answer()

    text = (
        "📱 Инструкции по подключению\n\n"
        "Выберите вашу операционную систему:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_instructions_keyboard()
    )


async def help_platform_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать инструкцию для конкретной платформы"""
    query = update.callback_query
    await query.answer()

    platform = query.data.split('_')[-1]

    instructions = {
        'ios': (
            "📱 Подключение на iOS\n\n"
            "Шаг 1️⃣: Установите приложение\n"
            "Скачайте WireGuard из App Store\n\n"
            "Шаг 2️⃣: Импортируйте конфигурацию\n"
            "• Откройте полученный QR-код\n"
            "• В приложении WireGuard нажмите '+'\n"
            "• Выберите 'Создать из QR-кода'\n"
            "• Отсканируйте QR-код\n\n"
            "Шаг 3️⃣: Активируйте VPN\n"
            "• Нажмите на переключатель рядом с конфигурацией\n"
            "• Подтвердите установку VPN профиля\n"
            "• Готово! VPN активен 🟢\n\n"
            "💡 Совет: Включите 'По требованию' для автоматического подключения"
        ),
        'android': (
            "🤖 Подключение на Android\n\n"
            "Шаг 1️⃣: Установите приложение\n"
            "Скачайте WireGuard из Google Play\n\n"
            "Шаг 2️⃣: Импортируйте конфигурацию\n"
            "• Откройте приложение WireGuard\n"
            "• Нажмите '+' в правом нижнем углу\n"
            "• Выберите 'Сканировать QR-код'\n"
            "• Отсканируйте полученный QR-код\n\n"
            "Шаг 3️⃣: Активируйте VPN\n"
            "• Нажмите на переключатель\n"
            "• Подтвердите VPN-подключение\n"
            "• Готово! VPN активен 🟢"
        ),
        'windows': (
            "💻 Подключение на Windows\n\n"
            "Шаг 1️⃣: Установите приложение\n"
            "Скачайте WireGuard с официального сайта:\n"
            "wireguard.com/install\n\n"
            "Шаг 2️⃣: Импортируйте конфигурацию\n"
            "• Откройте WireGuard\n"
            "• Нажмите 'Import tunnel(s) from file'\n"
            "• Выберите скачанный конфигурационный файл\n\n"
            "Шаг 3️⃣: Активируйте VPN\n"
            "• Нажмите 'Activate'\n"
            "• Готово! VPN активен 🟢"
        ),
        'macos': (
            "🍎 Подключение на MacOS\n\n"
            "Шаг 1️⃣: Установите приложение\n"
            "Скачайте WireGuard из App Store\n\n"
            "Шаг 2️⃣: Импортируйте конфигурацию\n"
            "• Откройте WireGuard\n"
            "• Нажмите 'Import tunnel(s) from file'\n"
            "• Выберите скачанный конфигурационный файл\n\n"
            "Шаг 3️⃣: Активируйте VPN\n"
            "• Нажмите 'Activate'\n"
            "• Готово! VPN активен 🟢"
        ),
        'linux': (
            "🐧 Подключение на Linux\n\n"
            "Установка через пакетный менеджер:\n\n"
            "Ubuntu/Debian:\n"
            "```\n"
            "sudo apt install wireguard\n"
            "```\n\n"
            "Fedora:\n"
            "```\n"
            "sudo dnf install wireguard-tools\n"
            "```\n\n"
            "Импорт конфигурации:\n"
            "```\n"
            "sudo wg-quick up /path/to/config.conf\n"
            "```"
        ),
        'router': (
            "🌐 Настройка на роутере\n\n"
            "Инструкция зависит от модели роутера.\n\n"
            "Общие шаги:\n"
            "1. Войдите в панель управления роутером\n"
            "2. Найдите раздел VPN или WireGuard\n"
            "3. Добавьте новое подключение\n"
            "4. Вставьте данные из конфигурационного файла\n\n"
            "Для получения детальной инструкции обратитесь в поддержку."
        )
    }

    text = instructions.get(platform, "Инструкция не найдена.")

    await query.edit_message_text(
        text=text,
        reply_markup=get_main_menu_keyboard()
    )
