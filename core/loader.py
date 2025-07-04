"""
Модуль констант для работы бота
"""
import dataclasses
import os

from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit('Файл .env не найден. Переменные не загружены')
else:
    load_dotenv()


@dataclasses.dataclass
class MainSettings:
    TOKEN = os.getenv('TOKEN')
    SUPERUSER = int(os.getenv('SUPERUSER'))
    ADMIN_LIST = [int(x) for x in os.getenv('ADMIN_LIST').split(' ')]


class DBSettings:
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')


class RedisSettings:
    REDIS_HOST = os.getenv('REDIS_DB_URL')
