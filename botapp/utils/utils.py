import asyncio
from aiogram.types import ContentType
from admin.kbs import *
from config import *
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger
from bot import bot
from user.kbs import *
import time
import re
from bot import redis
import os
import uuid
from datetime import datetime, timedelta
from gpt_talking.fn_utils import *

async def generate_short_link(data: str) -> str:
    """Генерируем короткий ID и сохраняем данные"""
    short_id = str(uuid.uuid4())[:8]
    await redis.setex(f"tg_msg_client:{short_id}", 18000, data)
    return f"https://t.me/ur_guide_in_wash_the_carpet_bot?start={short_id}"

async def get_thread_id(user_id, client) -> str:
    thread_id = await redis.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id

    thread = await client.beta.threads.create()
    await redis.setex(f"user:{user_id}:thread_id", 18000, thread.id)

    return thread.id


async def get_data_from_redis(redis_id_key_for_incoming_message: str) -> str:
    """Получаем данные по короткому ID"""
    return await redis.get(f"tg_msg_client:{redis_id_key_for_incoming_message}")

async def delete_keys_with_data_from_redis(redis_id_key_for_incoming_message: str):
    """Удаляем ключ со значением по короткому ID"""
    await redis.delete(f"tg_msg_client:{redis_id_key_for_incoming_message}")


def is_valid_international_phone_number(text: str) -> bool:
    """Проверяет, является ли номер международным (начинается с + и содержит от 10 до 15 цифр)."""
    return bool(re.fullmatch(r'\+?\d{1,4}(\d{10,15})', text))

def is_only_letters(text: str) -> bool:
    """Проверяет, что строка содержит только буквы (без цифр и символов)."""
    return bool(re.fullmatch(r'[А-Яа-яA-Za-z]+', text))

def validate_length(text: str) -> bool:
    """Проверяет, содержит ли строка не более 5 символов."""
    return len(text) >= 5

def validate_time_format(text: str) -> bool:
    """Проверяет, соответствует ли строка формату 'HH:MM - HH:MM' или 'HH:MM-HH:MM'."""
    return bool(re.fullmatch(r'\d{2}:\d{2}\s?-\s?\d{2}:\d{2}', text))

def contains_whitespace(text: str) -> bool:
    """Проверяет, содержит ли строка пробельные символы (пробелы, табуляции, переводы строк и т. д.)."""
    return bool(re.search(r'\s', text))

def validate_input(text: str) -> bool:
    """Проверяет, соответствует ли строка формату {число}м."""
    return bool(re.fullmatch(r'\d+[мm]', text))

def format_date_russian(date_input) -> str:
    months = {
        1: "январе", 2: "феврале", 3: "марте", 4: "апреле", 5: "мае", 6: "июне",
        7: "июле", 8: "августе", 9: "сентябре", 10: "октябре", 11: "ноябре", 12: "декабре"
    }
    if isinstance(date_input, str):
        date_obj = datetime.strptime(date_input, "%d/%m/%y")
    elif isinstance(date_input, datetime):
        date_obj = date_input
    else:
        raise ValueError("Дата должна быть строкой формата 'DD/MM/YY' или объектом datetime")

    month_name = months[date_obj.month]
    year = date_obj.year

    return f"{month_name} {year} года"


def format_date(date: datetime) -> str:
    return date.strftime('%d/%m/%y')

def format_date_russian(date_input) -> str:
    months = {
        1: "январе", 2: "феврале", 3: "марте", 4: "апреле", 5: "мае", 6: "июне",
        7: "июле", 8: "августе", 9: "сентябре", 10: "октябре", 11: "ноябре", 12: "декабре"
    }
    logger.info(type(date_input))
    if isinstance(date_input, str):
        date_obj = datetime.strptime(date_input, "%d/%m/%y")
    elif isinstance(date_input, datetime):
        date_obj = date_input
    else:
        raise ValueError("Дата должна быть строкой формата 'DD/MM/YY' или объектом datetime")

    month_name = months[date_obj.month]
    year = date_obj.year

    return f"{month_name} {year} года"


def contains_spaces(text: str) -> bool:
    return bool(re.fullmatch(r'[А-Яа-яёЁ ]+', text)) and ' ' in text


def contains_spaces(text: str) -> bool:
    return ' ' in text

def how_much(days: int) -> str:
    if not isinstance(days, int) or days <= 0:
        raise ValueError("Количество дней должно быть положительным целым числом")
    
    end_date = datetime.now() + timedelta(days=days)
    return end_date.strftime('%d/%m/%y')


def how_much_ago(date):
    now = datetime.now()
    delta = now - date
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} секунд назад"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} минут назад" if minutes > 1 else "1 минута назад"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} часа назад" if hours > 1 else "1 час назад"
    elif seconds < 2592000:
        days = int(seconds // 86400)
        return f"{days} д назад" if days > 1 else "1 д назад"
    elif seconds < 31536000:
        months = int(seconds // 2592000)
        return f"{months} мес назад" if months > 1 else "1 мес назад"
    else:
        years = int(seconds // 31536000)


async def process_dell_text_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Ошибка: Не удалось найти идентификатор последнего сообщения для удаления.")
        await message.delete()

    except Exception as e:
        logger.error(f"Произошла ошибка при удалении сообщения: {str(e)}")



def validate_birth_date(date_text):
    try:
        current_year = datetime.now().year
        date_str = f"{date_text}/{current_year}"
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# def validate_residence(residence_text):
#     return len(residence_text.strip()) > 0 


# def validate_email(email_text):
#     email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#     return re.match(email_regex, email_text) is not None


# def validate_phone(phone_text):
#     phone_regex = r'^\+?\d{1,3}?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
#     return re.match(phone_regex, phone_text) is not None


# def validate_text(text):
#     return len(text.strip()) > 0



async def process_dell_text_msg(message: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')
    logger.info(last_msg_id)

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Ошибка: Не удалось найти идентификатор последнего сообщения для удаления.")
        logger.info(True)
        await message.delete()

    except Exception as e:
        logger.error(f"Произошла ошибка при удалении сообщения: {str(e)}")