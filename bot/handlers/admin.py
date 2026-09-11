from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from database.models import User, Order, Subscription
from database.crud import get_user_by_telegram_id
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in settings.admin_ids


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin"""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    text = (
        "🔐 Админ-панель\n\n"
        "Доступные команды:\n"
        "/admin_stats - Статистика\n"
        "/admin_users - Управление пользователями\n"
        "/admin_orders - Заказы и платежи\n\n"
        "Используйте команды для управления системой."
    )

    await update.message.reply_text(text)


async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    db: Session = SessionLocal()

    try:
        # Получаем статистику
        total_users = db.query(func.count(User.id)).scalar()
        total_orders = db.query(func.count(Order.id)).scalar()
        paid_orders = db.query(func.count(Order.id)).filter(Order.status == 'paid').scalar()
        active_subscriptions = db.query(func.count(Subscription.id)).filter(
            Subscription.status == 'active'
        ).scalar()

        # Рассчитываем доход
        total_revenue = db.query(func.sum(Order.amount)).filter(
            Order.status == 'paid'
        ).scalar() or 0

        # Конверсия
        conversion_rate = (paid_orders / total_orders * 100) if total_orders > 0 else 0

        text = (
            "📊 Статистика\n\n"
            f"👥 Пользователи:\n"
            f"• Всего: {total_users}\n\n"
            f"💰 Финансы:\n"
            f"• Всего заказов: {total_orders}\n"
            f"• Оплачено: {paid_orders}\n"
            f"• Доход: {float(total_revenue):.2f}₽\n\n"
            f"📈 Подписки:\n"
            f"• Активных: {active_subscriptions}\n\n"
            f"🎯 Конверсия:\n"
            f"• Заказ → Оплата: {conversion_rate:.1f}%"
        )

        await update.message.reply_text(text)

    except Exception as e:
        logger.error(f"Error in admin_stats_command: {e}")
        await update.message.reply_text("Ошибка при получении статистики.")
    finally:
        db.close()
