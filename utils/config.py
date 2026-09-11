from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Bot Configuration
    BOT_TOKEN: str
    ADMIN_USER_IDS: str

    # Database
    DATABASE_URL: str

    # Remnwave API
    REMNWAVE_API_KEY: str
    REMNWAVE_API_URL: str

    # Payment Provider (ЮKassa)
    YUKASSA_SHOP_ID: str
    YUKASSA_SECRET_KEY: str
    YUKASSA_WEBHOOK_SECRET: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Application
    APP_URL: str
    WEBHOOK_PATH: str = "/webhook/telegram"
    PAYMENT_WEBHOOK_PATH: str = "/webhook/payment"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def admin_ids(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        return [int(uid.strip()) for uid in self.ADMIN_USER_IDS.split(',')]


settings = Settings()
