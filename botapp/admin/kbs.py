from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from db.models.ormmodels.models import *
from db.models.models.manager import *
from .form import *
from .schemas import *



async def options_apls_kbs_admin(apl_id: int, session: AsyncSession) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    apl = await ApplicationsDao.find_one_or_none_by_id(session=session, data_id=apl_id)
    if apl.active:
        kb.button(text="☝🏻 Сделать заявку не акт", callback_data=f"ogr-apl_{apl.id}")
    else:
        kb.button(text="☝🏻 Сделать активной", callback_data=f"ogr-apl_{apl.id}")
    kb.button(text="❌ Удалить заявку", callback_data=f"del-apl_{apl_id}_{apl.user_id}")
    kb.button(text="⬅️ Назад", callback_data=f"about-user_{apl.user_id}")
    kb.adjust(1)
    return kb.as_markup()

async def get_paginated_kb(session: AsyncSession, page: int) -> InlineKeyboardMarkup:

    products = await UserDAO.find_all(session=session)
    builder = InlineKeyboardBuilder()
    start_offset = page * 5
    end_offset = start_offset + 5

    for product in products[start_offset:end_offset]:  
        builder.row(InlineKeyboardButton(text=product.username if product.username else product.fio, callback_data=f"about-user_{product.telegram_id}"))

    buttons_row = []
    if page > 0:  
        buttons_row.append(  
            InlineKeyboardButton(  
                text="⬅️",  
                callback_data=Pagination(page=page - 1).pack(), 
            )  
        )  
    if end_offset < len(products):
        print(page)
        buttons_row.append(  
            InlineKeyboardButton(  
                text="➡️",  
                callback_data=Pagination(page=page + 1).pack()
            )  
        )
    buttons_row.append(InlineKeyboardButton(  
        text="⚙️ Админ панель",  
        callback_data="admin_panel"
    ))
    builder.row(*buttons_row)

    return builder.as_markup()


async def get_paginated_kbs_apls(session: AsyncSession, page: int, telegram_id: int) -> InlineKeyboardMarkup:

    products = await UserDAO.find_apls_of_users(session=session, telegram_id=telegram_id)
    builder = InlineKeyboardBuilder()
    start_offset = page * 5
    end_offset = start_offset + 5

    for product in products.applications[start_offset:end_offset]:  
        builder.row(InlineKeyboardButton(text=f"{"Активная" if product.active else ""} заявка {product.id}", callback_data=f"about-apl_{product.id}_{telegram_id}"))

    buttons_row = []
    if page > 0:  
        buttons_row.append(  
            InlineKeyboardButton(  
                text="⬅️",  
                callback_data=Pagination_other(page=page - 1, telegram_id=telegram_id).pack(), 
            )  
        )  
    if end_offset < len(products.applications):
        print(page)
        buttons_row.append(  
            InlineKeyboardButton(  
                text="➡️",  
                callback_data=Pagination_other(page=page + 1, telegram_id=telegram_id).pack()
            )  
        )
    buttons_row.append(InlineKeyboardButton(  
        text="👤 Управлять пользователями",  
        callback_data="users"
    ))
    builder.row(*buttons_row)

    return builder.as_markup()

# def catalog_admin_kb(catalog_data: List[Typoftariffs]) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     for category in catalog_data:
#         kb.button(text=category.type_tarif_name, callback_data=f"add_category_{category.id}")
#     kb.button(text="Отмена", callback_data="admin_panel")
#     kb.adjust(2)
#     return kb.as_markup()


# def admin_send_file_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Без файла", callback_data="without_file")
#     kb.button(text="Отмена", callback_data="admin_panel")
#     kb.adjust(2)
#     return kb.as_markup()

def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Управлять пользователями", callback_data="users")
    kb.button(text="⬅️ Назад", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

def end_the_ticket(tg_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Написать оператору", callback_data=f"send_mess_{tg_id}")
    kb.adjust(2)
    return kb.as_markup()

# def end_the_ticket(tg_id) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="👌 Завершить разговор", callback_data=f"delete-ticket_{tg_id}")
#     kb.adjust(2)
#     return kb.as_markup()

def end_the_ticket_v2(tg_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Завершить", callback_data=f"delete-ticket_{tg_id}")
    kb.adjust(2)
    return kb.as_markup()

# async def admin_kb_user(user_id, session: AsyncSession) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     user = await UserDAO.find_one_or_none(session=session, filters=UserBaseInDB(telegram_id=user_id))
#     if user.active:
#         kb.button(text="⚙️ Ограничить", callback_data=f"ogr-user_{user_id}")
#     else:
#         kb.button(text="⚙️ Снять огранечения", callback_data=f"ogr-user_{user_id}")
#     kb.button(text="⚙️ Назад", callback_data="users")
#     kb.button(text="🏠 В админ панель", callback_data="admin_panel")
#     kb.adjust(2)
#     return kb.as_markup()


# def stat_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="🔄 Управлять пользователями", callback_data="users")
#     kb.button(text="⚙️ Назад", callback_data="admin_panel")
#     kb.button(text="🏠 На главную", callback_data="home")
#     kb.adjust(2)
#     return kb.as_markup()



# def admin_kb_back() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
#     kb.button(text="🏠 На главную", callback_data="home")
#     kb.adjust(1)
#     return kb.as_markup()


# def options_product_kb(product_id: int) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="🗑️ Удалить", callback_data=f"dell-tariff_{product_id}")
#     kb.button(text="💤 Изменить название", callback_data=f"red-tariff-name_{product_id}")
#     kb.button(text="🎈 Изменить описание", callback_data=f"red-tariff-desc_{product_id}")
#     kb.button(text="💵 Изменить цену", callback_data=f"red-tariff-price_{product_id}")
#     kb.button(text="🔧 Выбрать другой тип", callback_data=f"red-tariff-type_{product_id}")
#     kb.adjust(3, 2)
#     return kb.as_markup()

# def options_cat_kb(product_id: int) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="🗑️ Удалить", callback_data=f"dell-type-tariff_{product_id}")
#     kb.button(text="💤 Изменить название", callback_data=f"red-type-name_{product_id}")
#     kb.button(text="⌚ Изменить срок", callback_data=f"red-type-exc_{product_id}")
#     kb.adjust(1, 3)
#     return kb.as_markup()


# def product_management_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="➕ Добавить подписку", callback_data="add_product")
#     kb.button(text="🏆 Подписки", callback_data="options_tariff")
#     kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
#     kb.button(text="🏠 На главную", callback_data="home")
#     kb.adjust(2, 2, 1)
#     return kb.as_markup()

# def category_management_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="➕ Добавить тип подписок", callback_data="add_cat")
#     kb.button(text="✨ Типы подписок", callback_data="options_type_tariff")
#     kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
#     kb.button(text="🏠 На главную", callback_data="home")
#     kb.adjust(2, 2, 1)
#     return kb.as_markup()


# def cancel_kb_inline() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Отмена", callback_data="cancel")
#     return kb.as_markup()


# def admin_confirm_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Все верно", callback_data="confirm_add")
#     kb.button(text="Отмена", callback_data="admin_panel")
#     kb.adjust(1)
#     return kb.as_markup()