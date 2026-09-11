"""Keyboards package"""
from .main import get_main_menu_keyboard, get_back_to_menu_keyboard
from .subscription import (
    get_plans_keyboard,
    get_payment_methods_keyboard,
    get_payment_keyboard,
    get_subscription_details_keyboard,
    get_no_subscription_keyboard
)
from .payment import (
    get_instructions_keyboard,
    get_support_menu_keyboard,
    get_faq_keyboard
)

__all__ = [
    'get_main_menu_keyboard',
    'get_back_to_menu_keyboard',
    'get_plans_keyboard',
    'get_payment_methods_keyboard',
    'get_payment_keyboard',
    'get_subscription_details_keyboard',
    'get_no_subscription_keyboard',
    'get_instructions_keyboard',
    'get_support_menu_keyboard',
    'get_faq_keyboard'
]
