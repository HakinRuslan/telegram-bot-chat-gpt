from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from ..database.database import get_async_session, session_maker
import time
from loguru import logger


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, delay: int):
        self.delay = delay
        self.last_message_time = {}

    async def __call__(self, handler, event, data):
        user_id = None
        
        # Проверяем, откуда пришел update и есть ли там from_user
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        elif hasattr(event, "from_user"):  # На случай других типов
            user_id = event.from_user.id

        # Если user_id не определен, просто пропускаем обработку
        if user_id is None:
            logger.info("не определен")
            return await handler(event, data)

        now = time.time()

        # Проверяем ограничение по времени
        if user_id in self.last_message_time and now - self.last_message_time[user_id] < self.delay:
            logger.info("сработало ограничение на спам")
            return await event.answer("⏳ Подожди немного перед следующим сообщением!")

        self.last_message_time[user_id] = now
        return await handler(event, data)
class DBMiddleware(BaseMiddleware):
    async def __call__(
        self,
        hanlder: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        async with session_maker() as session:
            self.set_session(data, session)
            try:
                result = await hanlder(event, data)
                await self.after_handler(session)
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    def set_session(self, data: Dict[str, Any], session) -> None:
        raise NotImplementedError("Этот метод должен быть реализован в подклассах.")

    async def after_handler(self, session) -> None:
        pass

class DBMiddlewareWithComm(DBMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
        print("commit")
        await session.commit()


class DBMiddlewareWithoutComm(DBMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_without_commit'] = session

