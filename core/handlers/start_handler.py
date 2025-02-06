"""
Обработчик команды /start - регистрация пользователя в БД
"""
from aiogram import Bot
from aiogram.types import Message, BotCommand, BotCommandScopeChat
from sqlalchemy.exc import InvalidRequestError

from loader import MainSettings
from database.requests import UserRequest


async def start_handler(message: Message, bot: Bot):
    """
    Обработчик команды /start - регистрация пользователя в БД

    :param message:
    :param bot:
    :return:
    """
    user_id = message.from_user.id
    print(user_id)

    if not message.from_user.full_name:
        user_name = message.from_user.username
    else:
        user_name = message.from_user.full_name

    # Добавляем пользователя в БД и устанавливаем его команды
    try:
        await UserRequest.add_user(user_id, user_name)
    except InvalidRequestError as e:
        print(e)

    await set_menu_commands(user_id, MainSettings.ADMIN_LIST, bot)
    await message.answer(f'Привет, {user_name}! Рады приветствовать тебя в рядах ходоков!\n'
                         f'Это бот для записи на тренировки по Скандинавской ходьбе.'
                         f'Чтобы посмотреть доступные используй команду /sign_up\n'
                         f'Чтобы посмотреть свои записи на тренировки - /my_walks')


async def set_menu_commands(user_id: int, admins: list, bot: Bot):
    """
    Установка меню в зависимости от роли пользователя

    :param user_id:
    :param admins:
    :param bot:
    :return:
    """
    if user_id in admins:
        # Команды для администраторов
        commands = [
            BotCommand(command='add_walk', description='Добавить тренировку'),
            BotCommand(command='show_walk', description='Показывает запланированные тренировки'),
            BotCommand(command='check_walks', description='Проверка посещаемости')
        ]
    else:
        # Команды для остальных пользователей
        commands = [
            BotCommand(command='sign_up', description='Записаться на тренировку'),
            BotCommand(command='my_walks', description='Просмотреть список тренировок'),
        ]

    # Установка команд
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
