"""
Модуль для управления существующими тренировками
"""
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import RegistrationRequests, WorkoutsRequests


async def show_walks_handler(message: Message):
    """
    Обработчик команды /show_walk

    Выводи список доступных тренировок администратору с кнопокй для удаления тренировок
    """
    await message.answer('Нажмите на чтобы увидеть подробности или удалить ее', reply_markup=await all_workouts_info_kb())


async def all_workouts_info_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура с информацией о всех доступных тренировках
    """
    show_workouts_kb_builder = InlineKeyboardBuilder()

    available_walks = await RegistrationRequests.get_all_available_workouts()
    count_walkers_on_registration = await RegistrationRequests.count_signs_for_workouts()
    pair_id_count = {str(pair[0]): pair[1] for pair in count_walkers_on_registration}

    if available_walks:
        for workout, type_ in available_walks:
            date = workout.date.strftime('%d.%m | %H:%M').replace('08:30', '08:30☀').replace('20:30', '20:30🌓')
            workout_type = type_.type_name
            workout_id = str(workout.workout_id)

            if workout_id not in pair_id_count.keys():
                count_of_walkers = 0
            else:
                count_of_walkers = pair_id_count[workout_id]
            show_workouts_kb_builder.button(text=f'{date} | {workout_type} | {count_of_walkers}',
                                            callback_data=f'walks_{workout_id}')

    show_workouts_kb_builder.adjust(1)
    return show_workouts_kb_builder.as_markup()


async def inspect_workout(call: CallbackQuery):
    """
    Обработчик кнопки проверки информации о тренировке
    """
    workout_id = int(call.data.split('_')[1])
    users_in_workout = await RegistrationRequests.get_workout_users(workout_id)
    walkers = enumerate([walker[0] for walker in users_in_workout], 1) # Список учабников тренировки
    listed_walkers = "\n".join([f'{list_info[0]}. {list_info[1]}' for list_info in walkers])
    await call.message.answer(f"Информация о тренировке:\n{listed_walkers}",
                              reply_markup=await delete_workout_kb(workout_id))
    await call.answer('')


async def delete_workout_kb(workout_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для удаления тренировки
    """
    moderate_workout_kb_builder = InlineKeyboardBuilder()
    moderate_workout_kb_builder.button(text='Удалить', callback_data=f'delete_{workout_id}')
    return moderate_workout_kb_builder.as_markup()


async def delete_workout_kb_handler(call: CallbackQuery):
    """
    Обработчик кнопки подтверждения удаления тренировки администратором
    """
    workout_id = int(call.data.split('_')[1])
    result = await WorkoutsRequests.delete_workout(workout_id)
    await call.message.answer(result)
    await call.answer('')
