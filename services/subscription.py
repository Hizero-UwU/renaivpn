from sqlalchemy.orm import Session
from typing import Optional, Dict
import uuid

from database.models import User, Plan, Order, Subscription
from database.crud import (
    create_order, create_subscription, get_plan_by_id,
    update_order_status, get_user_active_subscriptions
)
from services.remnwave import remnwave_client
from services.payment import payment_service
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SubscriptionService:
    """Сервис для управления подписками"""

    @staticmethod
    async def create_subscription_order(
        db: Session,
        user: User,
        plan_id: int
    ) -> Order:
        """
        Создать заказ на подписку

        Args:
            db: Database session
            user: Пользователь
            plan_id: ID тарифного плана

        Returns:
            Order объект
        """
        plan = get_plan_by_id(db, plan_id)
        if not plan:
            raise ValueError(f"План {plan_id} не найден")

        # Создаем заказ
        order = create_order(
            db=db,
            user_id=user.id,
            plan_id=plan.id,
            amount=float(plan.price),
            currency=plan.currency
        )

        logger.info(f"Order created: {order.id} for user {user.telegram_id}")
        return order

    @staticmethod
    async def process_payment_and_activate(
        db: Session,
        order: Order
    ) -> Subscription:
        """
        Обработать успешный платеж и активировать подписку

        Args:
            db: Database session
            order: Заказ

        Returns:
            Subscription объект
        """
        try:
            # Получаем план
            plan = get_plan_by_id(db, order.plan_id)

            # Создаем VPN аккаунт через Remnwave API
            remnwave_account = await remnwave_client.create_account(
                user_id=str(order.user.telegram_id),
                plan=plan.remnwave_plan_id or plan.slug,
                duration_days=plan.duration_days
            )

            # Создаем подписку в БД
            subscription = create_subscription(
                db=db,
                user_id=order.user_id,
                order_id=order.id,
                remnwave_account_id=remnwave_account['account_id'],
                config_url=remnwave_account['config_url'],
                qr_code=remnwave_account['qr_code'],
                duration_days=plan.duration_days
            )

            logger.info(f"Subscription activated: {subscription.id} for user {order.user.telegram_id}")
            return subscription

        except Exception as e:
            logger.error(f"Failed to activate subscription: {e}")
            raise

    @staticmethod
    async def initiate_payment(
        db: Session,
        order: Order,
        return_url: Optional[str] = None
    ) -> Dict:
        """
        Инициировать платеж через платежную систему

        Args:
            db: Database session
            order: Заказ
            return_url: URL для возврата после оплаты

        Returns:
            Dict с данными платежа
        """
        try:
            plan = get_plan_by_id(db, order.plan_id)

            # Создаем платеж
            payment_data = payment_service.create_payment(
                amount=order.amount,
                order_id=order.id,
                description=f"Оплата подписки: {plan.name}",
                return_url=return_url
            )

            # Обновляем заказ
            update_order_status(
                db=db,
                order=order,
                status='pending',
                payment_id=payment_data['payment_id'],
                payment_url=payment_data['payment_url']
            )

            logger.info(f"Payment initiated: {payment_data['payment_id']} for order {order.id}")
            return payment_data

        except Exception as e:
            logger.error(f"Failed to initiate payment: {e}")
            raise

    @staticmethod
    def check_active_subscription(db: Session, user: User) -> Optional[Subscription]:
        """
        Проверить наличие активной подписки у пользователя

        Args:
            db: Database session
            user: Пользователь

        Returns:
            Активная подписка или None
        """
        active_subscriptions = get_user_active_subscriptions(db, user.id)
        return active_subscriptions[0] if active_subscriptions else None


# Singleton instance
subscription_service = SubscriptionService()
