from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import uuid

from database import SessionLocal
from database.crud import (
    get_user_by_telegram_id, get_plan_by_id,
    get_order_by_id, update_order_status
)
from bot.keyboards import get_payment_keyboard, get_main_menu_keyboard
from services.subscription import subscription_service
from services.payment import payment_service
from utils.helpers import format_price, generate_order_id
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def pay_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оплата банковской картой через ЮKassa"""
    query = update.callback_query
    await query.answer()

    # Извлекаем plan_id из callback_data
    plan_id = int(query.data.split('_')[-1])
    user = update.effective_user
    db: Session = SessionLocal()

    try:
        db_user = get_user_by_telegram_id(db, user.id)
        plan = get_plan_by_id(db, plan_id)

        if not db_user or not plan:
            await query.edit_message_text("Ошибка при создании заказа.")
            return

        # Создаем заказ
        order = await subscription_service.create_subscription_order(
            db=db,
            user=db_user,
            plan_id=plan_id
        )

        # Инициируем платеж
        payment_data = await subscription_service.initiate_payment(
            db=db,
            order=order
        )

        short_order_id = str(order.id)[:8].upper()

        text = (
            "💳 Оплата банковской картой\n\n"
            f"Сумма к оплате: {format_price(float(order.amount))}\n\n"
            "После нажатия кнопки вы будете перенаправлены на "
            "защищенную страницу оплаты.\n\n"
            f"Ваш заказ: #{short_order_id}\n"
            "Заказ действителен 15 минут."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_payment_keyboard(str(order.id), payment_data['payment_url'])
        )

    except Exception as e:
        logger.error(f"Error in pay_card_callback: {e}")
        await query.edit_message_text(
            "Произошла ошибка при создании платежа. Попробуйте позже."
        )
    finally:
        db.close()


async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверить статус платежа"""
    query = update.callback_query
    await query.answer("Проверяем статус платежа...")

    # Извлекаем order_id из callback_data
    order_id = query.data.split('_')[-1]
    db: Session = SessionLocal()

    try:
        order = get_order_by_id(db, uuid.UUID(order_id))

        if not order:
            await query.edit_message_text("Заказ не найден.")
            return

        # Проверяем статус платежа
        payment_status = payment_service.get_payment_status(order.payment_id)

        if payment_status['paid']:
            # Платеж успешен
            update_order_status(db, order, 'paid')

            # Активируем подписку
            subscription = await subscription_service.process_payment_and_activate(
                db=db,
                order=order
            )

            text = (
                "✅ Оплата прошла успешно!\n\n"
                f"Ваша подписка активирована до: {subscription.expires_at.strftime('%d.%m.%Y')}\n\n"
                "📱 Данные для подключения отправлены вам отдельным сообщением.\n\n"
                "Спасибо за покупку!"
            )

            # Отправляем конфигурацию отдельным сообщением
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=(
                    "📥 Данные для подключения:\n\n"
                    f"🔗 Конфигурационный файл: {subscription.config_url}\n\n"
                    "📷 QR-код для быстрого подключения будет отправлен следующим сообщением.\n\n"
                    "Инструкции по подключению: /help"
                )
            )

            await query.edit_message_text(
                text=text,
                reply_markup=get_main_menu_keyboard()
            )

        elif payment_status['status'] == 'canceled':
            update_order_status(db, order, 'failed')
            await query.answer("Платеж отменен.", show_alert=True)

        else:
            await query.answer("Платеж еще не завершен. Попробуйте через минуту.", show_alert=True)

    except Exception as e:
        logger.error(f"Error in check_payment_callback: {e}")
        await query.answer("Ошибка при проверке платежа.", show_alert=True)
    finally:
        db.close()


async def cancel_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить заказ"""
    query = update.callback_query
    await query.answer()

    # Извлекаем order_id из callback_data
    order_id = query.data.split('_')[-1]
    db: Session = SessionLocal()

    try:
        order = get_order_by_id(db, uuid.UUID(order_id))

        if not order:
            await query.edit_message_text("Заказ не найден.")
            return

        # Отменяем платеж
        if order.payment_id:
            payment_service.cancel_payment(order.payment_id)

        # Обновляем статус заказа
        update_order_status(db, order, 'expired')

        text = "❌ Заказ отменен.\n\nВы можете создать новый заказ в любое время."

        await query.edit_message_text(
            text=text,
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in cancel_order_callback: {e}")
        await query.edit_message_text("Ошибка при отмене заказа.")
    finally:
        db.close()
