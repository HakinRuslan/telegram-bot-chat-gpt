from aiogram.fsm.state import StatesGroup, State

class Changeadressapl(StatesGroup):
    adress = State()
    id_apl = State()

class MessageFromClient(StatesGroup):
    msg = State()
    tg_id = State()
    msg_for_sender = State()

class Apladd(StatesGroup):
    fio = State()
    number = State()
    time = State()
    addres = State()
    quantity = State()
    quest = State()
    numb_carp = State()
    carpet_area = State()
    material = State()
    extra_services = State()
    availability_dmg = State()