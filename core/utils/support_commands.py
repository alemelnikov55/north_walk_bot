from aiogram import Bot

from core.loader import MainSettings


async def start_bot_sup_handler(bot: Bot) -> None:
    """Запуск бота """
    # await set_commands(bot)
    await bot.send_message(MainSettings.SUPERUSER, 'Бот запущен')


async def stop_bot_sup_handler(bot: Bot) -> None:
    """Остановка бота"""
    await bot.send_message(MainSettings.SUPERUSER, 'Бот остановлен')