from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from .kbs import *
from admin.kbs import *
from bot import client_gpt
from utils.utils import *
from db.sheets.tasks import *
from db.sheets.build import *
from db.models.models.manager import *
from loguru import logger
from .form import *
from .fn_utils import *
from .delay import *


chat_gpt_router = Router()


@chat_gpt_router.callback_query(F.data == "talking_with_gpt")
async def gpt_bot_tallking(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Вы попали к нашему консультанту, задайте вопрос и он постарается ответить!", reply_markup=gpt_questions())
    await state.set_state(Tallking_gpt.msg)

@chat_gpt_router.message(Tallking_gpt.msg, flags={"rate_limit": 5.5})
async def gpt_bot_tallking(message: Message, state: FSMContext):
    if await check_user_delay(message.from_user.id) and message.text:
        msg = await message.answer("<i>Подождите...</i>")
        data = await state.get_data()
        data = data.get("msg", None)
        try:
            response = await get_chat_completion_cons(message=message)
            await msg.delete()
            await message.answer(text=response, reply_markup=gpt_kb(message.from_user.id), parse_mode="Markdown")
            await state.set_state(Tallking_gpt.msg)
        except Exception as e:
            logger.info(e)
            await state.clear()
            await message.answer("<b> Увы, консультант временно не досутпен</b>")
            await message.answer(
                f"👋 Приветствуем, {message.from_user.full_name}! Вы находитесь в боте 'Прием заявок', выберите необходимое действие.",
                reply_markup=main_user_kb(message.from_user.id)
            )
    else:
        await message.answer("<b>Не спамьте! </b>")