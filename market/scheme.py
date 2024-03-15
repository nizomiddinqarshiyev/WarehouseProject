from datetime import datetime, date
from typing import Union, List

from pydantic import BaseModel, Field

from accounts.scheme import UserInfoScheme


class UnitScheme(BaseModel):
    id: int
    code: str
    name: str


class UnitAddScheme(BaseModel):
    name: str
    code: str


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


class ResourceScheme(BaseModel):
    id: int
    name: str
    description: str
    unit_id: int


class EmployeeScheme(BaseModel):
    id: int
    login: str
    firstname: str
    lastname: str
    email: str
    phone: str
    last_updated: datetime
    warehouse_id: int
    shift_id: int


class ProductScheme(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    unit_id: int
    price: float


class GetOrdersScheme(BaseModel):
    id: int
    user: UserInfoScheme
    paid: float
    total_price: float
    is_active: bool
    orders: List[OrderScheme]


class ReportGetScheme(BaseModel):
    id: int
    product: Union[ProductScheme, None]
    product_amount: Union[int, None]
    employee: EmployeeScheme
    resource: ResourceScheme
    resource_amount: float
    start_at: datetime
    end_at: Union[datetime, None]


class ResourceGetScheme(BaseModel):
    id: int
    name: str
    description: str
    unit: UnitScheme


class ResourceAddScheme(BaseModel):
    name: str
    description: str
    unit_id: int


class CreateRecipeScheme(BaseModel):
    resource_id: int
    amount: float


class GetRecipeScheme(BaseModel):
    product: ProductScheme
    resource: List[ResourceScheme]
    amount: float



















