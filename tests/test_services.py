"""Тесты сервисного слоя (ParcelService) и репозитория (ParcelRepository).

Сервис инициализируется ParcelRepository (а не AsyncSession напрямую),
а метод create_parcel принимает (session_id, parcel_data: ParcelCreateSchemas).
"""

import pytest

from src.db.models import ParcelType
from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.schemas.parcel import ParcelCreateSchemas
from src.domain.services.parcel import ParcelService

pytestmark = pytest.mark.asyncio


async def test_get_parcel_types(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """get_parcel_types возвращает все типы посылок в виде схем."""
    result = await service.get_parcel_types()
    assert len(result) == 3
    names = {t.name for t in result}
    assert names == {"одежда", "электроника", "разное"}


async def test_create_parcel_returns_id(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """create_parcel создаёт посылку и возвращает её целочисленный ID."""
    parcel_data = ParcelCreateSchemas(
        name="Свитер",
        weight_kg=0.8,
        type_id=1,
        content_value_usd=50.0,
    )
    parcel_id = await service.create_parcel("session-abc", parcel_data)
    assert isinstance(parcel_id, int)
    assert parcel_id > 0


async def test_create_parcel_has_no_delivery_cost(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """Только что созданная посылка имеет delivery_cost_rub = None."""
    parcel_data = ParcelCreateSchemas(
        name="Часы",
        weight_kg=0.2,
        type_id=2,
        content_value_usd=200.0,
    )
    parcel_id = await service.create_parcel("session-watch", parcel_data)

    parcel = await service.get_parcel_by_id(parcel_id, "session-watch")
    assert parcel is not None
    assert parcel.delivery_cost_rub is None
    assert parcel.type_name == "электроника"


async def test_get_user_parcels(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """get_user_parcels возвращает посылки конкретной сессии."""
    session_id = "session-user-1"
    for name in ("Посылка 1", "Посылка 2"):
        await service.create_parcel(
            session_id,
            ParcelCreateSchemas(name=name, weight_kg=1.0, type_id=3, content_value_usd=10.0),
        )

    parcels = await service.get_user_parcels(session_id)
    assert len(parcels) == 2
    assert all(p.type_name == "разное" for p in parcels)


async def test_get_user_parcels_filter_by_type(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """get_user_parcels фильтрует посылки по type_id."""
    session_id = "session-filter"
    await service.create_parcel(
        session_id,
        ParcelCreateSchemas(name="Одежда", weight_kg=1.0, type_id=1, content_value_usd=10.0),
    )
    await service.create_parcel(
        session_id,
        ParcelCreateSchemas(name="Гаджет", weight_kg=1.0, type_id=2, content_value_usd=10.0),
    )

    only_clothes = await service.get_user_parcels(session_id, type_id=1)
    assert len(only_clothes) == 1
    assert only_clothes[0].type_id == 1


async def test_get_user_parcels_pagination(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """get_user_parcels поддерживает limit и offset."""
    session_id = "session-pages"
    for i in range(5):
        await service.create_parcel(
            session_id,
            ParcelCreateSchemas(name=f"P-{i}", weight_kg=1.0, type_id=3, content_value_usd=10.0),
        )

    page1 = await service.get_user_parcels(session_id, limit=2, offset=0)
    page2 = await service.get_user_parcels(session_id, limit=2, offset=2)
    page3 = await service.get_user_parcels(session_id, limit=2, offset=4)

    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1


async def test_get_parcel_by_id_not_found(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """get_parcel_by_id возвращает None для несуществующей посылки."""
    result = await service.get_parcel_by_id(123456, "any-session")
    assert result is None


async def test_get_parcel_by_id_wrong_session(
    service: ParcelService,
    parcel_types: list[ParcelType],
) -> None:
    """Посылка не возвращается, если запрашивает чужая сессия."""
    parcel_id = await service.create_parcel(
        "owner-session",
        ParcelCreateSchemas(name="Секрет", weight_kg=1.0, type_id=1, content_value_usd=10.0),
    )

    result = await service.get_parcel_by_id(parcel_id, "intruder-session")
    assert result is None


# --- Тесты репозитория напрямую ---


async def test_repository_create_and_fetch(
    repository: ParcelRepository,
    parcel_types: list[ParcelType],
) -> None:
    """ParcelRepository создаёт посылку и читает её по ID с подгрузкой типа."""
    created = await repository.create_parcel(
        session_id="repo-session",
        name="RepoTest",
        weight_kg=3.0,
        type_id=2,
        content_value_usd=99.0,
    )
    assert created.id is not None

    fetched = await repository.get_parcel_by_id(created.id, "repo-session")
    assert fetched is not None
    assert fetched.name == "RepoTest"
    # selectinload должен подгрузить связанный тип
    assert fetched.parcel_type.name == "электроника"


async def test_repository_get_all_parcel_types(
    repository: ParcelRepository,
    parcel_types: list[ParcelType],
) -> None:
    """ParcelRepository возвращает все типы посылок."""
    types = await repository.get_all_parcel_types()
    assert len(types) == 3


async def test_repository_filter_has_delivery_cost(
    repository: ParcelRepository,
    parcel_types: list[ParcelType],
) -> None:
    """Фильтр has_delivery_cost=False возвращает посылки без рассчитанной стоимости."""
    await repository.create_parcel(
        session_id="repo-filter",
        name="NoCost",
        weight_kg=1.0,
        type_id=1,
        content_value_usd=10.0,
    )

    pending = await repository.get_parcels_by_session(
        session_id="repo-filter",
        has_delivery_cost=False,
    )
    assert len(pending) == 1
    assert pending[0].delivery_cost_rub is None