from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import *
from utils.utils import *
from db.models.ormmodels.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.models.manager import *


async def reply_kb(tg_id, msg) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    str_params = f"reply_{tg_id}_{msg}"
    link_redis_str_params = await generate_short_link(str_params)
    kb.button(text="✅ Ответить", url=f"{link_redis_str_params}")
    kb.adjust(2)
    return kb.as_markup()


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if user_id in settings.ADMINS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    else:
        kb.button(text="📂 Мои заявки", callback_data="my_apls")
        kb.button(text="✨ Оформить заявку", callback_data="did_apl")
        kb.button(text="🎫 Создать тикет", callback_data=f"send_mess_{user_id}")
        kb.button(text="⁉ У меня есть вопросы", callback_data=f"talking_with_gpt")
    kb.adjust(3, 1)
    return kb.as_markup()

def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
    return kb.as_markup()

def cancel_kb_ticket_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel_ticket")
    return kb.as_markup()

def cancel_kb_extra_info_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel_more_info")
    return kb.as_markup()

def options_apls_kbs(apl_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отменить заявку", callback_data=f"cancel-apl_{apl_id}")
    kb.button(text="🚗 Изменить адрес", callback_data=f"red-addres-apl_{apl_id}")
    kb.adjust(1)
    return kb.as_markup()

# async def options_apls_kbs_admin(apl_id: int, session: AsyncSession) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     apl = await ApplicationsDao.find_one_or_none_by_id(session=session, data_id=apl_id)
#     if apl.active:
#         kb.button(text="☝🏻 Сделать заявку не акт", callback_data=f"ogr-apl_{apl.id}")
#     else:
#         kb.button(text="☝🏻 Сделать активной", callback_data=f"ogr-user_{apl.id}")
#     kb.button(text="👤 Отправить сообщ клиенту", callback_data=f"send-mess_{apl.user_id}")
#     kb.button(text="❌ Удалить заявку", callback_data=f"cancel-apl_{apl_id}")
#     kb.adjust(1)
#     return kb.as_markup()

def yes_or_not_kbs(quest) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not quest:
        kb.button(text="🔄 Ред доп инфо", callback_data=f"add_more_info")
    kb.button(text="❗ Начать заново", callback_data=f"did_apl")
    kb.button(text="✅ Верно", callback_data=f"confirm_add")
    kb.adjust(1, 2)
    return kb.as_markup()

def ok_or_no_kbs() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Заново ред доп инфо", callback_data=f"add_more_info")
    kb.button(text="❗ Начать заново", callback_data=f"did_apl")
    kb.button(text="✅ Верно", callback_data=f"confirm_add")
    kb.adjust(1, 2)
    return kb.as_markup()


def yes_or_no_kbs() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Знаю", callback_data=f"yes")
    kb.button(text="Нет", callback_data=f"no")
    kb.button(text="Отмена", callback_data="cancel")
    kb.adjust(2, 1)
    return kb.as_markup()

def time_get(apls) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    btns = []
    for i in apls:
        if not i.time in btns:
            btns.append(i.time)
            kb.button(text=f"{i.time}")
    kb.adjust(1)
    
    return kb.as_markup(resize_keyboard=True)

def adders_get(apls) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    btns = []
    for i in apls:
        if not i.addres in btns:
            btns.append(i.addres)
            kb.button(text=f"{i.addres}")
    kb.adjust(1)
    
    return kb.as_markup(resize_keyboard=True)

def idk_kbs() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Не знаю")
    kb.adjust(1)
    
    return kb.as_markup(resize_keyboard=True)

def material_carpet() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Шерсть")
    kb.button(text="Смешанная шерсть")
    kb.button(text="Вискоза")
    kb.button(text="Хлопок")
    kb.button(text="Натуральный шёлк")
    kb.button(text="Ручная работа")
    kb.button(text="Другое")
    kb.adjust(3, 3, 1)
    
    return kb.as_markup(resize_keyboard=True)

def dmg_carpet() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Пятна")
    kb.button(text="Прожоги")
    kb.button(text="Следы плесени")
    kb.button(text="Старые пятна")
    kb.button(text="Прорехи по шву")
    kb.button(text="Отслоение основы")
    kb.button(text="Другое")
    kb.adjust(3, 3, 1)
    
    return kb.as_markup(resize_keyboard=True)


def extra_serv() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Удаление сложных пятен")
    kb.button(text="Удаление запахов и мочи животных")
    kb.button(text="Озонирование ковра")
    kb.button(text="Кондиционирование ворса")
    kb.button(text="Ковёр после потопа")
    kb.button(text="Очистка бахромы вручную")
    kb.button(text="Антибактериальная обработка")
    kb.button(text="Ремонт ковра (локальный)")
    kb.button(text="Оверлок (обработка краёв) ")
    kb.button(text="Не нужно")
    kb.adjust(6, 3, 1)
    
    return kb.as_markup(resize_keyboard=True)