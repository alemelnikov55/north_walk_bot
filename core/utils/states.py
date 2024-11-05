from aiogram.filters.state import State, StatesGroup


class UserAddState(StatesGroup):
    ASK_USERNAME = State()


class ChooseWorkoutTimeState(StatesGroup):
    CHOOSE_TIME = State()
    ADD_WORKOUT = State()
