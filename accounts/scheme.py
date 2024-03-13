from datetime import datetime, date
from typing import Union

from pydantic import BaseModel, Field

from warehouse.scheme import WarehouseGetScheme


class RegisterScheme(BaseModel):
    firstname: str
    lastname: str
    login: str
    email: str
    phone_number: str
    warehouse_id: int
    shift_id: int
    password1: str = Field(min_length=8)
    password2: str = Field(min_length=8)


class ShiftScheme(BaseModel):
    id: int
    name: str


class UserInfoScheme(BaseModel):
    login: str
    firstname: str
    lastname: str
    email: str
    phone: str
    last_updated: datetime
    warehouse: Union[WarehouseGetScheme, None]
    shift: Union[ShiftScheme, None]


class LoginScheme(BaseModel):
    login: str
    password: str = Field(min_length=8)


class CostumerAddScheme(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: str
