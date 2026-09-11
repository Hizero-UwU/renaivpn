from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database.connection import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language_code = Column(String(10))
    role = Column(String(50), default='user')
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    subscriptions = relationship('Subscription', back_populates='user', cascade='all, delete-orphan')
    support_tickets = relationship('SupportTicket', back_populates='user', cascade='all, delete-orphan')


class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='RUB')
    duration_days = Column(Integer, nullable=False)
    devices_count = Column(Integer, default=1)
    remnwave_plan_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship('Order', back_populates='plan')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='RUB')
    status = Column(String(50), nullable=False, index=True)  # pending, paid, failed, expired
    payment_provider = Column(String(50))
    payment_id = Column(String(255))
    payment_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship('User', back_populates='orders')
    plan = relationship('Plan', back_populates='orders')
    subscription = relationship('Subscription', back_populates='order', uselist=False)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'))
    remnwave_account_id = Column(String(255), nullable=False)
    config_url = Column(Text)
    qr_code = Column(Text)
    expires_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)  # active, expired, cancelled
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='subscriptions')
    order = relationship('Order', back_populates='subscription')
    auto_renewal = relationship('AutoRenewal', back_populates='subscription', uselist=False, cascade='all, delete-orphan')


class AutoRenewal(Base):
    __tablename__ = 'auto_renewals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id', ondelete='CASCADE'), nullable=False)
    payment_method_token = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    last_attempt_at = Column(DateTime, nullable=True)
    next_attempt_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship('Subscription', back_populates='auto_renewal')


class SupportTicket(Base):
    __tablename__ = 'support_tickets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subject = Column(String(255))
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, index=True)  # open, in_progress, resolved, closed
    priority = Column(String(50), default='medium')  # low, medium, high
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='support_tickets', foreign_keys=[user_id])
    messages = relationship('TicketMessage', back_populates='ticket', cascade='all, delete-orphan')


class TicketMessage(Base):
    __tablename__ = 'ticket_messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('support_tickets.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ticket = relationship('SupportTicket', back_populates='messages')


class PromoCode(Base):
    __tablename__ = 'promo_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False)  # percentage, fixed
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    max_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    usages = relationship('PromoCodeUsage', back_populates='promo_code')


class PromoCodeUsage(Base):
    __tablename__ = 'promo_code_usages'

    id = Column(Integer, primary_key=True)
    promo_code_id = Column(Integer, ForeignKey('promo_codes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'))
    discount_amount = Column(DECIMAL(10, 2))
    used_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    promo_code = relationship('PromoCode', back_populates='usages')

