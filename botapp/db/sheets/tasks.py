
from datetime import datetime
from aiogram.types import ChatMember
from loguru import logger
from .build import *
from db import *


def add_record_to_google_sheets(sheet, new_record):
    try:
        sheet.append_row(new_record)
    except Exception as e:
        logger.info(f"Ошибка при добавлении записи в Google Sheets: {e}")

def change_type(value_of_the_record):
    if isinstance(value_of_the_record, list):
        return ", ".join(map(str, value_of_the_record))
    return str(value_of_the_record)

def add_apl_to_google_sheets(sheet, new_record):
    new_record = [change_type(value) for value in new_record]
    try:
        sheet.append_row(new_record)
    except Exception as e:
        logger.info(f"Ошибка при добавлении записи в Google Sheets: {e}")

def increase_value_in_google_sheets(sheet, search_value, column_to_search, column_to_update):
    try:
        cell = sheet.find(str(search_value), in_column=column_to_search)
        if cell:
            row_number = cell.row
            current_value = sheet.cell(row_number, column_to_update).value
            new_value = int(current_value or 0) + 1
            sheet.update_cell(row_number, column_to_update, new_value)
    except Exception as e:
        logger.error(f"Ошибка при увелечении кол-ва заявок: {e}")


def update_sheets(sheet, search_value, column_to_search, new_value, column_to_update):
    try:
        cell = sheet.find(str(search_value), in_column=column_to_search)

        if cell:
            sheet.update_cell(cell.row, column_to_update, new_value)
            logger.info(f"Запись обновлена в строке {cell.row}")
        else:
            logger.warning("Значение не найдено")
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении записи: {e}")


def delete_record_in_google_sheets(sheet, search_value, column_to_search):
    try:
        cell = sheet.find(str(search_value), in_column=column_to_search)
        sheet.delete_rows(cell.row)
        logger.info(f"Запись удалена в строке {cell.row}")
    
    except Exception as e:
        logger.info("Запись в строках по переданным параметрам, была не найдена")
        logger.error(f"Ошибка при удалении записи: {e}")

