from src.db.models import ParcelType
from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.schemas.parcel import ParcelCreateSchemas, ParcelResponseSchemas, ParcelTypeSchemas


class ParcelService:
    def __init__(self, repo: ParcelRepository) -> None:
        self.repo = repo

    async def get_parcel_types(self) -> list[ParcelTypeSchemas]:
        """Получить все типы посылок"""
        types: list[ParcelType] = await self.repo.get_all_parcel_types()
        return [ParcelTypeSchemas(id=t.id, name=t.name) for t in types]  # type: ignore[arg-type]

    async def create_parcel(self, session_id: str, parcel_data: ParcelCreateSchemas) -> int:
        """Создать новую посылку"""
        parcel = await self.repo.create_parcel(
            session_id=session_id,
            name=parcel_data.name,  # type: ignore[arg-type]
            weight_kg=parcel_data.weight_kg,  # type: ignore[arg-type]
            type_id=parcel_data.type_id,  # type: ignore[arg-type]
            content_value_usd=parcel_data.content_value_usd,  # type: ignore[arg-type]
        )
        return parcel.id  # type: ignore[return-value]

    async def get_user_parcels(
        self,
        session_id: str,
        type_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ParcelResponseSchemas]:
        """Получить посылки пользователя"""
        parcels = await self.repo.get_parcels_by_session(
            session_id=session_id,
            type_id=type_id,
            skip=offset,  # offset -> skip
            limit=limit,
        )

        return [
            ParcelResponseSchemas(
                id=p.id,  # type: ignore[arg-type]
                name=p.name,  # type: ignore[arg-type]
                weight_kg=p.weight_kg,  # type: ignore[arg-type]
                type_id=p.type_id,  # type: ignore[arg-type]
                type_name=p.parcel_type.name,  # type: ignore[arg-type]
                content_value_usd=p.content_value_usd,  # type: ignore[arg-type]
                delivery_cost_rub=p.delivery_cost_rub,  # type: ignore[arg-type]
            )
            for p in parcels
        ]

    async def get_parcel_by_id(
        self, parcel_id: int, session_id: str
    ) -> ParcelResponseSchemas | None:
        """Получить посылку по ID"""
        parcel = await self.repo.get_parcel_by_id(parcel_id, session_id)

        if not parcel:
            return None

        return ParcelResponseSchemas(
            id=parcel.id,  # type: ignore[arg-type]
            name=parcel.name,  # type: ignore[arg-type]
            weight_kg=parcel.weight_kg,  # type: ignore[arg-type]
            type_id=parcel.type_id,  # type: ignore[arg-type]
            type_name=parcel.parcel_type.name,  # type: ignore[arg-type]
            content_value_usd=parcel.content_value_usd,  # type: ignore[arg-type]
            delivery_cost_rub=parcel.delivery_cost_rub,  # type: ignore[arg-type]
        )
