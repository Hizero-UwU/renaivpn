from datetime import datetime, timedelta
from typing import Optional
import pytz


def format_price(amount: float, currency: str = "RUB") -> str:
    """Форматирование цены для отображения"""
    symbols = {
        "RUB": "₽",
        "USD": "$",
        "EUR": "€"
    }
    symbol = symbols.get(currency, currency)
    return f"{amount:.0f}{symbol}"


def format_datetime(dt: datetime, tz: str = "Europe/Moscow") -> str:
    """Форматирование даты и времени для отображения"""
    timezone = pytz.timezone(tz)
    local_dt = dt.astimezone(timezone)
    return local_dt.strftime("%d.%m.%Y %H:%M")


def format_date(dt: datetime, tz: str = "Europe/Moscow") -> str:
    """Форматирование даты для отображения"""
    timezone = pytz.timezone(tz)
    local_dt = dt.astimezone(timezone)
    return local_dt.strftime("%d.%m.%Y")


def days_until(target_date: datetime) -> int:
    """Количество дней до указанной даты"""
    now = datetime.utcnow()
    delta = target_date - now
    return max(0, delta.days)


def format_traffic(bytes_count: int) -> str:
    """Форматирование трафика в читаемый вид"""
    gb = bytes_count / (1024 ** 3)
    if gb < 1:
        mb = bytes_count / (1024 ** 2)
        return f"{mb:.1f} МБ"
    return f"{gb:.1f} ГБ"


def generate_order_id() -> str:
    """Генерация короткого ID заказа"""
    import uuid
    return str(uuid.uuid4())[:8].upper()


def is_subscription_expiring_soon(expires_at: datetime, days: int = 3) -> bool:
    """Проверка, истекает ли подписка скоро"""
    return days_until(expires_at) <= days
