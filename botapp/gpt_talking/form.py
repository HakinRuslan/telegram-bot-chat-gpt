from aiogram.fsm.state import StatesGroup, State

class Tallking_gpt(StatesGroup):
    tg_id = State()
    msg = State()