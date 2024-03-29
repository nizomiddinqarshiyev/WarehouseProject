from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class WarehouseGetScheme(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float


class WarehouseAddScheme(BaseModel):
    name: str
    latitude: float
    longitude: float


class ProductLocationAddScheme(BaseModel):
    product_id: int
    warehouse_id: int
    product_amount: int


class ProductLocationGetScheme(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    product_amount: int


class UpdatePLScheme(BaseModel):
    warehouse_old_id: int
    product_id: int
    warehouse_new_id: int
    amount: int = Field(gt=0)


class WarehouseProductScheme(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    amount: int = Field(gte=0)
    unit_id: int
    price: float


class CategoriesScheme(BaseModel):
    category: int = Field(lt=4, gte=1)


class ProductScheme(BaseModel):
    id: int
    name: str
    description: str
    price: float


class HistoryGetScheme(BaseModel):
    id: int
    warehouse_old_id: int
    product: ProductScheme
    warehouse_new_id: int
    amount: int = Field(gte=0)
    last_update: datetime


class ResourceGetScheme(BaseModel):
    id: int
    name: str
    description: str


class WarehouseResource(BaseModel):
    id: int
    resource: ResourceGetScheme
    amount: float


class WarehouseResourceScheme(BaseModel):
    id: int
    resource: ResourceGetScheme
    warehouse: WarehouseGetScheme
    amount: float



