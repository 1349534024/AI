from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, model_validator, ValidationError
from pydantic import ConfigDict

# 接收用户传过来的数据的一个对象
RawPasswordStr = Annotated[str,Field(...,min_length=4,max_length=50)]
RawUserNameStr =Annotated[str,Field(...,min_length=4,max_length=50)]
class RegisterIn(BaseModel):
    email:EmailStr
    username:RawUserNameStr
    password:RawPasswordStr
    confirm_password:RawPasswordStr
    # 验证用户的有效性
    code:Annotated[str,Field(...,min_length=4,max_length=4)]

    # 完成确认密码的校验
    @model_validator(mode="after")
    def password_is_valid(self,password:str) -> bool:
        password = self.password
        confirm_password = self.confirm_password
        if password != confirm_password:
            raise ValidationError("Passwords don't match")
        return self

# 存入数据库的是少数字段
class UserCreateSchema(BaseModel):
    email:EmailStr
    username:RawUserNameStr
    password:RawPasswordStr

# 开发对象，接收用户登录信息
class LoginIn(BaseModel):
    email:EmailStr
    password:RawPasswordStr

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:Annotated[int,Field(...)]
    username: RawUserNameStr
    email: str
    is_admin: bool = False
    is_active: bool = True

from models.user import User
class LoginOut(BaseModel):
    user:UserSchema
    token: str

class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_admin: bool
    is_active: bool

class AdminUserListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AdminUserOut]

class AdminUserUpdateIn(BaseModel):
    email: str | None = None
    username: RawUserNameStr | None = None
    is_admin: bool | None = None
    is_active: bool | None = None

class AdminResetPasswordIn(BaseModel):
    password: RawPasswordStr
