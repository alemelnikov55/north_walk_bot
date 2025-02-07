"""
Модуль объявления функций для лучшей читаемости кода
"""
from database.requests import RegistrationRequests


async def get_formatted_list_of_users_by_workout_id(workout_id) -> str:
    """
    Получение форматированного списка записавшихся на тренировку

    по id тренировки получает пользователей и создает текст для вставки в сообщение
    :param workout_id: id тренировки
    :return: str
    """
    users_in_workout = await RegistrationRequests.get_workout_users(workout_id)
    walkers = enumerate([walker[0] for walker in users_in_workout], 1)  # Список участников тренировки
    listed_walkers = "\n".join([f'{list_info[0]}. {list_info[1]}' for list_info in walkers])
    return listed_walkers
