# 🚚 Сервис международной доставки

Микросервис для регистрации посылок и автоматического расчёта стоимости доставки в рублях на основе актуального курса USD.

## 📋 Описание

Сервис позволяет:
- Регистрировать посылки с указанием веса, типа и стоимости содержимого
- Автоматически рассчитывать стоимость доставки в рублях каждые 5 минут
- Получать список своих посылок с фильтрацией и пагинацией
- Отслеживать пользователей по сессиям (без авторизации)

Курс доллара берется из официального API ЦБ РФ и кэшируется в Redis.

---

## 🛠️ Технологический стек

- **Backend**: FastAPI (Python 3.12)
- **База данных**: PostgreSQL 15 (async SQLAlchemy + asyncpg)
- **Кэш/Брокер**: Redis 7
- **Фоновые задачи**: Celery + Celery Beat
- **Валидация**: Pydantic
- **Миграции**: Alembic
- **Контейнеризация**: Docker + Docker Compose
- **Code Quality**: Ruff, Mypy, Bandit

---

## 🚀 Быстрый старт

### Требования

- Docker и Docker Compose
- Git

### 1️⃣ Клонирование репозитория


git clone https://github.com/TimurGrebennikov/RoadmapProjectFastapi.git
cd RoadmapProjectFastapi
2️⃣ Запуск проекта
bash
Copy
docker-compose up -d
Что произойдет:

Поднимутся 5 контейнеров (app, db, redis, celery-worker, celery-beat)
Автоматически применятся миграции базы данных
Запустится FastAPI приложение на порту 8000
3️⃣ Проверка работы
Swagger документация доступна по адресу:

👉 http://localhost:8000/docs

📡 API Endpoints
1. Регистрация посылки
http
Copy
POST /parcels
Content-Type: application/json
Тело запроса:

JSON
Copy
{
  "name": "Посылка с одеждой",
  "type_id": 1,
  "weight_kg": 2.5,
  "content_value_usd": 150,
  "user_session_id": "my-session-123"
}
Ответ:

json
Copy
{
  "parcel_id": 1
}
Валидация:

name: не пустое
weight_kg: > 0
content_value_usd: >= 0
type_id: существующий тип посылки (1, 2 или 3)
1. Получить типы посылок
http
Copy
GET /parcel-types
Ответ:

json
Copy
[
  {"id": 1, "name": "одежда"},
  {"id": 2, "name": "электроника"},
  {"id": 3, "name": "разное"}
]
1. Список посылок пользователя
http
Copy
GET /parcels?user_session_id=my-session-123&type_id=1&has_cost=true&limit=10&offset=0
Query параметры:

user_session_id (обязательный): ID сессии пользователя
type_id (опционально): фильтр по типу посылки
has_cost (опционально): true — только с рассчитанной стоимостью, false — только без стоимости
limit (опционально): количество записей (по умолчанию 10)
offset (опционально): смещение для пагинации (по умолчанию 0)
Ответ:

JSON
Copy
[
  {
    "id": 1,
    "name": "Посылка с одеждой",
    "type_name": "одежда",
    "weight_kg": 2.5,
    "content_value_usd": 150.0,
    "delivery_cost_rub": 201.96,
    "user_session_id": "my-session-123",
    "created_at": "2026-06-19T15:30:00"
  }
]
1. Детали посылки по ID
http
Copy
GET /parcels/1
Ответ:

json
Copy
{
  "id": 1,
  "name": "Посылка с одеждой",
  "type_name": "одежда",
  "weight_kg": 2.5,
  "content_value_usd": 150.0,
  "delivery_cost_rub": 201.96,
  "user_session_id": "my-session-123",
  "created_at": "2026-06-19T15:30:00"
}
Если стоимость доставки ещё не рассчитана:

json
Copy
{
  "delivery_cost_rub": null
}
⏰ Периодические задачи
Автоматический расчёт стоимости доставки
Частота: каждые 5 минут

Что делает:

