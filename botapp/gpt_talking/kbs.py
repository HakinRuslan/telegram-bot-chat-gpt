from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import *
from db.models.ormmodels.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.models.manager import *

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

def gpt_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="home")
    kb.button(text="💤 Задать вопрос оператору", callback_data=f"send_mess_{user_id}")
    kb.adjust(1)
    return kb.as_markup()

def gpt_questions() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Хочу расчитать стоимость")
    kb.button(text="Покажите прайс лист")
    kb.button(text="Хочу оформить заказ")
    kb.adjust(2, 1)
    
    return kb.as_markup(resize_keyboard=True)