from datetime import datetime
from typing import List

from passlib.context import CryptContext
from sqlalchemy import insert, select, update, delete
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from accounts.scheme import RegisterScheme, LoginScheme, UserInfoScheme, CostumerAddScheme
from accounts.utils import generate_token, verify_token
from database import get_async_session
from models.models import User, Costumer, Warehouse, Shift, UserRoles
from permissions import permission
from warehouse.scheme import WarehouseGetScheme

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
account_router = APIRouter()


@account_router.post("/register")
async def register(
        user: RegisterScheme,
        session: AsyncSession = Depends(get_async_session)
):
    warehouse = await session.get(Warehouse, user.warehouse_id)
    shift = await session.get(Shift, user.shift_id)
    if warehouse and shift:
        if user.password1 == user.password2:
            query_login = select(User).where(User.login == user.login)
            is_login = await session.execute(query_login)
            email_query = select(User).where(User.email == user.email)
            exist_email = await session.execute(email_query)
            if is_login.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Login already exists !!!")
            elif exist_email.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already exists !!!")
            else:
                query = insert(User).values(
                    firstname=user.firstname,
                    lastname=user.lastname,
                    login=user.login,
                    email=user.email,
                    phone=user.phone_number,
                    password=pwd_context.hash(user.password1),
                    shift_id=user.shift_id,
                    warehouse_id=user.warehouse_id
                )
                await session.execute(query)
                await session.commit()
                return {'success': True, "message": "Account Created"}
        else:
            raise HTTPException(status_code=400, detail="Passwords does not same")
    else:
        raise HTTPException(status_code=400, detail='Request body is invalid')


@account_router.post('/login')
async def login(
        user: LoginScheme,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(User).where((User.login == user.login))
    user_login = await session.execute(query)
    user_obj = user_login.scalars().one()
    if pwd_context.verify(user.password, user_obj.password):
        user_id = user_obj.id
        user_obj.last_updated = datetime.now()
        await session.commit()
        return generate_token(user_id)
    else:
        raise HTTPException(status_code=400, detail="Login failed")


@account_router.get('/user_info', response_model=UserInfoScheme)
async def user_info(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    user_id = token['user_id']
    query = select(User).options(selectinload(User.warehouse), selectinload(User.shift)).where(User.id == user_id)
    user = await session.execute(query)
    user_data = user.scalars().first()
    return user_data


@account_router.get('/all-users', response_model=List[UserInfoScheme])
async def all_users(
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    if await permission(token['user_id'], session, ['admin', 'Boss']):
        query = select(User)
        users = await session.execute(query)
        users_data = users.scalars().all()
        return users_data
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@account_router.post('/add-costumer')
async def add_costumer(
        costumer: CostumerAddScheme,
        token: dict = Depends(verify_token),
        session: AsyncSession = Depends(get_async_session)
):
    query_phone = select(Costumer).where((Costumer.phone == costumer.phone) | (Costumer.email == costumer.email))
    is_phone = await session.execute(query_phone)
    if is_phone.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Costumer already exists !!!")
    query_costumer = insert(Costumer).values(
        **costumer.dict(),
        last_login=None,
        created_at=datetime.now(),
        user_id=token['user_id']
    )
    await session.execute(query_costumer)
    await session.commit()
    return {'success': True, **costumer.dict()}


@account_router.get('/employee-{pk}', response_model=UserInfoScheme)
async def get_employee(
        pk: int,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(User).options(selectinload(User.warehouse)).where(User.warehouse_id == pk)
    result = await session.execute(query)
    user = result.scalars().first()
    if user:
        users_warehouse_list = []
        user_warehouse = UserInfoScheme(
            login=user.login,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone=user.phone,
            last_updated=user.last_updated,
            warehouse=WarehouseGetScheme(
                id=user.warehouse.id,
                name=user.warehouse.name,
                longitude=user.warehouse.longitude,
                latitude=user.warehouse.latitude
            ).dict()
        )
        users_warehouse_list.append(user_warehouse)
        return user_warehouse
    else:
        raise HTTPException(status_code=400, detail="Employee not found")


# @account_router.get('all-employees', response_model=List[UserInfoScheme])
# async def get_all_employees(
#         session: AsyncSession = Depends()
# ):
#     query1 = select(UserRoles).options(selectinload(UserRoles.user), selectinload(UserRoles.role)).where(UserRoles.role.name == 'employee')
#     data = await session.execute(query1)
#     data1 = data.scalars().all()
#     return data1



