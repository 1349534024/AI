import os

DB_URI=os.getenv("DB_URI","mysql+aiomysql://root:123456@127.0.0.1:3306/ainameproject?charset=utf8mb4")

MAIL_USERNAME=os.getenv("MAIL_USERNAME","")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD","")
MAIL_FROM=os.getenv("MAIL_FROM",MAIL_USERNAME)
MAIL_PORT=int(os.getenv("MAIL_PORT","587"))
MAIL_SERVER=os.getenv("MAIL_SERVER","smtp.qq.com")
MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME","ainameappproject")
MAIL_STARTTLS=os.getenv("MAIL_STARTTLS","true").lower() == "true"
MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS","false").lower() == "true"
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","dev-only-change-me")
from datetime import timedelta
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
