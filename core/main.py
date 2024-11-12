import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram_calendar import SimpleCalendarCallback

from loader import MainSettings
from utils.support_commands import start_bot_sup_handler, stop_bot_sup_handler
from utils.states import ChooseWorkoutTimeState

from filters.is_admin_filter import IsAdmin

from handlers.admin.add_workout import add_workout, set_time_for_workout, process_simple_calendar, \
    choose_time_for_workout_handler, custom_time_handler
from handlers.admin.show_walk_handler import show_walks_handler, inspect_workout, \
    delete_workout_kb_handler
from handlers.admin.check_workout_handler import check_workout_kb_handler, check_workouts, user_status_change_kb_handler

from handlers.sign_up_workouts_handler import no_available_workout_handler, sign_up_workout_handler, \
    sign_up_workout_to_db
from handlers.show_registration_handler import show_my_registrations, give_up_handler, delete_registration
from handlers.start_handler import start_handler


dispatcher = Dispatcher()
init_bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def start_bot(bot: Bot, dp: Dispatcher):
    await bot.delete_webhook()
    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)

    dp.callback_query.register(process_simple_calendar, SimpleCalendarCallback.filter()) # от календаря
    dp.callback_query.register(choose_time_for_workout_handler, F.data.startswith('choose_')) # выбор времени тренировки
    dp.callback_query.register(set_time_for_workout, F.data.startswith('time_')) # выбор времени тренировки
    dp.callback_query.register(inspect_workout, F.data.startswith('walks_')) # проверка информации о тренировки
    dp.callback_query.register(delete_workout_kb_handler, F.data.startswith('delete_')) # удаление тренировки админом
    dp.callback_query.register(check_workout_kb_handler, F.data.startswith('check_')) # проверка присутствия
    dp.callback_query.register(user_status_change_kb_handler, F.data.startswith('stat_')) # изменение статуса

    dp.callback_query.register(sign_up_workout_to_db, F.data.startswith('signup_')) # запись на тренировку
    dp.callback_query.register(no_available_workout_handler, F.data == 'None') # нет доступных тренировок
    dp.callback_query.register(give_up_handler, F.data.startswith('giveup_')) # отмена записи на тренировку
    dp.callback_query.register(delete_registration, F.data.startswith('delMy_')) # проверка подтверждения удаления

    dp.message.register(add_workout, Command(commands='add_walk'), IsAdmin())
    dp.message.register(custom_time_handler, ChooseWorkoutTimeState.CHOOSE_TIME)
    dp.message.register(show_walks_handler, Command(commands='show_walk'))
    dp.message.register(check_workouts, Command(commands='check_walks'), IsAdmin())

    dp.message.register(start_handler, Command(commands='start'))
    dp.message.register(show_my_registrations, Command(commands='my_walks'))
    dp.message.register(sign_up_workout_handler, Command(commands='sign_up'))

    # dp.message.register(is_admin_test, IsAdmin())

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot(init_bot, dispatcher))
