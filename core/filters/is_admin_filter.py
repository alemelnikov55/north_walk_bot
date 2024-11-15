"""
Фильтры для определения ролей
"""
from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import Message

from loader import MainSettings


class IsAdmin(BaseFilter):
    """Проверка, является ли пользователь администратором."""
    def __init__(self, admins: List[int] = MainSettings.ADMIN_LIST):
        self.admins_ids = admins

    async def __call__(self, message: Message):
        if message.from_user.id in self.admins_ids or message.from_user.id == MainSettings.SUPERUSER:
            return True
        return False
