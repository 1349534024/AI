from core.mailtools import create_mail_instance
from fastapi_mail import FastMail
async def get_email() -> FastMail:
    return create_mail_instance()

from models import AsyncSessionFactory

async def get_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
       await session.close()