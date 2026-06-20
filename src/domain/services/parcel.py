from src.db.models import ParcelType
from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.schemas.parcel import ParcelCreateSchemas, ParcelResponseSchemas, ParcelTypeSchemas
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ParcelService:
    def __init__(self, repo: ParcelRepository) -> None:
        self.repo = repo

    async def get_parcel_types(self) -> list[ParcelTypeSchemas]:
        """Получить все типы посылок"""
        logger.info("Запрос всех типов посылок")
        types: list[ParcelType] = await self.repo.get_all_parcel_types()
        logger.info("Получено типов посылок: %d", len(types))
        return [ParcelTypeSchemas(id=t.id, name=t.name) for t in types]  # type: ignore[arg-type]

    async def create_parcel(self, session_id: str, parcel_data: ParcelCreateSchemas) -> int:
        """Создать новую посылку"""
        logger.info(
            "Создание посылки: name=%s, weight_kg=%s, type_id=%s, session_id=%s",
            parcel_data.name,
            parcel_data.weight_kg,
            parcel_data.type_id,
            session_id,
        )
        parcel = await self.repo.create_parcel(
            session_id=session_id,
            name=parcel_data.name,  # type: ignore[arg-type]
            weight_kg=parcel_data.weight_kg,  # type: ignore[arg-type]
            type_id=parcel_data.type_id,  # type: ignore[arg-type]
            content_value_usd=parcel_data.content_value_usd,  # type: ignore[arg-type]
        )
        logger.info("Посылка создана с ID=%s", parcel.id)
        return parcel.id  # type: ignore[return-value]

    async def get_user_parcels(
        self,
        session_id: str,
        type_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ParcelResponseSchemas]:
        """Получить посылки пользователя"""
        logger.info(
            "Запрос посылок пользователя: session_id=%s, type_id=%s, limit=%s, offset=%s",
            session_id,
            type_id,
            limit,
            offset,
        )
        parcels = await self.repo.get_parcels_by_session(
            session_id=session_id,
            type_id=type_id,
            skip=offset,  # offset -> skip
            limit=limit,
        )
        logger.info("Найдено посылок: %d", len(parcels))

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
        logger.info("Запрос посылки по ID=%s, session_id=%s", parcel_id, session_id)
        parcel = await self.repo.get_parcel_by_id(parcel_id, session_id)

        if not parcel:
            logger.warning("Посылка ID=%s не найдена для session_id=%s", parcel_id, session_id)
            return None

        logger.info("Посылка ID=%s успешно получена", parcel_id)
        return ParcelResponseSchemas(
            id=parcel.id,  # type: ignore[arg-type]
            name=parcel.name,  # type: ignore[arg-type]
            weight_kg=parcel.weight_kg,  # type: ignore[arg-type]
            type_id=parcel.type_id,  # type: ignore[arg-type]
            type_name=parcel.parcel_type.name,  # type: ignore[arg-type]
            content_value_usd=parcel.content_value_usd,  # type: ignore[arg-type]
            delivery_cost_rub=parcel.delivery_cost_rub,  # type: ignore[arg-type]
        )
