"""
Модуль определения подключения к БД Postre
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import docker

from loader import DBSettings

client_ = docker.from_env()

container = client_.containers.get('north_walk_db')
container_ip = container.attrs['NetworkSettings']['IPAddress']
print(container_ip)


# Создание двигателя и сессии для работы с БД
DATABASE_URL = f'postgresql+asyncpg://{DBSettings.POSTGRES_USER}:{DBSettings.POSTGRES_PASSWORD}@{container_ip}:5432/{DBSettings.DB_NAME}'

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
