from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from .kbs import *
from .schemas import *
from admin.kbs import *
from utils.utils import *
from db.sheets.tasks import *
from db.sheets.build import *
from db.models.models.manager import *
from loguru import logger
from .form import *
import base64
import uuid


user_router = Router()


@user_router.message(Command("start"))  # Обрабатываем команду /start
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    args = message.text.split(" ")
    redis_id_key_for_incoming_message = args[-1]
    try:
        data_value_for_operator_or_admin = await get_data_from_redis(redis_id_key_for_incoming_message=redis_id_key_for_incoming_message)
        await delete_keys_with_data_from_redis(redis_id_key_for_incoming_message=redis_id_key_for_incoming_message)
        logger.info(message.text)
        logger.info(data_value_for_operator_or_admin)
        decoded_string = data_value_for_operator_or_admin.decode("utf-8")
        incoming_query, tg_id, msg_for_sender = decoded_string.split("_")
        # Проверяем, что в параметре после /start передано что-то, что начинается с "reply_"
        logger.info("yes")
        msg = await message.answer(f"Вы собираетесь ответить пользователю на его тикет - <b>{msg_for_sender}</b> с ID: {tg_id}\n\nНапишите ваш ответ:")
        await state.update_data(tg_id=tg_id)
        await state.update_data(msg_for_sender=msg_for_sender)
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(MessageFromAdmin.send_confirm)  # Переход к состоянию для ответа на сообщение
        return
    except Exception as e:
        logger.info(f"причина почему не получается сделать логику отправки-ответа сообщение от оператора или от клиента - {e}")

    # Проверяем, является ли пользователь администратором
    user_id = message.from_user.id
    if user_id in settings.ADMINS:
        return await message.answer(
            f"👋 Привет, <b>админ- {message.from_user.full_name}!</b> Выберите необходимое действие",
            reply_markup=main_user_kb(user_id)
        )
    else:
        return await message.answer(
            f"👋 Приветствуем, {message.from_user.full_name}! Вы находитесь в боте 'Прием заявок', выберите необходимое действие.",
            reply_markup=main_user_kb(user_id)  # Вероятно, стоит сделать main_user_kb(user_id) для всех пользователей
        )
    

@user_router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = call.from_user.id
    await call.answer("Главная страница")
    return await call.message.answer(
            f"🏆 Вы на главное странице, {call.message.from_user.full_name}! Выберите необходимое действие.",
            reply_markup=main_user_kb(user_id)
    )

