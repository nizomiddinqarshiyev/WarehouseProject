from datetime import datetime
from typing import List
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import select, update, insert, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import session,
import asyncio
import sys
from typing import Callable, Any, Awaitable, TypeVar

from greenlet import getcurrent, greenlet

from sqlalchemy import extract
from accounts.utils import verify_token
from database import get_async_session
from market.scheme import ProductGetScheme, ProductAddScheme, ProductUpdateScheme, CategoryScheme, CategoryAddScheme, \
    OrderScheme
from models.models import *
from permissions import permission

market_router = APIRouter()


@market_router.get("/get_products")
async def get_all_products(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Product)
    product_data = await session.execute(query)
    product__data = product_data.scalars().all()
    lis = []
    for product in product__data:
        unit_query = select(Unit).where(Unit.id == product.unit_id)
        units = await session.execute(unit_query)
        unit__data = units.scalars().one()
        cat_query = select(Category).where(Category.id == product.category_id)
        category = await session.execute(cat_query)
        category__data = category.scalars().one()
        lis.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category': {
                'id': category__data.id,
                'name': category__data.name,
                'description': category__data.description
            },
            'unit': {
                'id': unit__data.id,
                'name': unit__data.name,
                'code': unit__data.code,
            },
            'price': product.price

        })
    return lis


@market_router.get('/product/{product_id}')
async def get_product(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Product).where(Product.id == product_id)
    product_data = await session.execute(query)
    product = product_data.scalars().first()
    if product:
        unit_query = select(Unit).where(Unit.id == product.unit_id)
        units = await session.execute(unit_query)
        unit__data = units.scalars().one()
        cat_query = select(Category).where(Category.id == product.category_id)
        category = await session.execute(cat_query)
        category__data = category.scalars().one()
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category': {
                'id': category__data.id,
                'name': category__data.name,
                'description': category__data.description
            },
            'unit': {
                'id': unit__data.id,
                'name': unit__data.name,
                'code': unit__data.code,
            },
            'price': product.price
        }
        return data
    else:
        raise HTTPException(status_code=400, detail='Product does not exist')


@market_router.get('/sort-by-category')
async def sort_by_category(
        category_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    category_query = select(Product).where(Product.id == category_id)
    products = await session.execute(category_query)
    product_data = products.scalars().all()
    if product_data:
        return product_data
    else:
        raise HTTPException(status_code=400, detail='Products does not exist')


@market_router.post("/add-product")
async def add_product(
        product_data: ProductAddScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)

):
    if await permission(token['user_id'], session, ['admin', 'boss']):
        query = insert(Product).values(**product_data.dict())
        await session.execute(query)
        await session.commit()
        return {'success': True, 'message': 'Product added successfully'}
    else:
        return {'success': False, 'message': 'Permission denied'}


@market_router.patch("/update-product/id")
async def update_product(
        product_id: int,
        product_new: ProductUpdateScheme,
        session: AsyncSession = Depends(get_async_session)
):
    # db_item = await session.get(Product, product_id)
    # print(product_new.name, product_new.price, product_new.description)
    # if product_new.name:
    #     db_item.name = product_new.name
    #     await session.commit()
    # elif product_new.description:
    #     db_item.description = product_new.description
    #     await session.commit()
    # elif product_new.price:
    #     db_item.price = product_new.price
    #     await session.commit()
    product_query = select(Product).where(Product.id == product_id)
    product = await session.execute(product_query)
    dic = {}
    for new_data_key, new_data_val in product_new.dict().items():
        if new_data_val:
            dic[new_data_key] = new_data_val
    if product:
        query = update(Product).where(Product.id == product_id).values(**dic)
        data = await session.execute(query)
    else:
        raise HTTPException(status_code=400, detail="Product cannot be updated")
    # db_item.last_updated = datetime.now()
    await session.commit()
    return {'success': True, 'message': 'Product updated'}


@market_router.delete("/delete-product/id")
async def delete_product(
        pk: int,
        session: AsyncSession = Depends(get_async_session)
):
    existing_product = await session.get(Product, pk)
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(existing_product)
    await session.commit()
    return {'success': True, 'message': 'Product deleted'}


@market_router.get("/categories", response_model=List[CategoryScheme])
async def list_categories(
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Category)
    category = await session.execute(query)
    category_data = category.scalars().all()
    return category_data


@market_router.post("/add-category")
async def add_category(
        category: CategoryAddScheme,
        # token:dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(Category).values(**category.dict())
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': 'Category'}


# @market_router.delete("/remove-category/id")
# async def remove_category(
#         category_id: int,
#         # token: dict = Depends(verify_token),
#         session: AsyncSession = Depends(get_async_session)
# ):
#     existing_category = await session.get(Category, category_id)
#     if existing_category is None:
#         raise HTTPException(status_code=404, detail="Category not found")
#     await session.delete(existing_category)
#     await session.commit()
#     return {'success': True, 'message': 'Category deleted'}


@market_router.post("/create-oder")
async def create_oder(
        costumer_id: int,
        paid: float,
        products: List[OrderScheme],
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    product_list = []
    total_price = 0
    for product in products:
        query_product = select(Product).where(Product.id == product.product_id)
        product_data = await session.execute(query_product)
        product__data = product_data.scalars().one()
        product_list.append(product__data)
        total_price += product__data.price*product.quantity
    if product_list:
        query = insert(OrderDetail).values(
            user_id=token['user_id'],
            costumer=costumer_id,
            total_price=total_price, paid=paid,
            created_at=datetime.now()
        )
        await session.execute(query)
        await session.commit()
        order_query = select(OrderDetail).where(
            (OrderDetail.user_id == token['user_id']) &
            (OrderDetail.costumer == costumer_id))
        order = await session.execute(order_query)
        order_data = order.scalars().all()
        for product in products:
            query = insert(Order).values(
                product_id=product.product_id,
                count=product.quantity,
                order_detail_id=order_data[-1].id
            )
            await session.execute(query)
            await session.commit()
        return {'success': True, 'message': 'Order successfully created'}
    else:
        raise HTTPException(status_code=400, detail='No result found')


@market_router.get('/client-orders/')
async def client_order(
        costumer_id=int,
        session: AsyncSession = Depends(get_async_session)
):
    query_orders = select(OrderDetail).where(OrderDetail.costumer == costumer_id)
    orders = await session.execute(query_orders)
    order_details = orders.scalars().all()
    print(order_details)
    order_list = []
    for order_detail in order_details:
        query = select(Order).where(Order.order_detail_id == order_detail.id)
        order_data = await session.execute(query)
        orders = order_data.scalars().all()
        product_list = []
        for order in orders:
            product_list.append({
                'product_id': order.product_id,
                'count': order.count
            })
        order_list.append({
            'id': order_detail.id,
            'paid': order_detail.paid,
            'consumer_id': order_detail.user_id,
            'total_price': order_detail.total_price,
            'created_at': order_detail.created_at,
            'is_active': order_detail.is_active,
            'products': product_list
        })

    return order_list




