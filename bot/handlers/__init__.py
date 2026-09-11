"""Handlers package"""
from .start import start_command, main_menu_callback
from .subscription import view_plans_callback, buy_plan_callback, my_subscriptions_callback
from .payment import pay_card_callback, check_payment_callback, cancel_order_callback
from .profile import (
    download_config_callback,
    show_qr_callback,
    help_instructions_callback,
    help_platform_callback
)
from .admin import admin_command, admin_stats_command

__all__ = [
    'start_command',
    'main_menu_callback',
    'view_plans_callback',
    'buy_plan_callback',
    'my_subscriptions_callback',
    'pay_card_callback',
    'check_payment_callback',
    'cancel_order_callback',
    'download_config_callback',
    'show_qr_callback',
    'help_instructions_callback',
    'help_platform_callback',
    'admin_command',
    'admin_stats_command'
]
