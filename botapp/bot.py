import logging
from config import settings
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis
from openai import OpenAI, Client, AsyncOpenAI


redis = Redis(host=settings.host_redis, port=settings.port_redis, password = settings.password_redis, db=0, decode_responses=True)
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
client_gpt = AsyncOpenAI(api_key=settings.openai_api_key)
storage = RedisStorage(redis)

models = client_gpt.models.list()  # Получаем список моделей

logger.info(models)

bot = Bot(token=settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=storage)