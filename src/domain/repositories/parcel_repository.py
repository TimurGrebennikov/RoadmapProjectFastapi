from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # ← ДОБАВЬ ЭТОТ ИМПОРТ!

from src.db.models import Parcel, ParcelType


class ParcelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_parcel_types(self) -> list[ParcelType]:
        """Получить все типы посылок"""
        query = select(ParcelType)
        result = await self.session.execute(query)
        types = result.scalars().all()
        return list(types)

    async def create_parcel(
        self,
        session_id: str,
        name: str,
        weight_kg: float,
        type_id: int,
        content_value_usd: float,
    ) -> Parcel:
        """Создать новую посылку"""
        new_parcel = Parcel(
            user_session_id=session_id,
            name=name,
            weight_kg=weight_kg,
            type_id=type_id,
            content_value_usd=content_value_usd,
            delivery_cost_rub=None,
        )

        self.session.add(new_parcel)
        await self.session.commit()
        await self.session.refresh(new_parcel)
        return new_parcel

    async def get_parcels_by_session(
        self,
        session_id: str,
        type_id: int | None = None,
        has_delivery_cost: bool | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Parcel]:
        """Получить посылки пользователя с фильтрами"""
        query = (
            select(Parcel)
            .options(selectinload(Parcel.parcel_type))
            .where(Parcel.user_session_id == session_id)
        )

        if type_id is not None:
            query = query.where(Parcel.type_id == type_id)

        if has_delivery_cost is not None:
            if has_delivery_cost:
                query = query.where(Parcel.delivery_cost_rub.is_not(None))
            else:
                query = query.where(Parcel.delivery_cost_rub.is_(None))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_parcel_by_id(self, parcel_id: int, session_id: str) -> Parcel | None:
        """Получить посылку по ID"""
        query = (
            select(Parcel)
            .options(selectinload(Parcel.parcel_type))
            .where(
                Parcel.id == parcel_id,
                Parcel.user_session_id == session_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
