from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputFile, BufferedInputFile, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from .kbs import *
from .schemas import *
from admin.kbs import *
from utils.utils import *
from db.sheets.tasks import *
from db.sheets.build import *
from db.models.models.manager import *
from loguru import logger
from .form import *


admin_router = Router()

@admin_router.callback_query(F.data == "admin_panel", F.from_user.id.in_(settings.ADMINS))
async def admin_process(call: CallbackQuery):
    await call.message.edit_text(f"Здравствуйте <b>{call.from_user.full_name}</b>, вы находитесь в админ панели.", reply_markup=admin_kb())

@admin_router.callback_query(F.data == "users", F.from_user.id.in_(settings.ADMINS))
async def start_admin(call: CallbackQuery, session_without_commit: AsyncSession):
    users = await UserDAO.find_all(session=session_without_commit)
    more_stats = await UserDAO.get_statistics(session=session_without_commit)
    text = (
        "👥 Зарегестрированные пользователи в базе:\n\n"
        "✅ Выберите в меню пользователя чтобы посмотреть <b>его заявки</b>.\n"
        f"👥 Всего пользователей: {more_stats["total_users"]}\n"
    )
    for user in users:
        # stats = await UserDAO.get_apls_statistics(session=session_without_commit, telegram_id=user.telegram_id)
        apls = await UserDAO.get_apls(session=session_without_commit, telegram_id=user.telegram_id)
        apls_active = await UserDAO.get_apls_active(session=session_without_commit, telegram_id=user.telegram_id)
        total_apls = len(apls) if apls else 0
        total_active_apls = len(apls_active) if apls_active else 0
        # all_apls = await UserDAO.get_apls(session=session_without_commit, telegram_id=user.telegram_id)
        # all_apls_active = await UserDAO.get_apls_active(session=session_without_commit, telegram_id=user.telegram_id)
        text += f'👤 <code>@{user.username}</code> - <code>{user.fio}</code> - <code>{user.number}</code>, кол-во заявок - <b>{total_apls}</b>, активных - <b>{total_active_apls}</b>\n'
    await call.message.edit_text(
        text=text,
        reply_markup=await get_paginated_kb(page=0, session=session_without_commit)
    )

@admin_router.callback_query(F.data.startswith('about-user'), F.from_user.id.in_(settings.ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    user_id = int(call.data.split('_')[-1])
    user = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=user_id))
    # stats_about_user = await UserDAO.get_apls_statistics(session=session_without_commit, telegram_id=user.telegram_id)
    apls = await UserDAO.get_apls(session=session_without_commit, telegram_id=user.telegram_id)
    apls_active = await UserDAO.get_apls_active(session=session_without_commit, telegram_id=user.telegram_id)
    total_apls = len(apls) if apls else 0
    total_active_apls = len(apls_active) if apls_active else 0
    text = (
        f" 👤 <code>@{user.username}</code> - <code>{user.fio}</code> - <code>{user.number}</code>:\n\n"
        f"Акт заявок - {total_active_apls}\n\n"
        f"Всех заявок - {total_apls}\n\n"
    )
    await call.message.edit_text(text=text, reply_markup=await get_paginated_kbs_apls(page=0, telegram_id=user.telegram_id, session=session_without_commit))

@admin_router.callback_query(F.data.startswith('about-apl'), F.from_user.id.in_(settings.ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    logger.info(call.data.split('_'))
    _, apl_id, telegram_user_id = call.data.split('_')
    user = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=int(telegram_user_id)))
    apl = await ApplicationsDao.get_apls_and_details_by_id(session=session_without_commit, data_id=int(apl_id))
    details = apl.apl_details
    # stats_about_user = await UserDAO.get_apls_statistics(session=session_without_commit, telegram_id=user.telegram_id)
    # apls = await UserDAO.get_apls(session=session_without_commit, telegram_id=user.telegram_id)
    # apls_active = await UserDAO.get_apls_active(session=session_without_commit, telegram_id=user.telegram_id)
    logger.info(details)
    if not details:
        details_text = "❗ <b>Подробности отсутствуют</b> ❗\n"
    else:
        details_text = (
            "❗ <b>Подробности:</b> ❗\n\n"
            f" <b>Пятна-повреждения:</b>\n"
            f" <i>{', '.join(list(details.availability_dmg)) if details.availability_dmg else 'Не указано'}</i>\n"
            f" <b>Материал:</b>\n"
            f" <i>{', '.join(list(details.material)) if details.material else 'Не указано'}</i>\n"
            f" <b>Площадь:</b>\n"
            f" <i>{', '.join(list(details.carpet_area)) if details.carpet_area else 'Не указано'}</i>\n"
            f" <b>Доп услуги:</b>\n"
            f" <i>{', '.join(list(details.extra_services)) if details.extra_services else 'Не указаны'}</i>\n"
        )
    logger.info(details)
    tariff_text = (
            f" 👤 <i>ФИО:</i> <b>{user.fio}</b>\n"
            f" 👤 <i>Номер:</i> <b>{user.number}</b>\n\n\n"
            f" 📦 <b>ЗАЯВКА:</b>\n\n"
            f" 🛒 Кол-во ковров: {apl.quantity}.\n"
            f" 🏙 Адрес: {apl.addres}.\n"
            f" ⏲ Предпочтительное время доставки: {apl.time}.\n\n"
            f"{details_text}"
    )   
                
    await call.message.edit_text(
            tariff_text,
            reply_markup=await options_apls_kbs_admin(session=session_without_commit, apl_id=int(apl_id))
    ) 

        # await call.message.answer("Меню", reply_markup=main_user_kb(call.from_user.id))
    # text = (
    #     f" 👤 <code>@{user.username}</code> - <code>{user.fio}</code> - <code>{user.number}</code>:\n\n"
    #     f"Акт заявок - {stats_about_user["total_active_apls"]}\n\n"
    #     f"Всех заявок - {stats_about_user["total_apls"]}\n\n"
    # )
    # await call.message.edit_text(text=text, reply_markup=await get_paginated_kbs_apls(page=0, telegram_id=user.telegram_id, session=session_without_commit))

