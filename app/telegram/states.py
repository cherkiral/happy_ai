from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    waiting_for_thread = State()
