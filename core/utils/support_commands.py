from aiogram import Bot
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.types.bot_command import BotCommand
from aiogram.types.bot_command_scope_all_chat_administrators import BotCommandScopeAllChatAdministrators
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
from aiogram.types.bot_command_scope_default import BotCommandScopeDefault

from core.loader import MainSettings


# async def set_commands(bot: Bot):
#     """Функция для установки команд бота"""
#     # Команды для участников
#     await bot.set_my_commands([
#         BotCommand(command='sign_up', description='Записаться на тренировку',
#                    scope=BotCommandScopeDefault()),
#         BotCommand(command='my_walks', description='Просмотреть список тренировок',
#                    scope=BotCommandScopeDefault()),
#         BotCommand(command='add_walk', description='Добавить тренировку',
#                    scope=BotCommandScopeChat(chat_id=MainSettings.SUPERUSER)),
#     ])

    # # Команды для администраторов
    # for user_id in MainSettings.ADMIN_LIST:
    #     print(user_id)
    #     await bot.set_my_commands([
    #         BotCommand(command='add_walk', description='Добавить тренировку',
    #                    scope=BotCommandScopeChat(chat_id=user_id)),
    #     ])


async def start_bot_sup_handler(bot: Bot) -> None:
    """Запуск бота """
    # await set_commands(bot)
    await bot.send_message(MainSettings.SUPERUSER, 'Бот запущен')


async def stop_bot_sup_handler(bot: Bot) -> None:
    """Остановка бота"""
    await bot.send_message(MainSettings.SUPERUSER, 'Бот остановлен')