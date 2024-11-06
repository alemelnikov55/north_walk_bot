from aiogram import Bot
from aiogram.types import Message, BotCommand, BotCommandScopeChat
from sqlalchemy.exc import IntegrityError

from loader import MainSettings
from database.requests import UserRequest


async def start_handler(message: Message, bot: Bot):
    user_id = message.from_user.id
    print(user_id)

    if not message.from_user.full_name:
        user_name = message.from_user.username
    else:
        user_name = message.from_user.full_name

    # Добавляем пользователя в БД и устанавливаем его команды
    try:
        await UserRequest.add_user(user_id, user_name)
    except IntegrityError as e:
        print(e)

    await set_menu_commands(user_id, MainSettings.ADMIN_LIST, bot)


async def set_menu_commands(user_id: int, admins: list, bot: Bot):
    if user_id in admins:
        # Команды для администраторов
        commands = [
            BotCommand(command='add_walk', description='Добавить тренировку'),
        ]
    else:
        # Команды для остальных пользователей
        commands = [
            BotCommand(command='sign_up', description='Записаться на тренировку'),
            BotCommand(command='my_walks', description='Просмотреть список тренировок'),
        ]

    # Установка команд
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))