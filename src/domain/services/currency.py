import logging

import httpx
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self) -> None:
        self.redis_url = "redis://redis:6379/0"
        self.api_url = "https://www.cbr-xml-daily.ru/daily_json.js"

    async def get_usd_rate(self) -> float:
        """Получить курс USD с кэшированием в Redis"""
        redis_client = redis.from_url(self.redis_url, decode_responses=True)

        try:
            # Проверяем кэш
            cached_rate = await redis_client.get("usd_rate")
            if cached_rate:
                rate_value = float(cached_rate)
                logger.info(f"Получен курс USD из кэша: {rate_value}")
                return rate_value

            # Запрашиваем из API ЦБ РФ
            logger.info("Кэш пуст, запрашиваем курс USD из API ЦБ РФ...")
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                usd_rate = data["Valute"]["USD"]["Value"]

            logger.info(f"Получен курс USD из API ЦБ РФ: {usd_rate}")

            # Сохраняем в кэш на 5 минут
            await redis_client.setex("usd_rate", 300, str(usd_rate))
            logger.info("Курс USD сохранён в кэш на 5 минут")

            return float(usd_rate)

        except httpx.HTTPError as e:
            logger.error(f"Ошибка HTTP при получении курса USD: {e}")
            raise

        except KeyError as e:
            logger.error(f"Ошибка парсинга ответа API ЦБ РФ: {e}")
            raise

        except redis.RedisError as e:
            logger.error(f"Ошибка Redis: {e}")
            raise

        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении курса USD: {e}")
            raise

        finally:
            await redis_client.aclose()
