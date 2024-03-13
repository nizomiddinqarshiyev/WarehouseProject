from datetime import datetime
from typing import List
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from accounts.utils import verify_token
from database import get_async_session
from market.scheme import ProductGetScheme, ProductAddScheme, ProductUpdateScheme, CategoryScheme, CategoryAddScheme, \
    OrderScheme, CompositeAddScheme, EndProcessScheme
from models.models import *
from permissions import permission

market_router = APIRouter()


@market_router.get("/get_products", response_model=List[ProductGetScheme])
async def get_all_products(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Product).options(selectinload(Product.category), selectinload(Product.unit)).order_by(Product.id)
    result = await session.execute(query)
    data = result.scalars().all()
    return data


@market_router.get('/product/{product_id}', response_model=ProductGetScheme)
async def get_product(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Product).options(selectinload(Product.category), selectinload(Product.unit)).where(Product.id == product_id)
    product_data = await session.execute(query)
    product = product_data.scalars().first()
    if product:
        return product
    else:
        raise HTTPException(status_code=400, detail='Product does not exist')


@market_router.get('/sort-by-category', response_model=List[ProductGetScheme])
async def sort_by_category(
        category_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    category_query = select(Product).options(selectinload(Product.category), selectinload(Product.unit)).where(Product.category_id == category_id)
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
        query1 = select(Category).where(Category.id == product_data.category)
        cat_data = await session.execute(query1)
        cat = cat_data.scalars().first()
        query2 = select(Unit).where(Unit.id == product_data.unit)
        unit_data = await session.execute(query2)
        unit = unit_data.scalars().first()
        if unit and cat:
            query = insert(Product).values(**product_data.dict())
            await session.execute(query)
            await session.commit()
            return {'success': True, 'message': 'Product added successfully'}
        else:
            raise HTTPException(status_code=400, detail='Category or Unit does not exist')
    else:
        return {'success': False, 'message': 'Permission denied'}


@market_router.patch("/update-product/id")
async def update_product(
        product_id: int,
        product_new: ProductUpdateScheme,
        session: AsyncSession = Depends(get_async_session)
):
    product_query = select(Product).where(Product.id == product_id)
    product = await session.execute(product_query)
    dic = {}
    for new_data_key, new_data_val in product_new.dict().items():
        if new_data_val:
            dic[new_data_key] = new_data_val
    if product:
        query = update(Product).where(Product.id == product_id).values(**dic, last_updated=datetime.utcnow())
        await session.execute(query)
    else:
        raise HTTPException(status_code=400, detail="Product cannot be updated")
    await session.commit()
    return {'success': True, 'message': 'Product updated'}


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
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query = insert(Category).values(**category.dict())
    await session.execute(query)
    await session.commit()
    return {'success': True, 'message': 'Category'}


@market_router.post("/create-oder")
async def create_oder(
        products: List[OrderScheme],
        costumer_id: int,
        warehouse_id: int,
        paid: float = 0,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    product_list = []
    total_price = 0
    if paid >= 0:
        for product in products:
            query_pl = select(ProductLocation).where(ProductLocation.product_id == product.product_id and ProductLocation.warehouse_id == warehouse_id)
            pl_data = await session.execute(query_pl)
            product_location = pl_data.scalars().first()
            if product_location and product_location.product_amount > product.quantity:
                query_product = select(Product).where(Product.id == product.product_id)
                product_data = await session.execute(query_product)
                product__data = product_data.scalars().first()
                product_list.append(product__data)
                total_price += product__data.price*product.quantity
            else:
                raise HTTPException(status_code=400, detail="Product is not enough")
        if product_list:
            query = insert(OrderDetail).values(
                user_id=token['user_id'],
                costumer_id=costumer_id,
                total_price=total_price,
                paid=paid,
                created_at=datetime.now()
            )
            await session.execute(query)
            order_query = select(OrderDetail).where(
                (OrderDetail.user_id == token['user_id']) &
                (OrderDetail.costumer.has(id=costumer_id)))
            order = await session.execute(order_query)
            order_data = order.scalars().all()
            for product in products:
                query = insert(Order).values(
                    product_id=product.product_id,
                    count=product.quantity,
                    order_detail_id=order_data[-1].id,
                    warehouse_id=warehouse_id
                )
                await session.execute(query)
            await session.commit()
            return {'success': True, 'message': 'Order successfully created'}
        else:
            raise HTTPException(status_code=400, detail='No result found')
    else:
        raise HTTPException(status_code=400, detail='Invalid payment')


@market_router.get('/client-orders/')
async def client_order(
        costumer_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query_orders = select(OrderDetail).where(OrderDetail.costumer.has(id =costumer_id))
    orders = await session.execute(query_orders)
    order_details = orders.scalars().all()
    order_list = []
    if order_details is not None:
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
    else:
        raise HTTPException(status_code=400, detail='No result found')
    return order_list


@market_router.post('/confirm-order')
async def confirm_order(
        order_detail_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Order).options(
        selectinload(Order.product),
        selectinload(Order.warehouse),
        selectinload(Order.order_detail)).where(Order.order_detail_id == order_detail_id)
    order__data = await session.execute(query)
    order_data = order__data.scalars().all()
    if order_data:
        data = await session.get(OrderDetail, order_detail_id)
        if data.is_active:
            for order in order_data:
                query2 = select(ProductLocation).where(
                    (ProductLocation.warehouse.has(id=order.warehouse_id)) &
                    (ProductLocation.product_id == order.product_id)
                )
                data2 = await session.execute(query2)
                data_loc = data2.scalars().first()
                if data_loc:
                    if data_loc.product_amount>=order.count:
                        query1 = update(ProductLocation).where(
                            ProductLocation.id == data_loc.id).values(
                            product_amount=data_loc.product_amount-order.count
                        )
                        await session.execute(query1)
                        order.order_detail.is_active = False
                    else:
                        raise HTTPException(status_code=400, detail=f'Product is not enough in {order.warehouse.name}')
                else:
                    raise HTTPException(status_code=400, detail=f'Product is None in {order.warehouse.name}')
            await session.commit()
        else:
            raise HTTPException(status_code=400, detail='order already confirmed')

        return {'message': 'Order confirmed.'}
    else:
        raise HTTPException(status_code=400, detail='Order not found')


@market_router.post('/start-composite')
async def start_composite(
        data: CompositeAddScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(Composite).values(**data.dict(), employee_id=token['user_id'])
        await session.execute(query)
        user = await session.get(User, token['user_id'])
        print(user)
        query1 = select(ResourceLocation).where(
            (ResourceLocation.warehouse_id == user.warehouse_id) and
            (ResourceLocation.resource_id == data.resource_id))
        data2 = await session.execute(query1)
        re_loc = data2.scalars().first()
        print(re_loc.id)
        if re_loc and re_loc.amount >= data.resource_amount:
            await session.execute(update(ResourceLocation).where(
                ResourceLocation.id == re_loc.id
            ).values(amount=re_loc.amount-data.resource_amount))
            await session.commit()
            return {'success': True, **data.dict()}
        else:
            raise HTTPException(status_code=400, detail=f'Resource location not {user.warehouse.name} or not enough')
    except Exception as e:
        raise HTTPException(status_code=400, detail='Request not valid')


@market_router.post('/end-composite')
async def end_composite(
        composite_id: int,
        confirm_data: EndProcessScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query = update(Composite).where(Composite.id == composite_id).values(**confirm_data.dict(), end_at=datetime.utcnow())
    data = await session.execute(query)
    if data:
        await session.commit()
        return {'success': True}
    else:
        return {'success': False}

# @market_router.post(''):






