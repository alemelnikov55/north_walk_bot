"""
Модуль добавления тренировки
"""
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram_calendar import SimpleCalendar

from database.data_models import Workout
from database.requests import ServiceRequests, WorkoutsRequests
from utils.workouts_types import workout_types
from utils.states import ChooseWorkoutTimeState
from utils.support_func import get_formatted_list_of_users_by_workout_id

from loader import MainSettings


async def add_workout(message: Message):
    """
    Обработчик команды /add_walk

    Вызывает клавиатуру с календарем для выбора даты
    """
    calendar = SimpleCalendar(show_alerts=True)
    await message.answer(
        'Выберите дату тренировки',
        reply_markup=await calendar.start_calendar()
    )


async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    """
    Обработчик нажатия на дату в календаре

    Отправляет выбранную дату и клавиатуру с выбором типа тренировки
    """
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime.today(), datetime.today() + timedelta(days=100))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    await state.update_data(date=date)
    if selected:
        await callback_query.message.answer(
            f'Ваш выбор: {date.strftime("%d.%m.%Y")}',
            reply_markup=await choose_workout_type_kb()
        )


async def choose_time_for_workout_handler(call: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора времени для тренировки
    """
    workout_type_id = int(call.data.split('_')[1])
    # time = call.data.split('_')[-1]
    await state.update_data(workout_type_id=workout_type_id)
    await call.message.answer(
        'Выберите время для тренировки',
        reply_markup=await choose_time_for_workout_kb()
    )
    await call.answer('Время выбрано')


async def set_time_for_workout(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    """
    Обработка, выбранного времени для тренировки
    """
    time = call.data.split('_')[-1]
    if time == 'morning':
        time = timedelta(hours=9, minutes=00)
        # await state.update_data(time=time)
        # await add_workout_to_db(call, bot, state, scheduler)
    elif time == 'evening':
        time = timedelta(hours=20, minutes=30)
    else:
        await call.message.answer('Введите время тренировки в формате ЧЧ:MM')
        await state.set_state(ChooseWorkoutTimeState.CHOOSE_TIME)
    await state.update_data(time=time)
    workout_data = await add_workout_to_db(call, state)
    # создание задачи на отправку сообщения за час до начала тренировки
    scheduler.add_job(remainder_with_list_of_users,
                      trigger='date',
                      run_date=workout_data.date - timedelta(hours=1),
                      kwargs={'workout_id': workout_data.workout_id})
    await call.answer('Время выбрано')


async def custom_time_handler(message: Message, bot: Bot, state: FSMContext, scheduler: AsyncIOScheduler):
    """
    Обработчик ввода времени для тренировки вручную
    """
    time = message.text.split(':')
    if len(time) == 2 and 0 <= int(time[0]) < 24 and 0 <= int(time[1]) < 60:
        time = timedelta(hours=int(time[0]), minutes=int(time[1]))
        await state.update_data(time=time)
        await state.set_state(ChooseWorkoutTimeState.ADD_WORKOUT)

        workout_data = await add_workout_to_db(message, state)
        scheduler.add_job(remainder_with_list_of_users,
                          trigger='date',
                          run_date=workout_data.date - timedelta(hours=1),
                          kwargs={'workout_id': workout_data.workout_id})
    else:
        await message.answer('Введите время тренировки в формате ЧЧ:MM')


async def add_workout_to_db(message: Message | CallbackQuery, state: FSMContext) -> Workout:
    """
    Добавление тренировки в базу данных
    """
    user_id = message.from_user.id
    data = await state.get_data()

    date = data.get('date')
    time = data.get('time')
    new_date = date + time

    workout_type_id = data.get('workout_type_id')
    workout = await WorkoutsRequests.create_workout(new_date, workout_type_id, user_id)
    answer_message = (f'Тренировка <b>{workout_types[workout.type_id]}</b> добавлена на <b>{workout.date.strftime("%d.%m")}</b>'
                      f' в <b>{workout.date.strftime("%H:%M")}</b>.\n '
                      f'Вы можете добавить еще тренировки.')

    if isinstance(message, CallbackQuery):
        await message.message.answer(answer_message)
    else:
        await message.answer(answer_message)
    return workout


async def remainder_with_list_of_users(bot: Bot, workout_id: int):
    """
    Отправляет уведомления тренеру, сообщая список участников за час до занятия
    :param bot:
    :param workout_id:
    :return:
    """
    users_list = await get_formatted_list_of_users_by_workout_id(workout_id)
    for user_id in (MainSettings.SUPERUSER, 6416472110):
        await bot.send_message(
            chat_id=user_id,
            text=f"Записаны:\n{users_list}",
        )


async def choose_workout_type_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа тренировки
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardBuilder()

    types = await ServiceRequests.fetch_all_from_table('workout_types')
    for type_ in types:
        text = type_[1]
        workout_type_id = type_[0]
        keyboard.button(text=text, callback_data=f'choose_{workout_type_id}')

    keyboard.adjust(1)

    return keyboard.as_markup()


async def choose_time_for_workout_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора времени для тренировки
    """
    times_keyboard = InlineKeyboardBuilder()

    times_keyboard.button(text='Утро ☀', callback_data='time_morning')
    times_keyboard.button(text='Вечер 🌓', callback_data='time_evening')
    times_keyboard.button(text='Вручную', callback_data='time_custom')

    times_keyboard.adjust(2)

    return times_keyboard.as_markup()