@admin_router.callback_query(F.data.startswith('ogr-apl'), F.from_user.id.in_(settings.ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    apl_id = int(call.data.split('_')[-1])
    apl_data = await ApplicationsDao.find_one_or_none_by_id(session=session_with_commit, data_id=apl_id)
    apl = None
    if apl_data.active:
        values = AplicationActiveModel(
            active = False
        )

        update_sheets(sheet_apl, search_value=apl_data.id, column_to_search=14, new_value=False, column_to_update=13)
        apl = await ApplicationsDao.update(session=session_with_commit, values=values, record_id=apl_data.id)
        user = await UserDAO.find_one_or_none(session=session_with_commit, filters=UserBaseInDB(telegram_id=apl.user_id))
        await call.answer(f"Вы сделали неактивной заявку, на юзера: @{user.username}, {user.fio}, {user.number}", show_alert=True)
    else:
        values = AplicationActiveModel(
            active = True
        )
        update_sheets(sheet_apl, search_value=apl_data.user_id, column_to_search=1, new_value=True, column_to_update=13)
        apl = await ApplicationsDao.update(session=session_with_commit, values=values, record_id=apl_data.id)
        user = await UserDAO.find_one_or_none(session=session_with_commit, filters=UserBaseInDB(telegram_id=apl.user_id))
        await call.answer(f"Вы вновь сделали заявку активной, на юзера: @{user.username}, {user.fio}, {user.number}", show_alert=True)
    appl = await ApplicationsDao.get_apls_and_details_by_id(session=session_with_commit, data_id=apl_id)
    details = appl.apl_details
    logger.info(details)
    if not details:
        details_text = "❗ <b>Подробности отсутствуют</b> ❗\n"
    else:
        details_text = (
            "❗ <b>Подробности:</b> ❗\n\n"
            f" <b>Пятна-повреждения:</b>\n"
            f" <i>{', '.join(list(details.availability_dmg)) if details.availability_dmg else 'Не указано'}</i>\n"
            f" <b>Материал:</b>\n"
            f" <i>{', '.join(list(details.material)) if details.material else 'Не указано'}</i>\n"
            f" <b>Площадь:</b>\n"
            f" <i>{', '.join(list(details.carpet_area)) if details.carpet_area else 'Не указано'}</i>\n"
            f" <b>Доп услуги:</b>\n"
            f" <i>{', '.join(list(details.extra_services)) if details.extra_services else 'Не указаны'}</i>\n"
        )
    logger.info(details)
    appl_text = (
            f" ✅ <b>{"АКТИВНАЯ"if appl.active else "НЕ АКТИВНАЯ"}</b> ✅\n"
            f" 👤 <i>ФИО:</i> <b>{user.fio}</b>\n"
            f" 👤 <i>Номер:</i> <b>{user.number}</b>\n\n\n"
            f" 📦 <b>ЗАЯВКА:</b>\n\n"
            f" 🛒 Кол-во ковров: {appl.quantity}.\n"
            f" 🏙 Адрес: {appl.addres}.\n"
            f" ⏲ Предпочтительное время доставки: {appl.time}.\n\n"
            f"{details_text}"
    )
                
    await call.message.edit_text(text=appl_text, reply_markup=await options_apls_kbs_admin(session=session_with_commit, apl_id=apl_id))

@admin_router.callback_query(F.data.startswith('del-apl'), F.from_user.id.in_(settings.ADMINS))
async def surv_process(call: CallbackQuery, session_with_commit: AsyncSession):
    _, apl_id, user_telegram_id = call.data.split('_')
    await ApplicationsDao.delete(session=session_with_commit, filters=AplicationDetailsIDModel(id = int(apl_id)))
    delete_record_in_google_sheets(sheet=sheet_apl, search_value=int(apl_id), column_to_search=14)
    await call.answer(f"Заявка была удалена, безвозвратно.", show_alert=True)
    await call.message.delete()

# @admin_router.message(Command("rplymsg"), F.from_user.id.in_(settings.ADMINS))
# async def surv_process(message: Message, state: FSMContext):
#     # user_telegram_id = call.data.split('_')[-1]
#     args = message.text.split(" ") 
#     if len(args) > 1 and args[1].startswith("reply_"):
#         tg_id = args[1].split("_")[1]
#         msg = await message.answer(f"Вы собираетесь ответить пользователю с ID: {tg_id}\n\nНапишите ваш ответ:")
#         await state.update_data(tg_id = tg_id)
#         await state.update_data(last_msg_id = msg.message_id)
#         await state.set_state(MessageFromAdmin.msg)

# @admin_router.message(Command("delmsg"), F.from_user.id.in_(settings.ADMINS))
# async def surv_process(message: Message, state: FSMContext):
#     # user_telegram_id = call.data.split('_')[-1]
#     args = message.text.split(" ") 
#     if len(args) > 1 and args[1].startswith("delmsg_"):
#         tg_id = args[1].split("_")[1]
#         await bot.send_message(f"Оператор завершил тикет", chat_id=tg_id)
#         await message.answer("Вы находитесь в админ меню.", reply_markup=admin_kb())

@admin_router.message(MessageFromAdmin.msg, F.from_user.id.in_(settings.ADMINS))
async def surv_process(message: Message, state: FSMContext):
    data = await state.get_data()
    logger.info(data)
    logger.info(message.text)
    data = message.text.split(" ")[-1]
    quer, user_id, msg_sender, usrnm =  data.split("_")
    msg = await message.answer(f"Вы собираетесь ответить пользователю на его тикет <i>{usrnm}</i> - <b>{msg_sender}</b> \n\nНапишите ваш ответ на его вопрос:")
    await state.update_data(tg_id=user_id)
    await state.update_data(msg_for_sender=msg_sender)
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(MessageFromAdmin.send_confirm)

@admin_router.message(MessageFromAdmin.send_confirm, F.from_user.id.in_(settings.ADMINS))
async def surv_process(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    await process_dell_text_msg(message, state)
    try:
        logger.info(message.text)
        await state.update_data(msg = message.text)
        data = await state.get_data()
        text = (
            "      ⁉ <b>ВАМ ПРИШЛО СООБЩЕНИЕ ОТ ОПЕРАТОРА</b> ⁉       \n\n"
            f"                  {message.text}                          \n"
            "      ⁉ <b>ВАМ ПРИШЛО СООБЩЕНИЕ ОТ ОПЕРАТОРА</b> ⁉          "
        )
        
        photo = FSInputFile("photos/image_adm.jpg") 
        # input_file = BufferedInputFile(photo_data, filename="image_adm.jpg")  
        await bot.send_photo(chat_id=data["tg_id"], photo=photo, caption=text)
        # await TicketDAO.find_one_or_none_by_id(session=session_with_commit, data_id=)
        # if 
        # await TicketDAO.add(session=session_with_commit, values=Ticketadd(tg_id_client=data["tg_id"], msg_operator=data["msg"]))
        await message.answer(f"Вы отравили сообщение <b>{message.text}, ожидайте ответа, или завершите диалог.</b>")
        await state.clear()
        await message.answer("Ваше сообщение было успешно адресовано!", reply_markup=admin_kb())
        # await ApplicationsDao.delete(session=session_with_commit, filters=AplicationDetailsIDModel(id = apl_id))
        # delete_record_in_google_sheets(sheet=sheet_apl, search_value=user_telegram_id, column_to_search=1)
        # await call.answer(f"Заявка была удалена, безвозвратно.", show_alert=True)
        # await call.message.delete()
    except Exception as e:
        logger.info(e)
        message.answer("Произошла ошибка при отправке сообщение клиенту")

@admin_router.callback_query(Pagination_other.filter())
async def products_pagination_callback_for_apls(call: CallbackQuery, callback_data: dict,  session_without_commit: AsyncSession):
    page = callback_data.page
    telegram_id = callback_data.telegram_id
    logger.info(page)
    await call.message.edit_reply_markup(  
    reply_markup=await get_paginated_kbs_apls(telegram_id=telegram_id, page=page, session=session_without_commit)  
)


@admin_router.callback_query(Pagination.filter())
async def products_pagination_callback(call: CallbackQuery, callback_data: dict,  session_without_commit: AsyncSession):
    page =  callback_data.page
    logger.info(page)
    await call.message.edit_reply_markup(  
    reply_markup=await get_paginated_kb(page=page, session=session_without_commit)  
)
