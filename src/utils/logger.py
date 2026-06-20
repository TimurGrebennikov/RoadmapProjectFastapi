"""Централизованная настройка логирования для приложения.

Использование:
    from src.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Сообщение")
"""

import logging
import sys

# Формат вывода логов: время | уровень | имя логгера | сообщение
_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Флаг, чтобы не настраивать корневой логгер повторно
_is_configured = False


def setup_logging(level: int = logging.INFO) -> None:
    """Настроить корневой логгер один раз за время жизни процесса.

    Args:
        level: Минимальный уровень логирования (по умолчанию INFO).
    """
    global _is_configured
    if _is_configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_DEFAULT_FORMAT, datefmt=_DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Добавляем обработчик только если его ещё нет (избегаем дублирования логов)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    _is_configured = True


def get_logger(name: str) -> logging.Logger:
    """Получить именованный логгер с гарантированной настройкой.

    Args:
        name: Имя логгера, обычно ``__name__`` вызывающего модуля.

    Returns:
        Настроенный экземпляр :class:`logging.Logger`.
    """
    setup_logging()
    return logging.getLogger(name)
