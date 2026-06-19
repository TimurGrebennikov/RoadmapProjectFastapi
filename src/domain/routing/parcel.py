from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_session_id
from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.schemas.parcel import (
    ParcelCreateSchemas,
    ParcelResponseSchemas,
    ParcelTypeSchemas,
)
from src.domain.services.parcel import ParcelService

router = APIRouter(tags=["parcels"])


def get_parcel_service(db: AsyncSession = Depends(get_db)) -> ParcelService:  # noqa: B008
    """Dependency для создания ParcelService"""
    repo = ParcelRepository(db)
    return ParcelService(repo)


@router.get("/parcel-types", response_model=list[ParcelTypeSchemas])
async def get_parcel_types(
    service: ParcelService = Depends(get_parcel_service),  # noqa: B008
) -> list[ParcelTypeSchemas]:
    """Получить все типы посылок"""
    return await service.get_parcel_types()


@router.post("/parcels")
async def create_parcel(
    parcel_data: ParcelCreateSchemas,
    session_id: str = Depends(get_session_id),  # noqa: B008
    service: ParcelService = Depends(get_parcel_service),  # noqa: B008
) -> dict[str, int]:
    """Добавить посылку"""
    parcel_id = await service.create_parcel(session_id, parcel_data)
    return {"parcel_id": parcel_id}


@router.get("/parcels", response_model=list[ParcelResponseSchemas])
async def get_my_parcels(
    type_id: int | None = None,
    skip: int = 0,
    limit: int = 10,
    session_id: str = Depends(get_session_id),  # noqa: B008
    service: ParcelService = Depends(get_parcel_service),  # noqa: B008
) -> list[ParcelResponseSchemas]:  # ← ДОБАВЬ ЭТУ АННОТАЦИЮ!
    """Получить список своих посылок с фильтрацией и пагинацией"""
    return await service.get_user_parcels(
        session_id=session_id,
        type_id=type_id,
        offset=skip,
        limit=limit,
    )


@router.get("/parcels/{parcel_id}", response_model=ParcelResponseSchemas)
async def get_parcel(
    parcel_id: int,
    session_id: str = Depends(get_session_id),  # noqa: B008
    service: ParcelService = Depends(get_parcel_service),  # noqa: B008
) -> ParcelResponseSchemas:
    """Получить данные о посылке по ID"""
    parcel = await service.get_parcel_by_id(parcel_id, session_id)

    if not parcel:
        raise HTTPException(status_code=404, detail="Посылка не найдена")

    return parcel
