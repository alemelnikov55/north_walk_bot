"""
Модуль определения подключения к БД Postre
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from loader import DBSettings

# Создание двигателя и сессии для работы с БД
DATABASE_URL = f'postgresql+asyncpg://{DBSettings.POSTGRES_USER}:{DBSettings.POSTGRES_PASSWORD}@172.17.0.2:5432/{DBSettings.DB_NAME}'

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

