from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from database.requests import RegistrationRequests
from utils.workouts_types import workout_types


async def check_workouts(message: Message):
    """
    Обрабртка команды /check_walks

    Запускае т сценарий проверки присутвия людей на тренировках.
    """
    await message.answer('Выберите тренировку для проверки:', reply_markup=await moderate_workout_kb())


async def moderate_workout_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки посещаемости тренировки
    """
    moderate_workout_kb_builder = InlineKeyboardBuilder()

    last_week_workouts = await RegistrationRequests.get_last_week_workouts(7)

    for workout, workout_type in last_week_workouts:
        date = (workout.date.strftime('%d.%m | %H:%M')
                .replace('08:30', '08:30☀')
                .replace('20:30', '20:30🌓'))
        workout_type = workout_type.type_name
        workout_id = str(workout.workout_id)

        moderate_workout_kb_builder.button(text=f'{date} | {workout_type}',
                                           callback_data=f'check_{workout_id}')

    moderate_workout_kb_builder.adjust(1)
    return moderate_workout_kb_builder.as_markup()


async def check_workout_kb_handler(call: CallbackQuery, bot: Bot):
    """
    Обработка обновлений от moderate_workout_kb

    Отправляет администратору всех участников с ФИ/username и клавиатурой user_status_change_kb
    """
    workout_id = int(call.data.split('_')[1])
    users = await RegistrationRequests.get_workout_username_and_id(workout_id)
    await call.answer('Выберите присутствовавших участников')
    for user_and_workout_info in users:
        date = user_and_workout_info.date.strftime('%d.%m | %H:%M').replace('08:30', '08:30☀').replace('20:30', '20:30🌓')
        text = (f'{user_and_workout_info.name}\n'
                f'{date} | {user_and_workout_info.type_name} #{workout_id}')
        try:  # обработка исключения, если нет аватарки
            file = await bot.get_user_profile_photos(user_and_workout_info.user_id)
        except TelegramBadRequest as e:
            print(e)
            await call.message.answer(text, reply_markup=await user_status_change_kb(user_and_workout_info.user_id))
            continue

        photo = file.photos[0][0].file_id
        await call.message.answer_photo(photo, caption=text, reply_markup=await user_status_change_kb(user_and_workout_info.user_id))


async def user_status_change_kb(user_id) -> InlineKeyboardMarkup:
    """
    Клавиатура для изменения статуса участника

    Доступные кнопки: был/не был
    """
    status_kb = InlineKeyboardBuilder()

    status_kb.button(text='Был ✅', callback_data=f'stat_y_{user_id}')
    status_kb.button(text='Не был ❌', callback_data=f'stat_n_{user_id}')

    status_kb.adjust(2)
    return status_kb.as_markup()


async def user_status_change_kb_handler(call: CallbackQuery, bot: Bot):
    """
    Обработка нажатия клавиатуры для изменения статута записи пльзователя

    Изменяет запись в таблице Registration
    """
    user_id = int(call.data.split('_')[-1])
    status_code = call.data.split('_')[1]

    message_id = call.message.message_id
    chat_id = call.message.chat.id

    # Информация, зависящая от нажатой кнопки
    status = 5  # не посетил
    adding_text = '- Не был ❌'
    if status_code == 'y':
        status = 2  # посетил
        adding_text = '- Был ✅'

    if call.message.caption:
        workout_id = int(call.message.caption.split('#')[-1])
        text = call.message.caption.split('#')[0]
        await bot.edit_message_caption(message_id=message_id, chat_id=chat_id, caption=f'{text.strip()} {adding_text}')
    else:
        workout_id = int(call.message.text.split('#')[-1])
        text = call.message.text.split('#')[0]
        await bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'{text.strip()} {adding_text}')

    result = await RegistrationRequests.update_user_status(workout_id, user_id, status)
    if result:
        await call.answer('Статус изменен')