@user_router.callback_query(F.data.startswith('send_mess'))
async def page_home(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[-1]
    await state.update_data(tg_id = call.from_user.id)
    await call.answer("Создание тикета")
    text = (
        "Оператор отвечает в течении 30 минут\n"
        "Опишите свою проблему в сообщении.\n"
        "И отправьте оператору."
    )
    msg = await call.message.answer(
            text=text,
            reply_markup=cancel_kb_ticket_inline()
    )
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(MessageFromClient.msg)



@user_router.message(MessageFromClient.msg)
async def page_home(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    data = await state.get_data()
    text = (
        f" <b>СРОК ТИКЕТА 5 ЧАСОВ</b>\n\n"
        f" <b>@{message.from_user.username}</b> отправил сообщение операторам:\n\n\n"
        f" <i>{message.text}</i>"
    )
    await bot.send_message(text=text, chat_id=settings.group_id, reply_markup=await reply_kb(tg_id=data["tg_id"], msg=message.text))
    await message.answer("<b>Вы успешно отправили своё сообщение операторам!</b>")
    await state.clear()
    return await message.answer(
            f"👋 Приветствуем, {message.from_user.full_name}! вы находитесь в боте 'Прием заявок', выберите необходимое действие.",
            reply_markup=main_user_kb(data["tg_id"])
    )
    # await state.update_data(last_msg_id = msg.message_id)
    # await state.set_state(MessageFromClient.msg)

@user_router.callback_query(F.data == 'cancel_more_info')
async def surv_process(call: CallbackQuery, state: FSMContext):
    data_old = await state.get_data()
    for key in ["carpet_area", "material", "extra_services", "availability_dmg", "numb_carp", "quest"]:
        data_old.pop(key, None)
        logger.info(data_old)
    logger.info(data_old)
    await state.set_data(data_old)
    data = await state.get_data()
    quest = data.get("quest", None)
    tariff_text = (
        f" 📦 <b>ЗАЯВКА:</b>\n\n"
        f" 💰 Кол-во ковров: {len(data["quantity"])}.\n"
        f" 💰 Адрес: {data["addres"]}.\n"
        f" ⏲ Предпочтительное время доставки: {data["time"]}.\n\n"
        " ❗<b>Подробности:</b>❗\n\n"
        f" <b>Пятна-повреждения:</b>\n"
        f" <i>{', '.join(data['availability_dmg']) if data.get('availability_dmg') else 'Не указано'}</i>\n"
        f" <b>Материал:</b>\n"
        f" <i>{', '.join(data['material']) if data.get('material') else 'Не указано'}</i>\n"
        f" <b>Площадь:</b>\n"
        f" <i>{', '.join(data['carpet_area']) if data.get('carpet_area') else 'Не указано'}</i>\n"
        f" <b>Доп услуги:</b>\n"
        f" <i>{', '.join(data.get('extra_services')) if data.get('extra_services') else 'Не указаны'}</i>\n\n"
        " 🛒 <b>Проверьте, все ли корректно.</b>"
    )    
    msg = await call.message.edit_text(
        tariff_text,
        reply_markup=yes_or_not_kbs(quest)
    ) 
    await state.update_data(last_msg_id = msg.message_id)
    # await ApplicationsDao.update(session=session_with_commit, record_id=int(apl_id), values=AplicationActiveModel(active=False))
    # update_sheets(sheet=sheet_apl, search_value=call.from_user.id, column_to_search=1, new_value=False, column_to_update=14)
    # await call.answer(f"🆗 Ваша заявка была отменена!", show_alert=True)
    # await call.message.delete()

@user_router.callback_query(F.data.startswith('cancel-apl_'))
async def surv_process(call: CallbackQuery, session_with_commit: AsyncSession):
    _, apl_id = call.data.split('_')
    await ApplicationsDao.update(session=session_with_commit, record_id=int(apl_id), values=AplicationActiveModel(active=False))
    update_sheets(sheet=sheet_apl, search_value=int(apl_id), column_to_search=14, new_value=False, column_to_update=13)
    await call.answer(f"🆗 Ваша заявка была отменена!", show_alert=True)
    await call.message.delete()

@user_router.callback_query(F.data.startswith('red-addres-apl_'))
async def surv_process(call: CallbackQuery, state: FSMContext):
    apl_id = int(call.data.split('_')[-1])
    await state.update_data(id_apl = apl_id)
    msg = await call.message.answer("Отлично введите новый адрес для доставки(улица, дом, город)")
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(Changeadressapl.adress)

@user_router.message(Changeadressapl.adress)
async def surv_process(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    await process_dell_text_msg(message, state)
    await state.update_data(adress=message.text)
    data = await state.get_data()
    apl_id = data.get("id_apl", None)
    await ApplicationsDao.update(session=session_with_commit, record_id=apl_id, values=AplicationAdressModel(addres=message.text))
    update_sheets(sheet=sheet_apl, search_value=apl_id, column_to_search=14, new_value=message.text, column_to_update=11)
    await message.answer(f"🆗 Адресс вашей заявки был поменят")
    await message.answer(f"🏆 Вы на главное странице, {message.from_user.full_name}! Выберите необходимое действие.", reply_markup=main_user_kb(message.from_user.id))

@user_router.callback_query(F.data == "did_apl")
async def page_about(call: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await call.answer("Оформление заявки")
    await state.clear()
    # user_info = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=call.from_user.id))
    await call.message.edit_text(
        f"...",
    )
    msg = await call.message.answer(
        f"Укажите адрес доставки(номер дома, улица, город)",
         reply_markup=cancel_kb_inline()
    )
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(Apladd.addres)


@user_router.message(Apladd.addres)
async def page_about(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await process_dell_text_msg(message, state)
    if validate_length(message.text):
        await state.update_data(addres = message.text)
        msg = await message.answer(
                f"Укажите удобное для вас время доставки(10:00 - 18:00 например)",
                reply_markup=cancel_kb_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        await state.set_state(Apladd.time)
    else:
        
        msg = await message.answer(
            f"Введите корректно, например: Улица пушкина 192, Москва",
            reply_markup=cancel_kb_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        return

@user_router.message(Apladd.time)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    if validate_time_format(message.text):
        await state.update_data(time = message.text)
        msg = await message.answer(
            f"Теперь укажите сколько ковров вам нужно почистить.",
            reply_markup=cancel_kb_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        await state.set_state(Apladd.quantity)
    else:
        msg = await message.answer(
            f"Не правильно, прошу вас ввести строго в формате: 00:00 - 23:00.",
            reply_markup=cancel_kb_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        return

@user_router.message(Apladd.quantity)
async def page_about(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await process_dell_text_msg(message, state)
    try:
        num = int(message.text)
        numbers_list = list(range(1, num + 1))
        await state.update_data(quantity = numbers_list)
        user_info = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=message.from_user.id))
        if not user_info:
            msg = await message.answer(
                f"Напишите свой номер, чтобы с вами связаться",
                reply_markup=cancel_kb_inline()
            )
            await state.update_data(last_msg_id = msg.message_id)
            await state.set_state(Apladd.number)
        else:
            data = await state.get_data()
            quest = data.get("quest", None)
            tariff_text = (
                f" 📦 <b>ЗАЯВКА:</b>\n\n"
                f" 💰 Кол-во ковров: {len(data["quantity"])}.\n"
                f" 💰 Адрес: {data["addres"]}.\n"
                f" ⏲ Предпочтительное время доставки: {data["time"]}.\n\n"
                " ❗<b>Подробности:</b>❗\n\n"
                f" <b>Пятна-повреждения:</b>\n"
                f" <i>{', '.join(data['availability_dmg']) if data.get('availability_dmg') else 'Не указано'}</i>\n"
                f" <b>Материал:</b>\n"
                f" <i>{', '.join(data['material']) if data.get('material') else 'Не указано'}</i>\n"
                f" <b>Площадь:</b>\n"
                f" <i>{', '.join(data['carpet_area']) if data.get('carpet_area') else 'Не указано'}</i>\n"
                f" <b>Доп услуги:</b>\n"
                f" <i>{', '.join(data.get('extra_services')) if data.get('extra_services') else 'Не указаны'}</i>\n\n"
                " 🛒 <b>Проверьте, все ли корректно.</b>"
            )    
            msg = await message.answer(
                tariff_text,
                reply_markup=yes_or_not_kbs(quest)
            ) 
            await state.update_data(last_msg_id = msg.message_id)
    except ValueError:
        await message.answer(text="Вы допустили ошибку, прошу вас ввести числовое значение, для указания кол-во ковров.", reply_markup=cancel_kb_inline())
        return



@user_router.message(Apladd.number)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    if is_valid_international_phone_number(message.text):
        await state.update_data(number = message.text)
        msg = await message.answer(
            f"А фамилию, имя, отчество, введите",
            reply_markup=cancel_kb_inline()
            )
        await state.update_data(last_msg_id = msg.message_id)
        await state.set_state(Apladd.fio)
    else:
        msg = await message.answer(
            f"Ошибка! Введите международный номер телефона, начиная с + и содержащий от 10 до 15 цифр.",
            reply_markup=cancel_kb_inline()
            )
        await state.update_data(last_msg_id = msg.message_id)
        return

@user_router.message(Apladd.fio)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    if is_only_letters(message.text):
        await state.update_data(fio = message.text)
        await state.update_data(quest = False)
        data = await state.get_data()
        quest = data.get("quest", None)
        tariff_text = (
            f" 📦 <b>ЗАЯВКА:</b>\n\n"
            f" 💰 Кол-во ковров: {len(data["quantity"])}.\n"
            f" 💰 Адрес: {data["addres"]}.\n"
            f" ⏲ Предпочтительное время доставки: {data["time"]}.\n\n"
            " ❗<b>Подробности:</b>❗\n\n"
            f" <b>Пятна-повреждения:</b>\n"
            f" <i>{', '.join(data['availability_dmg']) if data.get('availability_dmg') else 'Не указано'}</i>\n"
            f" <b>Материал:</b>\n"
            f" <i>{', '.join(data['material']) if data.get('material') else 'Не указано'}</i>\n"
            f" <b>Площадь:</b>\n"
            f" <i>{', '.join(data['carpet_area']) if data.get('carpet_area') else 'Не указано'}</i>\n"
            f" <b>Доп услуги:</b>\n"
            f" <i>{', '.join(data.get('extra_services')) if data.get('extra_services') else 'Не указаны'}</i>\n\n"
            " 🛒 <b>Проверьте, все ли корректно.</b>"
        )   
        msg = await message.answer(
            tariff_text,
            reply_markup=yes_or_not_kbs(quest)
        ) 
        
        # msg = await message.answer(
        #     f"Отлично, а хотите ли вы предоставить уточнение по поводу чистки ковров(размер, материал, доп услуги, и т.д)?",
        #     reply_markup=yes_or_no_kbs()
        #     )
        await state.update_data(last_msg_id = msg.message_id)
    else:
        msg = await message.answer("Введите без цифр, без символов, ваше ФИО, пожайлуста.", reply_markup=cancel_kb_inline())
        await state.update_data(last_msg_id = msg.message_id)
        return

@user_router.callback_query(F.data == "add_more_info")
async def page_about(call: CallbackQuery, state: FSMContext):
    await process_dell_text_msg(call, state)
    data_old = await state.get_data()
    for key in ["carpet_area", "material", "extra_services", "availability_dmg", "numb_carp"]:
        data_old.pop(key, None)
        logger.info(data_old)
    logger.info(data_old)
    await state.set_data(data_old)
    await state.update_data(quest = True)
    data = await state.get_data()
    logger.info(data)
    numb_carp = data.get("numb_carp", 1)
    await state.update_data(numb_carp = numb_carp)
    msg = await call.message.answer(
    f"Хорошо, укажите из чего ваш {numb_carp} ковер(если не знаете можете написать 'не знаю').",
        reply_markup=cancel_kb_extra_info_inline()
    )
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(Apladd.material)

# @user_router.callback_query(F.data == "add_more_info", Apladd.quest)
# async def page_about(call: CallbackQuery, state: FSMContext):
#     await process_dell_text_msg(call.message, state)
#     await state.update_data(quest = call.data)
#     data = await state.get_data()
#     numb_carp = data.get(numb_carp, 1)
#     msg = await call.message.answer(
#     f"Хорошо, укажите из чего ваш {numb_carp} ковер {", из всех указанных ковров" if len(data["quantity"]) > 1 else ""}?", обработчик на нет когда мы не хотим адд мор инфо
#         reply_markup=cancel_kb_inline()
#     )
#     await state.update_data(last_msg_id = msg.message_id)
#     await state.set_state(Apladd.material)

@user_router.callback_query(F.data == "confirm_add")
async def page_about(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    await process_dell_text_msg(call, state)
    # await state.update_data(quest = call.data)
    await call.answer("Подождите...")
    data = await state.get_data()
    try:
        det_id = None
        if data.get("fio", None):
            user_data = Userapl(
                username = call.from_user.username,
                telegram_id = call.from_user.id,
                fio = data["fio"],
                number = data["number"]
            )
            await UserDAO.add(session=session_with_commit, values=user_data)
            list_user = [call.from_user.id, call.from_user.username, data["fio"], data["number"]]
            add_record_to_google_sheets(sheet=sheet_user, new_record=list_user)
        if data.get("quest", None):
            logger.info(data)
            details_data = DetailsAboutApl(
                extra_services = data.get("extra_services", None),
                carpet_area = data.get("carpet_area", None),
                material = data.get("material", None),
                availability_dmg = data.get("availability_dmg", None)
            )
            details_data = await DetailsAplDAO.add(session=session_with_commit, values=details_data)
            logger.info(details_data)
            det_id = details_data.id
        apl_data = AplicationModel(
            time= str(data["time"]),
            quantity = len(data["quantity"]),
            addres = data["addres"],
            source = "telegram",
            user_id = call.from_user.id,
            active = True,
            det_id = det_id,
        )
        apl_data = await ApplicationsDao.add(session=session_with_commit, values=apl_data)
        user_info = await UserDAO.find_one_or_none(session=session_with_commit, filters=UserBaseInDB(telegram_id = call.from_user.id))
        list_apl = [
            call.from_user.id, call.from_user.username, user_info.fio, user_info.number, data.get("carpet_area", "Не указан"), data.get("material", "Не указан"), data.get("availability_dmg", "Не указано"), data.get("extra_services", "Не выбрано"), len(data["quantity"]), data["time"], data["addres"], "telegram", True, apl_data.id
                        ]
        add_apl_to_google_sheets(sheet=sheet_apl, new_record=list_apl)
        # increase_value_in_google_sheets(sheet_user, search_value=call.from_user.id, column_to_search=1, column_to_update=5)
        await call.message.answer(
            f"Хорошо, вы подали заявку на чистку {"ваших ковров" if len(data["quantity"]) > 1 else "вашего ковера"}",
        )
        await call.message.answer(
            f"Подробнее о ваших заявках, вы можете посмотреть по кнопке 'Мои заявки'.",
            reply_markup=main_user_kb(call.from_user.id)
        )
        await state.clear()
    except Exception as e:
        logger.info(e)
        await state.clear()
        await call.message.answer(
            f"Произошла ошибка добавление заявки",
            reply_markup=main_user_kb(call.from_user.id)
        )

@user_router.message(Apladd.material)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    data = await state.get_data()
    logger.info(data)
    numb_carp = data.get("numb_carp", None)
    mat_list = data.get("material", None)
    if not mat_list:
        mat_list = [message.text]
        await state.update_data(material = mat_list)
    else:
        mat_list.append(message.text)
        await state.update_data(material = mat_list)
    msg = await message.answer(
        f"Это отлично, укажите площадь вашего {numb_carp} ковра(Длина * Ширину)",
        reply_markup=cancel_kb_extra_info_inline()
    )
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(Apladd.carpet_area)

@user_router.message(Apladd.carpet_area)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    if validate_input(message.text):
        data = await state.get_data()
        numb_carp = data.get("numb_carp", None)
        carp_list = data.get("carpet_area", None)
        if not carp_list:
            carp_list = [message.text]
            await state.update_data(carpet_area = carp_list)
        else:
            carp_list.append(message.text)
            await state.update_data(carpet_area = carp_list)
        msg = await message.answer(
            f"Это отлично, укажите причину загрязнения для вашего {numb_carp} ковра ",
            reply_markup=cancel_kb_extra_info_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        await state.set_state(Apladd.availability_dmg)
    else:
        msg = await message.answer(
            f"Вы ввели неправильно, но за место ваших <b>{message.text}</b>, нужно <b>10м</b> или <b>15м</b>, а если не знаете напишите просто 1м(нужно чтобы главное было указание что это м-метры, и было целое число)",
            reply_markup=cancel_kb_extra_info_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        return

@user_router.message(Apladd.availability_dmg)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    data = await state.get_data()
    numb_carp = data.get("numb_carp", None)
    availability_dmg_list = data.get("availability_dmg", None)
    if not availability_dmg_list:
        availability_dmg_list = [message.text]
        await state.update_data(availability_dmg = availability_dmg_list)
    else:
        availability_dmg_list.append(message.text)
        await state.update_data(availability_dmg = availability_dmg_list)
    msg = await message.answer(
        f"Понял вас, теперь выберите какую нибудь доп услугу для {numb_carp} ковра",
        reply_markup=extra_serv()
    )
    await state.update_data(last_msg_id = msg.message_id)
    await state.set_state(Apladd.extra_services)

@user_router.message(Apladd.extra_services)
async def page_about(message: Message, state: FSMContext):
    await process_dell_text_msg(message, state)
    data = await state.get_data()
    numb_carp = data.get("numb_carp", None)
    extra_services_list = data.get("extra_services", None)
    if not extra_services_list:
        extra_services_list = [message.text]
        await state.update_data(extra_services = extra_services_list)
    else:
        extra_services_list.append(message.text)
        await state.update_data(extra_services = extra_services_list)
    quant_total = len(data.get("quantity", None))
    if not numb_carp == quant_total:
        await state.update_data(numb_carp = numb_carp + 1)
        msg = await message.answer(
        f"Хорошо, укажите из чего ваш {numb_carp + 1} ковер",
        reply_markup=cancel_kb_extra_info_inline()
        )
        await state.update_data(last_msg_id = msg.message_id)
        await state.set_state(Apladd.material)
    else:
        data = await state.get_data()
        # quest = data.get("quest", None)
        tariff_text = (
            f" 📦 <b>ЗАЯВКА:</b>\n\n"
            f" 💰 Кол-во ковров: {len(data["quantity"])}.\n"
            f" 💰 Адрес: {data["addres"]}.\n"
            f" ⏲ Предпочтительное время доставки: {data["time"]}.\n\n"
            " ❗<b>Подробности:</b>❗\n\n"
            f" <b>Пятна-повреждения:</b>\n"
            f" <i>{', '.join(data['availability_dmg']) if data.get('availability_dmg') else 'Не указано'}</i>\n"
            f" <b>Материал:</b>\n"
            f" <i>{', '.join(data['material']) if data.get('material') else 'Не указано'}</i>\n"
            f" <b>Площадь:</b>\n"
            f" <i>{', '.join(data['carpet_area']) if data.get('carpet_area') else 'Не указано'}</i>\n"
            f" <b>Доп услуги:</b>\n"
            f" <i>{', '.join(data.get('extra_services')) if data.get('extra_services') else 'Не указаны'}</i>\n\n"
            " 🛒 <b>Проверьте, все ли корректно.</b>"
        )      
        msg = await message.answer(
                tariff_text,
                reply_markup=ok_or_no_kbs()
        )
        await state.update_data(last_msg_id = msg.message_id)
        # try:
        #     if data.get("fio", None):
        #         user_data = Userapl(
        #         username = message.from_user.username,
        #         telegram_id = message.from_user.id,
        #         fio = data["fio"],
        #         number = data["number"]
        #         )
        #         await UserDAO.add(session=session_with_commit, values=user_data)
        #         list_user = [message.from_user.id, message.from_user.username, data["fio"], data["number"], 0]
        #         add_record_to_google_sheets(sheet=sheet_user, new_record=list_user)
        #     # details_data = DetailsAboutApl(
        #     #     extra_services = data.get("extra_services", None),
        #     #     carpet_area = data.get("carpet_area", None),
        #     #     material = data.get("material", None),
        #     #     availability_dmg = data.get("availability_dmg", None)
        #     # )
        #     # details_add = await DetailsAplDAO.add(session=session_with_commit, values=details_data)
        #     apl_data = AplicationModel(
        #         time=str(data["time"]),
        #         quantity = int(data["quantity"]),
        #         addres = data["addres"],
        #         source = "telegram",
        #         user_id = message.from_user.id,
        #         active = True,
        #         det_id = None,
        #     )
        #     apl_data = await ApplicationsDao.add(session=session_with_commit, values=apl_data)
        #     user_info = await UserDAO.find_one_or_none(session=session_with_commit, filters=UserBaseInDB(telegram_id = message.from_user.id))
        #     list_apl = [
        #         message.from_user.username, user_info.fio, user_info.number, data.get("carpet_area", "Не указан"), data.get("material", "Не указан"), data.get("availability_dmg", "Не указано"), data.get("extra_services", "Не выбрано"), len(data["quantity"]), data["time"], data["addres"], "telegram", True
        #                 ]
        #     add_record_to_google_sheets(sheet=sheet_apl, new_record=list_apl)
        #     increase_value_in_google_sheets(sheet_user, search_value=message.from_user.id, column_to_search=1, column_to_update=5)
        #     await message.answer(
        #     f"Хорошо, вы подали заявку на чиску {"ваших ковров" if len(data["quantity"]) > 1 else "вашего ковера"}",
        #     )
        #     await message.answer(
        #     f"Подробнее о ваших заявках, вы можете посмотреть по кнопке 'Мои заявки'.",
        #     reply_markup=main_user_kb(message.from_user.id)
        #     )
        #     await state.clear()
        # except Exception as e:
        #     logger.info(e)
        #     await state.clear()
        #     await message.answer(
        #     f"Произошла ошибка добавление заявки",
        #     reply_markup=main_user_kb(message.from_user.id)
        #     )
    # msg = await message.answer(
    #     f"Это отлично, теперь выберите какую нибудь доп услугу для {numb_carp} ковра, из {", из всех указанных ковров" if len(data["quantity"]) > 1 else ""}(Длина * Ширину)?",
    #     reply_markup=extra_serv()
    # )
    # await state.update_data(last_msg_id = msg.message_id)
    # await state.set_state(Apladd.availability_dmg)

@user_router.callback_query(F.data == "cancel")
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена добавления')
    await call.message.delete()
    await call.message.answer(
        text="Вы отменили добавление заявки",
        reply_markup=main_user_kb(user_id=call.from_user.id)
    )

@user_router.callback_query(F.data == "cancel_ticket")
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена создания тикета')
    await call.message.delete()
    await call.message.answer(
        text="Вы отменили создание тикета.",
        reply_markup=main_user_kb(user_id=call.from_user.id)
    )

@user_router.callback_query(F.data == "my_apls")
async def page_about(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Мои заявки")
    apls = await UserDAO.get_apls_active(session=session_without_commit, telegram_id=call.from_user.id)
    if not apls:
        await call.message.edit_text(
            text="🔍 <b>Вы пока не оформили не одной заяки..</b>\n\n",
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        await call.message.edit_text("👌 <b>Вот ваши заявки</b>")
        logger.info(apls)
        for i in apls:
            details = i.apl_details
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
                f" 📦 <b>ЗАЯВКА:</b>\n\n"
                f" 💰 Кол-во ковров: {i.quantity}.\n"
                f" 💰 Адрес: {i.addres}.\n"
                f" ⏲ Предпочтительное время доставки: {i.time}.\n\n"
                f"{details_text}"
            )   
                
            await call.message.answer(
                appl_text,
                reply_markup=options_apls_kbs(i.id)
            ) 

        await call.message.answer("Меню", reply_markup=main_user_kb(call.from_user.id))
