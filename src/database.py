from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.config import DATA_BASE_URL

engine = create_async_engine(DATA_BASE_URL)
# echo=True
async_sessionmaker = sessionmaker(engine,class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass