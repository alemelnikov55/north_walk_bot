import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram_calendar import SimpleCalendarCallback
from aiogram.types import Update

from loader import MainSettings
from utils.support_commands import start_bot_sup_handler, stop_bot_sup_handler
from utils.states import UserAddState, ChooseWorkoutTimeState

from filters.is_admin_filter import IsAdmin

from handlers.test import is_admin_test
from handlers.add_workout import add_workout, set_time_for_workout, process_simple_calendar, add_workout_to_db, \
    choose_time_for_workout_handler, custom_time_handler
from handlers.add_user_handler import add_user_handler_process, add_user_handler_starter
from handlers.sign_up_workouts_handler import no_available_workout_handler, sign_up_workout_handler, sign_up_workout_to_db
from handlers.show_registration_handler import show_my_registrations
from handlers.start_handler import start_handler

dispatcher = Dispatcher()
init_bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def start_bot(bot: Bot, dp: Dispatcher):
    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)

    dp.callback_query.register(process_simple_calendar, SimpleCalendarCallback.filter())
    dp.callback_query.register(choose_time_for_workout_handler, F.data.startswith('choose_'))
    dp.callback_query.register(set_time_for_workout, F.data.startswith('time_'))
    dp.callback_query.register(sign_up_workout_to_db, F.data.startswith('signup_'))
    dp.callback_query.register(no_available_workout_handler, F.data == 'None')

    dp.message.register(start_handler, Command(commands='start'))
    dp.message.register(add_workout, Command(commands='add_walk'), IsAdmin())
    dp.message.register(custom_time_handler, ChooseWorkoutTimeState.CHOOSE_TIME)

    # dp.message.register(add_user_handler_starter, Command(commands='register'))
    dp.message.register(add_user_handler_process, UserAddState.ASK_USERNAME)
    dp.message.register(show_my_registrations, Command(commands='мои_записи'))

    dp.message.register(sign_up_workout_handler, Command(commands='запись'))

    # dp.message.register(is_admin_test, IsAdmin())

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot(init_bot, dispatcher))
