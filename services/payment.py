from yookassa import Configuration, Payment
from typing import Dict, Optional
from decimal import Decimal
import uuid

from utils.logger import setup_logger
from utils.config import settings

logger = setup_logger(__name__)

# Configure YooKassa
Configuration.account_id = settings.YUKASSA_SHOP_ID
Configuration.secret_key = settings.YUKASSA_SECRET_KEY


class PaymentService:
    """Сервис для работы с платежами через ЮKassa"""

    @staticmethod
    def create_payment(
        amount: Decimal,
        order_id: uuid.UUID,
        description: str,
        return_url: str = None
    ) -> Dict:
        """
        Создать платеж в ЮKassa

        Args:
            amount: Сумма платежа
            order_id: ID заказа
            description: Описание платежа
            return_url: URL для возврата после оплаты

        Returns:
            {
                'payment_id': '...',
                'payment_url': '...',
                'status': 'pending'
            }
        """
        try:
            payment = Payment.create({
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or f"{settings.APP_URL}/payment/success"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "order_id": str(order_id)
                }
            }, uuid.uuid4())

            logger.info(f"Payment created: {payment.id} for order {order_id}")

            return {
                'payment_id': payment.id,
                'payment_url': payment.confirmation.confirmation_url,
                'status': payment.status
            }

        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise

    @staticmethod
    def get_payment_status(payment_id: str) -> Dict:
        """
        Получить статус платежа

        Returns:
            {
                'payment_id': '...',
                'status': 'pending|succeeded|canceled',
                'paid': bool,
                'amount': Decimal,
                'metadata': {...}
            }
        """
        try:
            payment = Payment.find_one(payment_id)

            return {
                'payment_id': payment.id,
                'status': payment.status,
                'paid': payment.paid,
                'amount': Decimal(payment.amount.value),
                'metadata': payment.metadata
            }

        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            raise

    @staticmethod
    def verify_webhook_signature(headers: Dict, body: str) -> bool:
        """
        Проверить подпись webhook от ЮKassa

        Args:
            headers: HTTP заголовки запроса
            body: Тело запроса (raw string)

        Returns:
            True если подпись валидна
        """
        # TODO: Implement signature verification
        # https://yookassa.ru/developers/using-api/webhooks#verifying-signature
        return True

    @staticmethod
    def cancel_payment(payment_id: str) -> Dict:
        """
        Отменить платеж

        Returns:
            {
                'payment_id': '...',
                'status': 'canceled'
            }
        """
        try:
            payment = Payment.cancel(payment_id, uuid.uuid4())

            logger.info(f"Payment cancelled: {payment_id}")

            return {
                'payment_id': payment.id,
                'status': payment.status
            }

        except Exception as e:
            logger.error(f"Failed to cancel payment: {e}")
            raise


# Singleton instance
payment_service = PaymentService()
