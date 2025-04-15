from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

# class TariffTypeIDModel(BaseModel):
#     id: int

class UserBaseInDB(BaseModel):
    telegram_id: int

    
    model_config = ConfigDict(from_attributes=True)

class Usersch(UserBaseInDB):
    username: str

class Userapl(UserBaseInDB):
    username: Optional[str]
    fio: str
    number: int

class AplicationDetailsIDModel(BaseModel):
    id: int

class AplicationActiveModel(BaseModel):
    active: bool

class TicketOperator(BaseModel):
    tg_id_client: int

class TicketClient(BaseModel):
    tg_id_client: int

class Ticketadd(BaseModel):
    tg_id_client: Optional[int] = Field(None)
    msg_client: Optional[str] = Field(None)
    msg_operator: Optional[str] = Field(None)


# class User_upd_active(BaseModel):
#     active: bool


# class TypetariffModelUpd(BaseModel):
#     type_tarif_name: Optional[str] = Field(None, min_length=5)
#     how_much_days: Optional[int] = None

# class TarifftModelUpd(BaseModel):
#     name: Optional[str] = Field(None, min_length=5)
#     description: Optional[str] = Field(None, min_length=5)
#     price: Optional[int] = Field(None, gt=0)
#     type_of_tarrifs_id: Optional[int] = Field(None, gt=0)

# class TypetariffModel(BaseModel):
#     type_tarif_name: str = Field(..., min_length=5)
#     how_much_days: int

# class TarifftModel(BaseModel):
#     name: str = Field(..., min_length=5)
#     description: str = Field(..., min_length=5)
#     price: int = Field(..., gt=0)
#     type_of_tarrifs_id: int = Field(..., gt=0)

# class PaymentData(BaseModel):
#     user_id: int = Field(..., description="ID пользователя Telegram")
#     payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
#     active: bool
#     price: int = Field(..., description="Сумма платежа в рублях")
#     tariff_id: int = Field(..., description="ID товара")