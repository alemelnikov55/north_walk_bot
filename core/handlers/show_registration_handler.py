from aiogram.types import Message
from database.requests import RegistrationRequests


async def show_my_registrations(message: Message):
    """
    Обработчик для команды /my_walks

    Оправляет список актуальных записей для пользователя
    """
    user_id = message.from_user.id
    registrations = await RegistrationRequests.get_workouts_by_user_id(user_id)

    answer_msg = [f'{workout.date.strftime("%m.%d в %H:%M")} - {workout.type_name}' for workout in registrations]

    await message.answer('\n'.join(answer_msg))
