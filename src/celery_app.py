from celery import Celery

# Создание Celery приложения
celery_app = Celery(
    "delivery_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Настройка расписания Beat
celery_app.conf.beat_schedule = {
    "calculate-delivery-costs": {
        "task": "src.tasks.delivery_cost.calculate_delivery_costs",
        "schedule": 300.0,  # каждые 5 минут (в секундах)
    },
}

# Автоматический поиск задач
celery_app.autodiscover_tasks(["src.tasks"])
