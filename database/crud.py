from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from database.models import User, Plan, Order, Subscription, AutoRenewal, SupportTicket, PromoCode
import uuid


# ==================== USER CRUD ====================

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(db: Session, telegram_id: int, username: str = None,
                first_name: str = None, last_name: str = None,
                language_code: str = None) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, **kwargs) -> User:
    """Обновить данные пользователя"""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# ==================== PLAN CRUD ====================

def get_all_active_plans(db: Session) -> List[Plan]:
    """Получить все активные тарифные планы"""
    return db.query(Plan).filter(Plan.is_active == True).all()


def get_plan_by_id(db: Session, plan_id: int) -> Optional[Plan]:
    """Получить тарифный план по ID"""
    return db.query(Plan).filter(Plan.id == plan_id).first()


def get_plan_by_slug(db: Session, slug: str) -> Optional[Plan]:
    """Получить тарифный план по slug"""
    return db.query(Plan).filter(Plan.slug == slug).first()


# ==================== ORDER CRUD ====================

def create_order(db: Session, user_id: int, plan_id: int,
                 amount: float, currency: str = 'RUB',
                 payment_provider: str = 'yukassa') -> Order:
    """Создать новый заказ"""
    order = Order(
        id=uuid.uuid4(),
        user_id=user_id,
        plan_id=plan_id,
        amount=amount,
        currency=currency,
        status='pending',
        payment_provider=payment_provider,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order_by_id(db: Session, order_id: uuid.UUID) -> Optional[Order]:
    """Получить заказ по ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_by_payment_id(db: Session, payment_id: str) -> Optional[Order]:
    """Получить заказ по ID платежа в платежной системе"""
    return db.query(Order).filter(Order.payment_id == payment_id).first()


def update_order_status(db: Session, order: Order, status: str,
                       payment_id: str = None, payment_url: str = None) -> Order:
    """Обновить статус заказа"""
    order.status = status
    if payment_id:
        order.payment_id = payment_id
    if payment_url:
        order.payment_url = payment_url
    if status == 'paid':
        order.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


# ==================== SUBSCRIPTION CRUD ====================

def create_subscription(db: Session, user_id: int, order_id: uuid.UUID,
                       remnwave_account_id: str, config_url: str,
                       qr_code: str, duration_days: int) -> Subscription:
    """Создать новую подписку"""
    subscription = Subscription(
        id=uuid.uuid4(),
        user_id=user_id,
        order_id=order_id,
        remnwave_account_id=remnwave_account_id,
        config_url=config_url,
        qr_code=qr_code,
        expires_at=datetime.utcnow() + timedelta(days=duration_days),
        status='active'
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_user_active_subscriptions(db: Session, user_id: int) -> List[Subscription]:
    """Получить активные подписки пользователя"""
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == 'active',
        Subscription.expires_at > datetime.utcnow()
    ).all()


def get_subscription_by_id(db: Session, subscription_id: uuid.UUID) -> Optional[Subscription]:
    """Получить подписку по ID"""
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def update_subscription_status(db: Session, subscription: Subscription, status: str) -> Subscription:
    """Обновить статус подписки"""
    subscription.status = status
    subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    return subscription


def extend_subscription(db: Session, subscription: Subscription, additional_days: int) -> Subscription:
    """Продлить подписку"""
    subscription.expires_at += timedelta(days=additional_days)
    subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    return subscription


# ==================== SUPPORT TICKET CRUD ====================

def create_support_ticket(db: Session, user_id: int, subject: str,
                         description: str, priority: str = 'medium') -> SupportTicket:
    """Создать тикет в поддержку"""
    ticket = SupportTicket(
        id=uuid.uuid4(),
        user_id=user_id,
        subject=subject,
        description=description,
        status='open',
        priority=priority
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_user_tickets(db: Session, user_id: int) -> List[SupportTicket]:
    """Получить все тикеты пользователя"""
    return db.query(SupportTicket).filter(
        SupportTicket.user_id == user_id
    ).order_by(SupportTicket.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: uuid.UUID) -> Optional[SupportTicket]:
    """Получить тикет по ID"""
    return db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()


# ==================== PROMO CODE CRUD ====================

def get_promo_code_by_code(db: Session, code: str) -> Optional[PromoCode]:
    """Получить промокод по коду"""
    return db.query(PromoCode).filter(
        PromoCode.code == code.upper(),
        PromoCode.is_active == True
    ).first()


def validate_promo_code(db: Session, promo_code: PromoCode) -> tuple[bool, str]:
    """Проверить валидность промокода"""
    now = datetime.utcnow()

    if not promo_code.is_active:
        return False, "Промокод неактивен"

    if promo_code.valid_until and promo_code.valid_until < now:
        return False, "Промокод истек"

    if promo_code.valid_from > now:
        return False, "Промокод еще не активен"

    if promo_code.max_uses and promo_code.current_uses >= promo_code.max_uses:
        return False, "Промокод исчерпан"

    return True, "OK"
