from datetime import datetime, date
from typing import Union, List

from pydantic import BaseModel, Field

from accounts.scheme import UserInfoScheme


class UnitScheme(BaseModel):
    id: int
    code: str
    name: str


class CategoryScheme(BaseModel):
    id: int
    name: str
    description: str


class CategoryAddScheme(BaseModel):
    name: str
    description: str


class ProductGetScheme(BaseModel):
    id: int
    name: str
    description: str
    category: CategoryScheme
    unit: UnitScheme
    price: float


class ProductAddScheme(BaseModel):
    name: str
    description: str
    price: float = Field(gte=0)
    unit: int = Field(gt=0)
    category: int = Field(gt=0)


class ProductUpdateScheme(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[int, None] = None


class OrderScheme(BaseModel):
    product_id: int
    quantity: int = 1


class CompositeAddScheme(BaseModel):
    equipment_id: int
    resource_id: int
    resource_amount: float


class EndProcessScheme(BaseModel):
    product_id: int
    product_amount: int


class GetOrdersScheme(BaseModel):
    id: int
    user: UserInfoScheme
    paid: float
    total_price: float
    is_active: bool
    orders: List[OrderScheme]