from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import WorkoutsRequests, RegistrationRequests


async def sign_up_workout_handler(message: Message):
    """Обработчик записи на тренировки - комада /запись"""
    await message.answer('Выберите тренировку для записи:', reply_markup=await choose_workout_kb())


async def choose_workout_kb():
    """Клавиатура выбора тренировки"""
    choose_workout_kb_builder = InlineKeyboardBuilder()

    available_workouts = await WorkoutsRequests.show_workouts()
    # print(available_workouts)
    if available_workouts:
        for workout, type_ in available_workouts:
            date = workout.date.strftime('%d.%m | %H:%M').replace('08:30', '08:30☀').replace('20:30', '20:30🌓')
            workout_type = type_.type_name
            workout_id = workout.workout_id
            choose_workout_kb_builder.button(text=f'{date} | {workout_type}', callback_data=f'signup_{workout_id}')

    else:
        choose_workout_kb_builder.button(text='Нет доступных тренировок',
                                         callback_data='None')

    choose_workout_kb_builder.adjust(1)
    return choose_workout_kb_builder.as_markup()


async def sign_up_workout_to_db(call: CallbackQuery) -> None:
    workout_id = int(call.data.split('_')[-1])
    user_id = call.from_user.id

    await RegistrationRequests.add_registration(user_id, workout_id)

    workout_data = await WorkoutsRequests.get_workout_by_id(workout_id)
    # print(workout_data[0], workout_data[1])
    date = workout_data[0][0].date.strftime('%m.%d')
    time = workout_data[0][0].date.strftime('%H:%M')
    workout_type = workout_data[0][1].type_name

    await call.message.answer(f'Вы записаны на тренировку:\n'
                              f'<b>{date} в {time} тебя ждет {workout_type}</b>')


async def no_available_workout_handler(call: CallbackQuery) -> None:
    await call.answer('Ожидайте добавления тренировок')
