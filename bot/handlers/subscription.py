from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from database import SessionLocal
from database.crud import (
    get_user_by_telegram_id, get_all_active_plans,
    get_plan_by_id, get_user_active_subscriptions
)
from bot.keyboards import (
    get_plans_keyboard, get_payment_methods_keyboard,
    get_subscription_details_keyboard, get_no_subscription_keyboard
)
from services.subscription import subscription_service
from utils.helpers import format_date, format_price, days_until, format_traffic
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def view_plans_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать тарифные планы"""
    query = update.callback_query
    await query.answer()

    db: Session = SessionLocal()

    try:
        plans = get_all_active_plans(db)

        if not plans:
            await query.edit_message_text(
                "К сожалению, тарифы временно недоступны.\n"
                "Попробуйте позже или обратитесь в поддержку."
            )
            return

        # Формируем сообщение с тарифами
        text = "💎 Наши тарифы\n\n"

        for plan in plans:
            price_per_month = float(plan.price) / (plan.duration_days / 30)
            discount = ""

            if plan.duration_days >= 365:
                discount = f"\n💰 Скидка 44% ({int(price_per_month)}₽/мес)"
            elif plan.duration_days >= 90:
                discount = f"\n💰 Скидка 22% ({int(price_per_month)}₽/мес)"

            text += (
                f"📅 {plan.name.upper()} - {format_price(float(plan.price))}{discount}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✓ {plan.devices_count} устройств{'о' if plan.devices_count == 1 else 'а'}\n"
                f"✓ Безлимитный трафик\n"
                f"✓ Все серверы\n"
            )

            if plan.duration_days >= 365:
                text += "✓ Приоритетная поддержка\n✓ Статический IP\n"
            elif plan.duration_days >= 90:
                text += "✓ Приоритетная поддержка\n"

            text += "\n"

        text += "Выберите подходящий тариф:"

        await query.edit_message_text(
            text=text,
            reply_markup=get_plans_keyboard(plans)
        )

    except Exception as e:
        logger.error(f"Error in view_plans_callback: {e}")
        await query.edit_message_text("Произошла ошибка при загрузке тарифов.")
    finally:
        db.close()


async def buy_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать покупку выбранного тарифа"""
    query = update.callback_query
    await query.answer()

    # Извлекаем plan_id из callback_data
    plan_id = int(query.data.split('_')[-1])
    db: Session = SessionLocal()

    try:
        plan = get_plan_by_id(db, plan_id)
        if not plan:
            await query.edit_message_text("Тариф не найден.")
            return

        text = (
            f"✅ Вы выбрали тариф: {plan.name.upper()}\n\n"
            f"💰 Стоимость: {format_price(float(plan.price))}\n"
            f"⏱ Срок действия: {plan.duration_days} дней\n"
            f"📱 Устройств: {plan.devices_count}\n\n"
            f"Выберите способ оплаты:"
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_payment_methods_keyboard(plan_id)
        )

    except Exception as e:
        logger.error(f"Error in buy_plan_callback: {e}")
        await query.edit_message_text("Произошла ошибка при обработке заказа.")
    finally:
        db.close()


async def my_subscriptions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать подписки пользователя"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    db: Session = SessionLocal()

    try:
        db_user = get_user_by_telegram_id(db, user.id)
        if not db_user:
            await query.edit_message_text("Пользователь не найден.")
            return

        subscriptions = get_user_active_subscriptions(db, db_user.id)

        if not subscriptions:
            text = (
                "📊 Ваши подписки\n\n"
                "У вас пока нет активных подписок.\n\n"
                "💡 Выберите подходящий тариф и начните пользоваться "
                "безопасным интернетом!"
            )
            await query.edit_message_text(
                text=text,
                reply_markup=get_no_subscription_keyboard()
            )
            return

        # Показываем информацию о первой активной подписке
        subscription = subscriptions[0]
        days_left = days_until(subscription.expires_at)

        text = (
            "📊 Ваши подписки\n\n"
            "🟢 АКТИВНАЯ ПОДПИСКА\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 Активна до: {format_date(subscription.expires_at)} "
            f"(осталось {days_left} дней)\n"
            f"🆔 ID подписки: {str(subscription.id)[:8]}\n\n"
            "Управление подпиской:"
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_subscription_details_keyboard(str(subscription.id))
        )

    except Exception as e:
        logger.error(f"Error in my_subscriptions_callback: {e}")
        await query.edit_message_text("Произошла ошибка при загрузке подписок.")
    finally:
        db.close()
