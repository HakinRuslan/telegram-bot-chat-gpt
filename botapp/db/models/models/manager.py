from db.basemodel.basedao import *
from ..ormmodels.models import *
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case, desc
from typing import Optional, Tuple, Dict
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, UTC
import pytz

# class TicketDAO(BaseDAO[Ticket]):
#     model = Ticket

class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_apls_statistics(cls, session: AsyncSession, telegram_id: int) -> Optional[Dict[str, int]]:
        try:
            # Запрос для получения общего числа покупок и общей суммы
            result = await session.execute(
                select(
                    func.count(Application.id).label('total_apls'),
                    func.count().filter(Application.active == True).label('total_active_apls')
                )
                .join(Application,User.telegram_id == Application.user_id)
                .filter(User.telegram_id == telegram_id)
            )
            stats = result.one_or_none()

            if stats is None:
                return None

            total_apls, total_active_apls = stats
            return {
                'total_apls': total_apls or 0,
                'total_active_apls': total_active_apls or 0  # Обработка случая, когда сумма может быть None
            }

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            logger.info(f"Ошибка при получении статистики заявок пользователя: {e}")
            return None
        
    @classmethod
    async def get_statistics(cls, session: AsyncSession):
        try:
            now = datetime.now(pytz.UTC).replace(tzinfo=None)

            query = select(
                func.count().label('total_users'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=1), 1), else_=0)).label('new_today'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=7), 1), else_=0)).label('new_week'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=30), 1), else_=0)).label('new_month')
            )

            result = await session.execute(query)
            stats = result.fetchone()

            statistics = {
                'total_users': stats.total_users,
                'new_today': stats.new_today,
                'new_week': stats.new_week,
                'new_month': stats.new_month
            }

            logger.info(f"Статистика успешно получена: {statistics}")
            return statistics
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            raise

    @classmethod
    async def get_apls(cls, session: AsyncSession, telegram_id: int) -> Optional[List[Application]]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.applications).selectinload(Application.apl_details)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None
            return user.applications

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о заявках пользователя: {e}")
            return None   

    @classmethod
    async def get_apls_active(cls, session: AsyncSession, telegram_id: int) -> Optional[List[Application]]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.applications).selectinload(Application.apl_details)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None
            active_applications = [apl for apl in user.applications if apl.active]
            return active_applications if active_applications else None


        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о заявках пользователя: {e}")
            return None         

    
    @classmethod
    async def find_apls_of_users(cls, session: AsyncSession, telegram_id: int) -> Optional[User]:
        try:
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.applications).selectinload(Application.apl_details)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None
            return user

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о заявках пользователя: {e}")
            return None   
     
        

    # @classmethod
    # async def update_user(cls, session: AsyncSession, record_id: int, values: BaseModel):
    #     values_dict = values.model_dump(exclude_unset=True)
    #     logger.info(f"Обновление записи {cls.model.__name__} с параметрами: {values_dict}")
        
    #     try:
            
    #         query = select(cls.model).filter_by(telegram_id=record_id)
    #         result = await session.execute(query)
    #         record = result.scalar_one_or_none()

    #         if not record:
    #             logger.info(f"Запись с id={record_id} не найдена")
    #             return None

    #         for key, value in values_dict.items():
    #             setattr(record, key, value)

    #         await session.flush()

    #         logger.info(f"Запись {cls.model.__name__} успешно обновлена")
    #         return record

    #     except SQLAlchemyError as e:
    #         await session.rollback()
    #         logger.error(f"Ошибка при обновлении записи: {e}")
    #         raise e   


class DetailsAplDAO(BaseDAO[Details_apl]):
    model = Details_apl


class ApplicationsDao(BaseDAO[Application]):
    model = Application


    @classmethod
    async def get_apls_and_details_by_id(cls, session: AsyncSession, data_id: int) -> Optional[Application]:
        try:
            # Запрос для получения пользователя с его покупками и связанными продуктами
            result = await session.execute(
                select(Application)
                .options(
                    selectinload(Application.apl_details)
                )
                .filter(Application.id == data_id)
            )
            apl = result.scalar_one_or_none()

            if apl is None:
                return None
            return apl

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f"Ошибка при получении информации о заявках пользователя: {e}")
            return None   

    # @classmethod
    # async def get_full_summ(cls, session: AsyncSession) -> int:
    #     """Получить общую сумму покупок."""
    #     query = select(func.sum(cls.model.price).label('total_price'))
    #     result = await session.execute(query)
    #     total_price = result.scalars().one_or_none()
    #     return total_price if total_price is not None else 0
    
    # @classmethod
    # async def get_latest_active_purchase(
    #     cls, session: AsyncSession, user_id: int
    # ) -> Optional["Purchase"]:
    #     try:
    #         result = await session.execute(
    #             select(cls.model)
    #             .join(User)
    #             .options(selectinload(cls.model.tariff))
    #             .filter(User.id == user_id, cls.model.active.is_(True))
    #             .order_by(desc(cls.model.created_at))
    #             .limit(1)
    #         )
    #         purch = result.scalar_one_or_none()
        
    #         if purch is None:
    #             return None
                
    #         return purch

    #     except SQLAlchemyError as e:
    #         print(f"Ошибка при получении активной последней покупки: {e}")
    #         return None