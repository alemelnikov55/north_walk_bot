from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def is_admin_test(message: Message, state: FSMContext):
    print('start-----------------')
    print(state.get_state())
    await message.answer('Да, ты админ')