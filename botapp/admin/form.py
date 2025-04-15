from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State


class Pagination(CallbackData, prefix="pag"):
    page: int


class MessageFromAdmin(StatesGroup):
    msg = State()
    tg_id = State()
    msg_for_sender = State()
    send_confirm = State()


class Pagination_other(CallbackData, prefix="pag"):
    page: int
    telegram_id: int