from sqlalchemy import select

from models.models import UserRoles, Role


async def permission(user_id, session, role_names: list):
    query = select(UserRoles).where(UserRoles.user_id == user_id)
    user_roles = await session.execute(query)
    user_role_data = user_roles.scalars().all()
    for user_role in user_role_data:
        query_role = select(Role).where(Role.id == user_role.role_id)
        role_data = await session.execute(query_role)
        role = role_data.scalars().one()
        if role.name in role_names:
            return True
    return False
