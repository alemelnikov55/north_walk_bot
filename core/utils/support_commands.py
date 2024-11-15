"""
Вспомогательные команды для оповещения администратора и страта бота
"""
from aiogram import Bot

from loader import MainSettings
from database.requests import StartServiceRequest


async def start_bot_sup_handler(bot: Bot) -> None:
    """Запуск бота

    Отправляет сообщение админимтратору и запускает процесс создания и проверки БД
    """
    await StartServiceRequest.create_and_fill_db()
    await bot.send_message(MainSettings.SUPERUSER, 'Бот запущен')


async def stop_bot_sup_handler(bot: Bot) -> None:
    """Остановка бота"""
    await bot.send_message(MainSettings.SUPERUSER, 'Бот остановлен')
