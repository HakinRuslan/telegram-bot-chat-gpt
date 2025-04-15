from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserBaseInDB(BaseModel):
    telegram_id: int

    
    model_config = ConfigDict(from_attributes=True)

class User(UserBaseInDB):
    username: Optional[str]

class Userapl(UserBaseInDB):
    username: Optional[str]
    fio: str
    number: int

class AplicationModel(BaseModel):
    time: str
    addres: str = Field(..., description="Адрес с заявки")
    source: str = Field(..., description="Источник оформления заявки")
    user_id: int = Field(..., description="ID пользователя Telegram")
    active: bool
    quantity: int
    det_id: Optional[int] = Field(None, description="ID подробностей о заявке")

class AplicationDetailsIDModel(BaseModel):
    id: int

class AplicationActiveModel(BaseModel):
    active: bool

class AplicationAdressModel(BaseModel):
    addres: str

# class AplicationActiveModel(BaseModel):
#     user_id: int
#     active: bool

class DetailsAboutApl(BaseModel):
    extra_services: Optional[list] = Field(None)
    carpet_area: Optional[list] = Field(None)
    material: Optional[list] = Field(None)
    availability_dmg: Optional[list] = Field(None)

# class TariffIDModel(BaseModel):
#     id: int

# class TypeoftariffIDModel(BaseModel):
#     type_of_tarrifs_id: int

# class Payment_user_id(BaseModel):
#     user_id: int = Field(..., description="ID пользователя Telegram")

# class PaymentData(BaseModel):
#     user_id: int = Field(..., description="ID пользователя Telegram")
#     payment_id: str = Field(..., max_length=255, description="Уникальный ID платежа")
#     active: bool
#     price: int = Field(..., description="Сумма платежа в рублях")
#     tariff_id: int = Field(..., description="ID товара")

# class ProductModel(BaseModel):
#     name: str = Field(..., min_length=5)
#     description: str = Field(..., min_length=5)
#     price: int = Field(..., gt=0)
#     type_of_tarrifs_id: int = Field(..., gt=0)
 