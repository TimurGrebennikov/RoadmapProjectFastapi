import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.celery_app import celery_app
from src.config import DATA_BASE_URL_ASYNC
from src.db.models import Parcel
from src.domain.services.currency import CurrencyService

logger = logging.getLogger(__name__)

# Создание async engine для Celery задач
engine = create_async_engine(DATA_BASE_URL_ASYNC, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@celery_app.task(name="src.tasks.delivery_cost.calculate_delivery_costs")
def calculate_delivery_costs() -> None:
    """
    Периодическая задача расчёта стоимости доставки.
    Выполняется каждые 5 минут.
    """
    import asyncio

    asyncio.run(_calculate_delivery_costs_async())


async def _calculate_delivery_costs_async() -> None:
    """Асинхронная реализация расчёта стоимости доставки"""
    logger.info("Начинаем расчёт стоимости доставки...")

    # 1. Получить курс USD
    currency_service = CurrencyService()
    try:
        usd_rate = await currency_service.get_usd_rate()
        logger.info(f"Курс USD для расчёта: {usd_rate}")
    except Exception as e:
        logger.error(f"Не удалось получить курс USD: {e}")
        return

    # 2. Найти все посылки без стоимости доставки
    async with AsyncSessionLocal() as session:
        query = select(Parcel).where(Parcel.delivery_cost_rub.is_(None))
        result = await session.execute(query)
        parcels = result.scalars().all()

        if not parcels:
            logger.info("Нет посылок для расчёта стоимости")
            return

        logger.info(f"Найдено {len(parcels)} посылок для расчёта")

        # 3. Рассчитать и обновить стоимость для каждой посылки
        for parcel in parcels:
            delivery_cost = (parcel.weight_kg * 0.5 + parcel.content_value_usd * 0.01) * usd_rate

            # Обновить в БД
            update_query = (
                update(Parcel).where(Parcel.id == parcel.id).values(delivery_cost_rub=delivery_cost)
            )
            await session.execute(update_query)

            logger.info(f"Посылка ID={parcel.id}: рассчитана стоимость {delivery_cost:.2f} руб.")

        await session.commit()
        logger.info(f"Расчёт завершён. Обработано посылок: {len(parcels)}")
