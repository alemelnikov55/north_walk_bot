"""
Модель для проверки пользователем своих записей на тренировки и отмены существующих
"""
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from database.requests import RegistrationRequests


async def show_my_registrations(message: Message):
    """
    Обработчик для команды /my_walks

    Оправляет список актуальных записей для пользователя
    """
    user_id = message.from_user.id
    await message.answer('Если необходимо отменить запись - нажмите на тренировку и подтвердите отмену.'
                         '\nВаши тренировки:',
                         reply_markup=await show_all_my_registrations_kb(user_id))


async def show_all_my_registrations_kb(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для демонстрации всех записей пользователя на тренировки
    :param user_id:
    """
    show_my_registration_kb_builder = InlineKeyboardBuilder()

    registrations = await RegistrationRequests.get_workouts_by_user_id(user_id)

    for registration in registrations:
        date = registration.date.strftime("%m.%d в %H:%M")
        workout_type = registration.type_name
        show_my_registration_kb_builder.button(text=f'{date} | {workout_type}',
                                               callback_data=f'giveup_{registration.registration_id}')

    show_my_registration_kb_builder.adjust(1)
    return show_my_registration_kb_builder.as_markup()


async def give_up_handler(call: CallbackQuery):
    """
    Обработчик кнопки "Отменить запись"
    """
    registration_id = int(call.data.split('_')[1])
    workout_info = await RegistrationRequests.get_workout_info_by_reg_id(registration_id)
    info_for_send = workout_info[0].date.strftime("%d.%m в %H:%M |") + workout_info[0][1]

    await call.message.answer(f'Вы уверены, что хотите удалить тренировку\n{info_for_send}',
                              reply_markup=await delete_confirm_kb(registration_id))
    await call.answer('')


async def delete_confirm_kb(registration_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения удаления тренировки пользователем
    :param registration_id:
    """
    delete_kb = InlineKeyboardBuilder()
    delete_kb.button(text='Да', callback_data=f'delMy_{registration_id}')
    delete_kb.button(text='Нет', callback_data='delMy_no')

    return delete_kb.as_markup()


async def delete_registration(call: CallbackQuery):
    """
    Обработчик клавиатуры подтверждения удаления тренировки.

    Вносит изменения в БД, сообщает об успешном удалении
    :param call:
    """
    answer = call.data.split('_')[1]
    if answer == 'no':
        await call.message.answer('Ну нет так нет...')
        await call.answer('Ну нет так нет...')
        return

    answer = await RegistrationRequests.give_up_registration(int(answer))
    if answer:
        await call.message.answer('Запись на тренировку успешно отменена.')
        await call.answer('Удаление прошло успешно')
