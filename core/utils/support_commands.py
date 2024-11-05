from aiogram import Bot
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.types.bot_command import BotCommand

from core.loader import MainSettings



async def set_commands(bot: Bot):
    """Функция для установки команд бота"""
    await bot.set_my_commands([
        # BotCommand(command='get_pptx', description='Скачать презентацию',
        #            scope=BotCommandScopeChat(chat_id=MainSettings.SUPERUSER)),
        # BotCommand(command='clear_files', description='Очистить локальные файлы',
        #            scope=BotCommandScopeChat(chat_id=MainSettings.SUPERUSER))
    ])


async def start_bot_sup_handler(bot: Bot) -> None:
    """Запуск бота """
    await set_commands(bot)
    await bot.send_message(MainSettings.SUPERUSER, 'Бот запущен')


async def stop_bot_sup_handler(bot: Bot) -> None:
    """Остановка бота"""
    await bot.send_message(MainSettings.SUPERUSER, 'Бот остановлен')