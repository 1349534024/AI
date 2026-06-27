import asyncio

from models import AsyncSessionFactory, engine
from models.user import User
from sqlalchemy import select


ADMIN_EMAIL = "admin@example.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123456"


async def create_admin():
    session = AsyncSessionFactory()
    try:
        async with session.begin():
            result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                existing_user.username = ADMIN_USERNAME
                existing_user.password = ADMIN_PASSWORD
                existing_user.is_admin = True
                existing_user.is_active = True
                print(f"管理员已存在，已更新密码和权限：{ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            else:
                admin = User(
                    email=ADMIN_EMAIL,
                    username=ADMIN_USERNAME,
                    password=ADMIN_PASSWORD,
                    is_admin=True,
                    is_active=True,
                )
                session.add(admin)
                print(f"管理员创建成功：{ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    finally:
        await session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
