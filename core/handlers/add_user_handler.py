from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.states import UserAddState
from database.requests import UserRequest


async def add_user_handler_starter(message: Message, state: FSMContext):
    """
    Обработчик команды /register
    """
    await state.set_state(UserAddState.ASK_USERNAME)
    await message.answer("Введи свое Имя Фамилию, чтобы мы знали как к тебе обращаться")


async def add_user_handler_process(message: Message, state: FSMContext):
    """
    Добавдение юзера в БД
    """
    username = message.text
    user_id = message.from_user.id
    replay = await UserRequest.add_user(user_id, username)
    await state.clear()
    await message.answer(f'Вы зарегистрированы под именем: {replay.name}')
