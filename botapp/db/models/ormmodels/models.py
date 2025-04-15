from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, String, ARRAY
from db.database.database import Base
import datetime


class Details_apl(Base):
    __tablename__ = 'apl_details'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    extra_services: Mapped[List[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    carpet_area: Mapped[List[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    material: Mapped[List[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    availability_dmg: Mapped[List[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    applications: Mapped["Application"] = relationship("Application", back_populates="apl_details")

    def __repr__(self):
        return f"<Details_apl(id={self.id}, carpet_area={self.carpet_area}, date={self.created_at})>"

class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str]
    fio: Mapped[str | None]
    number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    applications: Mapped[List["Application"]] = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self): 
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
    
# class Ticket(Base):
#     __tablename__ = 'tickets'

#     tg_id_client: Mapped[int] = mapped_column(BigInteger, nullable=False)
#     msg_client: Mapped[str | None]
#     msg_operator: Mapped[str | None]

#     def __repr__(self): 
#         return f"<Ticket(id={self.id}, client_msg={self.msg_client}, operator_msg='{self.msg_operator}')>"
    
class Application(Base):
    __tablename__ = 'applications'
    
    quantity: Mapped[int]
    time:  Mapped[str]
    addres: Mapped[str]
    source: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    user: Mapped["User"] = relationship("User", back_populates="applications")
    active: Mapped[bool]
    det_id: Mapped[int | None] = mapped_column(ForeignKey('apl_details.id'))
    apl_details: Mapped["Details_apl"] = relationship("Details_apl", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, active={self.active}, data={self.created_at}, time={self.time})>"
    
