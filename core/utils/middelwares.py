"""
Модуль для передачи scheduler в обработчики
"""
import dataclasses
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler



@dataclasses.dataclass
class ApschedulerMiddleware(BaseMiddleware):
    """
    middelware для Добавления в сообщение scheduler
    """
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        data['scheduler'] = self.scheduler
        return await handler(event, data)
        # Если в хэндлере сделать return, то это значение попадёт в result