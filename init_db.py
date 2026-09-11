#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных с тестовыми тарифными планами
"""
from database import SessionLocal, init_db
from database.models import Plan
from utils.logger import setup_logger

logger = setup_logger(__name__)


def init_plans():
    """Создать тестовые тарифные планы"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже планы
        existing_plans = db.query(Plan).count()
        if existing_plans > 0:
            logger.info(f"Plans already exist ({existing_plans} plans found)")
            return

        plans = [
            Plan(
                name="Месячный",
                slug="monthly",
                description="1 месяц безлимитного VPN",
                price=299.00,
                currency="RUB",
                duration_days=30,
                devices_count=1,
                remnwave_plan_id="monthly_plan",
                is_active=True
            ),
            Plan(
                name="Квартальный",
                slug="quarterly",
                description="3 месяца безлимитного VPN со скидкой 22%",
                price=699.00,
                currency="RUB",
                duration_days=90,
                devices_count=2,
                remnwave_plan_id="quarterly_plan",
                is_active=True
            ),
            Plan(
                name="Годовой",
                slug="yearly",
                description="12 месяцев безлимитного VPN со скидкой 44%",
                price=1999.00,
                currency="RUB",
                duration_days=365,
                devices_count=5,
                remnwave_plan_id="yearly_plan",
                is_active=True
            )
        ]

        db.add_all(plans)
        db.commit()

        logger.info(f"Created {len(plans)} plans successfully")

        for plan in plans:
            logger.info(f"  - {plan.name}: {plan.price} {plan.currency} for {plan.duration_days} days")

    except Exception as e:
        logger.error(f"Error initializing plans: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

    logger.info("Creating plans...")
    init_plans()
    logger.info("Setup completed successfully!")
