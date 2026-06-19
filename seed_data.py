import asyncio

from sqlalchemy import select

from src.database import async_session_maker
from src.db.models import ParcelType


async def seed_parcel_types():
    """Добавить типы посылок в БД"""
    async with async_session_maker() as session:
        # Проверяем, есть ли уже типы
        result = await session.execute(select(ParcelType))
        existing = result.scalars().all()

        if existing:
            print("✅ Типы посылок уже существуют:")
            for pt in existing:
                print(f"   - {pt.id}: {pt.name}")
            return

        # Добавляем типы
        types = [
            ParcelType(name="одежда"),
            ParcelType(name="электроника"),
            ParcelType(name="разное"),
        ]

        session.add_all(types)
        await session.commit()
        print("✅ Типы посылок добавлены:")
        print("   - 1: одежда")
        print("   - 2: электроника")
        print("   - 3: разное")


if __name__ == "__main__":
    asyncio.run(seed_parcel_types())