Получает курс USD из API ЦБ РФ (https://www.cbr-xml-daily.ru/daily_json.js)
Кэширует курс в Redis на 5 минут
Находит все посылки без рассчитанной стоимости
Рассчитывает стоимость по формуле:
Стоимость = (вес_кг * 0.5 + стоимость_usd * 0.01) * курс_usd
Сохраняет результат в базу данных
Запуск задачи вручную (для отладки)
bash
Copy
docker exec roadmapprojectfastapi-celery-worker-1 celery -A src.celery_app call src.tasks.delivery_cost.calculate_delivery_costs
📂 Структура проекта
RoadmapProjectFastapi/
├── src/
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Конфигурация приложения
│   ├── database.py             # Настройка БД (async engine, session)
│   ├── celery_app.py           # Конфигурация Celery
│   │
│   ├── db/
│   │   └── models.py           # SQLAlchemy модели (Parcel, ParcelType)
│   │
│   ├── domain/
│   │   ├── schemas/
│   │   │   └── parcel.py       # Pydantic схемы для валидации
│   │   │
│   │   ├── repositories/
│   │   │   └── parcel_repository.py  # Слой работы с БД
│   │   │
│   │   ├── services/
│   │   │   ├── parcel.py       # Бизнес-логика посылок
│   │   │   └── currency.py     # Сервис получения курса USD
│   │   │
│   │   └── routing/
│   │       └── parcel.py       # API роуты
│   │
│   └── tasks/
│       ├── __init__.py
│       └── delivery_cost.py    # Celery задача расчёта стоимости
│
├── alembic/                    # Миграции базы данных
├── docker-compose.yml          # Конфигурация Docker Compose
├── Dockerfile                  # Образ приложения
├── entrypoint.sh               # Скрипт автозапуска миграций
├── pyproject.toml              # Зависимости (Poetry)
└── README.md                   # Документация
🐳 Docker сервисы
┌─────────────┬──────────────┬────────────────────┐
│   Сервис    │     Порт     │     Назначение     │
├─────────────┼──────────────┼────────────────────┤
│ app         │ 8000         │ FastAPI приложение │
│ db          │ 5432         │ PostgreSQL         │
│ redis       │ 6379         │ Кэш + брокер       │
│ celery-worker│ -           │ Выполнение задач   │
│ celery-beat │ -            │ Планировщик задач  │
└─────────────┴──────────────┴────────────────────┘
🔧 Полезные команды
Просмотр логов
bash
Copy
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker logs roadmapprojectfastapi-app-1 -f
docker logs roadmapprojectfastapi-celery-worker-1 -f
docker logs roadmapprojectfastapi-celery-beat-1 -f
Перезапуск сервисов
bash
Copy
# Все сервисы
docker-compose restart

# Конкретный сервис
docker-compose restart app
docker-compose restart celery-worker
Остановка проекта
bash
Copy
docker-compose down
Полная очистка (удаление данных БД)
bash
Copy
docker-compose down -v
Применение новых миграций
bash
Copy
# Создание новой миграции
docker exec roadmapprojectfastapi-app-1 poetry run alembic revision --autogenerate -m "description"

# Применение миграций (происходит автоматически при запуске)
docker exec roadmapprojectfastapi-app-1 poetry run alembic upgrade head
Запуск линтеров и форматтеров
bash
Copy
# Проверка качества кода
docker exec roadmapprojectfastapi-app-1 poetry run ruff check src

# Автофикс проблем
docker exec roadmapprojectfastapi-app-1 poetry run ruff check src --fix

# Форматирование кода
docker exec roadmapprojectfastapi-app-1 poetry run ruff format src

# Проверка типов
docker exec roadmapprojectfastapi-app-1 poetry run mypy src
🧪 Тестирование
Пример использования API
bash
Copy
# 1. Создать посылку
curl -X POST "http://localhost:8000/parcels" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовая посылка",
    "type_id": 1,
    "weight_kg": 3.0,
    "content_value_usd": 200,
    "user_session_id": "test-session"
  }'

# 2. Получить типы посылок
curl "http://localhost:8000/parcel-types"

# 3. Получить список своих посылок
curl "http://localhost:8000/parcels?user_session_id=test-session"

# 4. Получить детали посылки
curl "http://localhost:8000/parcels/1"

# 5. Запустить расчёт стоимости вручную
docker exec roadmapprojectfastapi-celery-worker-1 celery -A src.celery_app call src.tasks.delivery_cost.calculate_delivery_costs

# 6. Проверить что стоимость рассчиталась
curl "http://localhost:8000/parcels/1"
📊 Архитектура
Проект построен по принципу многослойной архитектуры:

┌─────────────┐
│   Router    │  ← HTTP endpoints (FastAPI)
└──────┬──────┘
       │
┌──────▼──────┐
│   Service   │  ← Бизнес-логика
└──────┬──────┘
       │
┌──────▼──────┐
│ Repository  │  ← Работа с БД
└──────┬──────┘
       │
┌──────▼──────┐
│   Models    │  ← SQLAlchemy модели
└─────────────┘
Преимущества:

Разделение ответственности
Легкое тестирование
Возможность замены БД без изменения бизнес-логики
🔐 Особенности реализации
Отслеживание пользователей
Приложение НЕ содержит авторизации. Пользователи отслеживаются по user_session_id (строка).

Асинхронность
Все операции с БД и внешними API выполняются асинхронно (async/await).

Кэширование
Курс USD кэшируется в Redis на 5 минут, чтобы не нагружать API ЦБ РФ.

Валидация
Все входные данные валидируются через Pydantic схемы с понятными сообщениями об ошибках.

👨‍💻 Автор
Тимур Гребенников

GitHub: TimurGrebennikov
```bash