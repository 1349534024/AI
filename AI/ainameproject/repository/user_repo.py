from sqlalchemy.ext.asyncio.session import AsyncSession
from models.user import User, EmailCode
from sqlalchemy import select, update, delete, exists, func, or_
from datetime import datetime, timedelta

from schemas.user_schemas import UserCreateSchema


class EmailCodeRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_email_code(self,email:str,code:str):
        async with self.session.begin():
            email_code = EmailCode(email=email,code=code)
            self.session.add(email_code)
            return email_code

    async def check_email_code(self,email:str,code:str):
        async with self.session.begin():
            email_code = await self.session.scalar(select(EmailCode)
                                                   .filter(EmailCode.email==email,EmailCode.code==code))

            if not email_code:
                return False
                # 超过5分钟过期失效
            if (datetime.now() - email_code.created_time) >= timedelta(minutes=5):
                return False
                # 校验通过
            return True

class UserRepository():
    def __init__(self, session: AsyncSession):
        self.session = session
    async def get_user_by_email(self,email:str):
        async with self.session.begin():
            result = await self.session.execute(select(User).where(User.email==email))
            return result.scalar_one_or_none()
    async def get_user_by_id(self,user_id:int):
        async with self.session.begin():
            result = await self.session.execute(select(User).where(User.id==user_id))
            return result.scalar_one_or_none()
    async def create_user(self,user:UserCreateSchema):
        async with self.session.begin():
            user = User(**user.model_dump())
            self.session.add(user)
            return user
    async def email_is_exist(self,email:str):
        async with self.session.begin():
            stmt = select(exists().where(User.email==email))
            return await self.session.scalar(stmt)

    async def email_is_exist_except_user(self,email:str,user_id:int):
        async with self.session.begin():
            stmt = select(exists().where(User.email==email,User.id!=user_id))
            return await self.session.scalar(stmt)

    async def list_users(self,page:int=1,page_size:int=20,keyword:str|None=None,is_active:bool|None=None):
        stmt = select(User)
        count_stmt = select(func.count()).select_from(User)
        filters = []
        if keyword:
            like_keyword = f"%{keyword}%"
            filters.append(or_(User.email.like(like_keyword),User.username.like(like_keyword)))
        if is_active is not None:
            filters.append(User.is_active==is_active)
        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)
        offset = (page - 1) * page_size
        async with self.session.begin():
            total = await self.session.scalar(count_stmt)
            result = await self.session.execute(stmt.order_by(User.id.desc()).offset(offset).limit(page_size))
            return total or 0,result.scalars().all()

    async def count_users_by_status(self,keyword:str|None=None):
        filters = []
        if keyword:
            like_keyword = f"%{keyword}%"
            filters.append(or_(User.email.like(like_keyword),User.username.like(like_keyword)))
        total_stmt = select(func.count()).select_from(User)
        active_stmt = select(func.count()).select_from(User).where(User.is_active==True)
        frozen_stmt = select(func.count()).select_from(User).where(User.is_active==False)
        if filters:
            total_stmt = total_stmt.where(*filters)
            active_stmt = active_stmt.where(*filters)
            frozen_stmt = frozen_stmt.where(*filters)
        async with self.session.begin():
            total = await self.session.scalar(total_stmt)
            active = await self.session.scalar(active_stmt)
            frozen = await self.session.scalar(frozen_stmt)
            return {
                "total": total or 0,
                "active": active or 0,
                "frozen": frozen or 0,
            }

    async def update_user(self,user_id:int,values:dict):
        async with self.session.begin():
            user = await self.session.get(User,user_id)
            if not user:
                return None
            for key,value in values.items():
                if key == "password":
                    user.password = value
                else:
                    setattr(user,key,value)
            return user

    async def delete_user(self,user_id:int):
        async with self.session.begin():
            user = await self.session.get(User,user_id)
            if not user:
                return False
            await self.session.delete(user)
            return True
