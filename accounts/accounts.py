from datetime import datetime
from typing import List

from passlib.context import CryptContext
from sqlalchemy import insert, select, update, delete
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.scheme import RegisterScheme, LoginScheme, UserInfoScheme, CostumerAddScheme
from accounts.utils import generate_token, verify_token
from database import get_async_session
from models.models import User, Costumer
from permissions import permission

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
account_router = APIRouter()


@account_router.post("/register")
async def register(
        user: RegisterScheme,
        session: AsyncSession = Depends(get_async_session)
):
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
                password=pwd_context.hash(user.password1)
            )
            await session.execute(query)
            await session.commit()
            return {'success': True, "message": "Account Created"}
    else:
        raise HTTPException(status_code=400, detail="Passwords does not same")


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
    query = select(User).where(User.id == user_id)
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




