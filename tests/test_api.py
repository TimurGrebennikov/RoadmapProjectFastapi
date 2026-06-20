"""Тесты API-эндпоинтов (через httpx AsyncClient + ASGITransport)."""

from httpx import AsyncClient
import pytest

pytestmark = pytest.mark.asyncio


async def test_root(client: AsyncClient) -> None:
    """GET / возвращает информацию о сервисе."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert "message" in data


async def test_health_check(client: AsyncClient) -> None:
    """GET /health возвращает статус healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_get_parcel_types(client: AsyncClient) -> None:
    """GET /parcel-types возвращает заполненные типы посылок."""
    response = await client.get("/parcel-types")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    names = {item["name"] for item in data}
    assert names == {"одежда", "электроника", "разное"}


async def test_create_parcel(client: AsyncClient) -> None:
    """POST /parcels создаёт посылку и возвращает её ID."""
    payload = {
        "name": "Ноутбук",
        "weight_kg": 2.5,
        "type_id": 2,
        "content_value_usd": 1000.0,
    }
    response = await client.post("/parcels", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "parcel_id" in data
    assert isinstance(data["parcel_id"], int)


async def test_create_parcel_sets_session_cookie(client: AsyncClient) -> None:
    """POST /parcels устанавливает cookie session_id для нового пользователя."""
    payload = {
        "name": "Футболка",
        "weight_kg": 0.3,
        "type_id": 1,
        "content_value_usd": 20.0,
    }
    response = await client.post("/parcels", json=payload)
    assert response.status_code == 200
    assert "session_id" in response.cookies


async def test_create_parcel_validation_error(client: AsyncClient) -> None:
    """POST /parcels с некорректным весом возвращает 422."""
    payload = {
        "name": "Бракованная",
        "weight_kg": -1.0,  # нарушает gt=0
        "type_id": 1,
        "content_value_usd": 10.0,
    }
    response = await client.post("/parcels", json=payload)
    assert response.status_code == 422


async def test_get_my_parcels_empty(client: AsyncClient) -> None:
    """GET /parcels для новой сессии возвращает пустой список."""
    response = await client.get("/parcels")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_and_list_parcels(client: AsyncClient) -> None:
    """Созданная посылка появляется в списке посылок той же сессии."""
    payload = {
        "name": "Телефон",
        "weight_kg": 0.5,
        "type_id": 2,
        "content_value_usd": 500.0,
    }
    create_resp = await client.post("/parcels", json=payload)
    assert create_resp.status_code == 200

    list_resp = await client.get("/parcels")
    assert list_resp.status_code == 200

    parcels = list_resp.json()
    assert len(parcels) == 1
    assert parcels[0]["name"] == "Телефон"
    assert parcels[0]["type_name"] == "электроника"
    assert parcels[0]["delivery_cost_rub"] is None


async def test_get_parcel_by_id(client: AsyncClient) -> None:
    """GET /parcels/{id} возвращает конкретную посылку."""
    payload = {
        "name": "Книга",
        "weight_kg": 1.0,
        "type_id": 3,
        "content_value_usd": 30.0,
    }
    create_resp = await client.post("/parcels", json=payload)
    parcel_id = create_resp.json()["parcel_id"]

    response = await client.get(f"/parcels/{parcel_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == parcel_id
    assert data["name"] == "Книга"
    assert data["type_name"] == "разное"


async def test_get_parcel_not_found(client: AsyncClient) -> None:
    """GET /parcels/{id} для несуществующей посылки возвращает 404."""
    response = await client.get("/parcels/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Посылка не найдена"


async def test_parcels_filter_by_type(client: AsyncClient) -> None:
    """GET /parcels?type_id=... фильтрует посылки по типу."""
    await client.post(
        "/parcels",
        json={"name": "Куртка", "weight_kg": 1.2, "type_id": 1, "content_value_usd": 80.0},
    )
    await client.post(
        "/parcels",
        json={"name": "Планшет", "weight_kg": 0.7, "type_id": 2, "content_value_usd": 300.0},
    )

    response = await client.get("/parcels", params={"type_id": 1})
    assert response.status_code == 200

    parcels = response.json()
    assert len(parcels) == 1
    assert parcels[0]["type_id"] == 1


async def test_parcels_pagination(client: AsyncClient) -> None:
    """GET /parcels?limit=...&skip=... поддерживает пагинацию."""
    for i in range(3):
        await client.post(
            "/parcels",
            json={
                "name": f"Посылка-{i}",
                "weight_kg": 1.0,
                "type_id": 3,
                "content_value_usd": 10.0,
            },
        )

    response = await client.get("/parcels", params={"limit": 2, "skip": 0})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response_page2 = await client.get("/parcels", params={"limit": 2, "skip": 2})
    assert response_page2.status_code == 200
    assert len(response_page2.json()) == 1


async def test_parcels_isolated_by_session(client: AsyncClient) -> None:
    """Посылки одной сессии не видны другой сессии."""
    # Первая сессия создаёт посылку (cookie сохранится в client)
    await client.post(
        "/parcels",
        json={"name": "Личная", "weight_kg": 1.0, "type_id": 1, "content_value_usd": 10.0},
    )

    # Имитируем другую сессию: запрос с собственным session_id cookie
    response = await client.get("/parcels", cookies={"session_id": "other-session"})
    assert response.status_code == 200
    assert response.json() == []
