from typing import Union

from pydantic import BaseModel, Field


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
    category_id: CategoryScheme
    unit_id: UnitScheme
    price: float


class ProductAddScheme(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    unit: int
    category: int


class ProductUpdateScheme(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[int, None] = None


class OrderScheme(BaseModel):
    product_id: int
    quantity: int = 1


