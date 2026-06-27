from sqlalchemy import Integer,String,DateTime,Boolean
from sqlalchemy.orm import  Mapped,mapped_column
from pwdlib import PasswordHash
from . import Base
from datetime import datetime
password_hash = PasswordHash.recommended()
class User(Base):
    __tablename__ = "user"
    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    email:Mapped[str] = mapped_column(String(100),unique=True)
    username:Mapped[str] = mapped_column(String(100))
    _password:Mapped[str] = mapped_column(String(200))
    is_admin:Mapped[bool] = mapped_column(Boolean,default=False,server_default="0")
    is_active:Mapped[bool] = mapped_column(Boolean,default=True,server_default="1")

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        password = kwargs.pop("password",None)
        if password:
            self.password=password
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self,password):
        self._password=password_hash.hash(password)
    def check_password(self,password):
        return password_hash.verify(password,self._password)

class EmailCode(Base):
    __tablename__ = "email_code"

    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    email:Mapped[str] = mapped_column(String(100))
    code:Mapped[str] = mapped_column(String(100))
    created_time:Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

