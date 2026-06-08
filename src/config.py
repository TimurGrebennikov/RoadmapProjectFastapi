import os

from dotenv import load_dotenv

load_dotenv()

DATA_BASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/delivery")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USD_RATE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
