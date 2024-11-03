from aiogram.fsm.state import StatesGroup, State


class Payments(StatesGroup):
    choose_service = State()
