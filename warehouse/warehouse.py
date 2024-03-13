from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from database import get_async_session
from market.scheme import ProductGetScheme
from models.models import Warehouse, WarehouseType, Product, ProductLocation, Category, Unit, ProductHistory

from .scheme import WarehouseGetScheme, WarehouseAddScheme, ProductLocationAddScheme, ProductLocationGetScheme, \
    UpdatePLScheme, WarehouseProductScheme, CategoriesScheme, HistoryGetScheme

warehouse_router = APIRouter()


@warehouse_router.get("/warehouses", response_model=List[WarehouseGetScheme])
async def get_warehouses(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Warehouse).order_by(Warehouse.id)
    data = await session.execute(query)
    warehouses = data.scalars().all()
    return warehouses


@warehouse_router.post("/create_warehouse")
async def create_warehouse(
        warehouse: WarehouseAddScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(Warehouse).values(**warehouse.dict())
    await session.execute(query)
    await session.commit()
    return {'success': True, **warehouse.dict()}


@warehouse_router.post("/connect-warehouse_type")
async def connect_warehouse_type(
    warehouse_id: int,
    categories: List[CategoriesScheme],
    session: AsyncSession = Depends(get_async_session)
):
    try:
        for category in categories:
            cat_data = session.get(Category, category)
            await session.commit()
            if cat_data:
                query = insert(WarehouseType).values(warehouse_id=warehouse_id, category_id=category.category)
                await session.execute(query)
                await session.commit()
            else:
                raise HTTPException(status_code=400, detail="Category does not exist")
        return {'success': True, 'message': 'Warehouse type has been added'}
    except HTTPException as e:
        raise {'success': False, 'message': 'Warehouse type could not be added'}


@warehouse_router.post("/add-product_location")
async def add_product_location(
    product_locations: ProductLocationAddScheme,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(ProductLocation).where(
        ProductLocation.product_id == product_locations.product_id and
        ProductLocation.warehouse_id == product_locations.warehouse_id
    )
    data = await session.execute(query)
    product_l = data.scalars().first()
    if product_l is None:
        query = insert(ProductLocation).values(**product_locations.dict())
        await session.execute(query)
    else:
        await session.execute(update(ProductLocation).where(ProductLocation.id == product_l.id).values(product_amount=product_locations.product_amount))
    await session.commit()
    return {'success': True, 'message': 'Product location has been added'}


@warehouse_router.get('/product_locations', response_model=List[ProductLocationGetScheme])
async def get_product_locations(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(ProductLocation).order_by(ProductLocation.warehouse_id)
    data = await session.execute(query)
    return data.scalars().all()


@warehouse_router.get('/product_locations/{id}', response_model=List[ProductLocationGetScheme])
async def get_product_location(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(ProductLocation).where(ProductLocation.product_id == product_id)
    data = await session.execute(query)
    return data.scalars().all()


@warehouse_router.patch("/update-product_location")
async def update_product_location(
        data: UpdatePLScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query_new = select(ProductLocation).where(
        (ProductLocation.product_id == data.product_id) and
        (ProductLocation.warehouse_id == data.warehouse_new_id)
    )
    new_loc = await session.execute(query_new)
    new_loc_data = new_loc.scalars().first()
    try:
        query_old = select(ProductLocation).where(
            (ProductLocation.warehouse_id == data.warehouse_old_id) and (ProductLocation.product_id == data.product_id)
        )
        old_loc = await session.execute(query_old)
        old_loc_data = old_loc.scalars().first()
    except IntegrityError as e:
        old_loc_data = None
        raise
    is_changed = False
    print(new_loc_data)
    print(old_loc_data.product_amount)
    if not new_loc_data and old_loc_data and old_loc_data.product_amount >= data.amount:
        await session.execute(insert(ProductLocation).values(
            warehouse_id=data.warehouse_new_id,
            product_id=data.product_id,
            product_amount=data.amount
        ))
        query1 = update(ProductLocation).where(
            ProductLocation.id == old_loc_data.id and ProductLocation.product_id == data.product_id).values(
            product_amount=int(old_loc_data.product_amount - data.amount))
        await session.execute(query1)
        await session.commit()
        is_changed = True
    elif new_loc_data and old_loc_data.product_amount >= data.amount:
        query1 = update(ProductLocation).where(ProductLocation.id == old_loc_data.id and ProductLocation.product_id==data.product_id).values(product_amount=int(old_loc_data.product_amount - data.amount))
        await session.execute(query1)
        query2 = update(ProductLocation).where(ProductLocation.id == new_loc_data.id and ProductLocation.product_id==data.product_id).values(product_amount=int(data.amount + new_loc_data.product_amount))
        await session.execute(query2)
        await session.commit()
        is_changed = True

    else:
        raise HTTPException(status_code=400, detail='Bad Request')

    if is_changed:
        query3 = insert(ProductHistory).values(**data.dict())
        await session.execute(query3)
        await session.commit()
        return {'success': True, 'message': 'Product location has been updated'}


@warehouse_router.get('/warehouse_products', response_model=List[WarehouseProductScheme])
async def get_warehouse_products(
        warehouse_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(ProductLocation).where(ProductLocation.warehouse_id == warehouse_id)
    data = await session.execute(query)
    loc_data = data.scalars().all()
    product_list = []
    for loc in loc_data:
        query = select(Product).where(Product.id == loc.product_id)
        product = await session.execute(query)
        data = product.scalars().first()
        data.amount = loc.product_amount
        product_list.append(data)
    return product_list


@warehouse_router.get('/history', response_model=List[HistoryGetScheme])
async def get_history(
        session: AsyncSession = Depends(get_async_session)
):
    query = select(ProductHistory).options(selectinload(ProductHistory.product)).order_by(ProductHistory.product_id)
    data = await session.execute(query)
    lis = data.scalars().all()
    return lis


# @warehouse_router.post('/history')


