from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.schemas.parcel import (
    ParcelCreateSchemas,
    ParcelResponseSchemas,
    ParcelTypeSchemas,
)


class ParcelService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ParcelRepository(session)

    async def get_all_types(self) -> list[ParcelTypeSchemas]:
        """Получить все типы посылок"""
        types = await self.repo.get_all_parcel_types()

        return [
            ParcelTypeSchemas(id=t.id, name=t.name)  # type: ignore[arg-type]
            for t in types
        ]

    async def create_parcel(self, session_id: str, data: ParcelCreateSchemas) -> int:
        """Создать новую посылку"""
        parcel = await self.repo.create_parcel(
            session_id=session_id,
            name=data.name,
            weight_kg=data.weight_kg,
            type_id=data.type_id,
            content_value_usd=data.content_value_usd,
        )
        return parcel.id  # type: ignore[return-value]

    async def get_user_parcels(
        self,
        session_id: str,
        type_id: int | None = None,
        has_delivery_cost: bool | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> list[ParcelResponseSchemas]:
        """Получить все посылки пользователя"""
        parcels = await self.repo.get_parcels_by_session(
            session_id=session_id,
            type_id=type_id,
            has_delivery_cost=has_delivery_cost,
            skip=skip,
            limit=limit,
        )

        return [
            ParcelResponseSchemas(  # type: ignore[arg-type]
                id=p.id,  # type: ignore[arg-type]
                name=p.name,  # type: ignore[arg-type]
                weight_kg=p.weight_kg,  # type: ignore[arg-type]
                type_id=p.type_id,  # type: ignore[arg-type]
                type_name=p.type.name,
                content_value_usd=p.content_value_usd,  # type: ignore[arg-type]
                delivery_cost_rub=p.delivery_cost_rub,  # type: ignore[arg-type]
            )
            for p in parcels
        ]

    async def get_parcel_details(
        self, parcel_id: int, session_id: str
    ) -> ParcelResponseSchemas | None:
        """Получить одну посылку по ID"""
        parcel = await self.repo.get_parcel_by_id(parcel_id, session_id)

        if not parcel:
            return None

        return ParcelResponseSchemas(  # type: ignore[arg-type]
            id=parcel.id,  # type: ignore[arg-type]
            name=parcel.name,  # type: ignore[arg-type]
            weight_kg=parcel.weight_kg,  # type: ignore[arg-type]
            type_id=parcel.type_id,  # type: ignore[arg-type]
            type_name=parcel.type.name,
            content_value_usd=parcel.content_value_usd,  # type: ignore[arg-type]
            delivery_cost_rub=parcel.delivery_cost_rub,  # type: ignore[arg-type]
        )
