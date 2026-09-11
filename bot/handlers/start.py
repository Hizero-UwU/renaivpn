from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database import SessionLocal
from database.crud import get_user_by_telegram_id, create_user
from bot.keyboards import get_main_menu_keyboard
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    db: Session = SessionLocal()

    try:
        # Проверяем, есть ли пользователь в БД
        db_user = get_user_by_telegram_id(db, user.id)

        if not db_user:
            # Создаем нового пользователя
            db_user = create_user(
                db=db,
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
            logger.info(f"New user created: {user.id}")

            # Приветственное сообщение для нового пользователя
            welcome_text = (
                "🌐 Добро пожаловать в RenaiVPN!\n\n"
                "Защитите свою конфиденциальность в интернете с помощью "
                "нашего быстрого и надежного VPN-сервиса.\n\n"
                "✅ Высокая скорость\n"
                "✅ Без логов\n"
                "✅ Серверы в 50+ странах\n"
                "✅ Поддержка 24/7\n\n"
                "Выберите действие:"
            )
        else:
            # Сообщение для существующего пользователя
            welcome_text = (
                f"👋 С возвращением, {user.first_name}!\n\n"
                "Выберите действие:"
            )

        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text(
            "Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        )
    finally:
        db.close()


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик возврата в главное меню"""
    query = update.callback_query
    await query.answer()

    text = "📋 Главное меню\n\nВыберите действие:"

    await query.edit_message_text(
        text=text,
        reply_markup=get_main_menu_keyboard()
    )
