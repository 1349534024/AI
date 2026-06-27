from fastapi import FastAPI
from fastapi.params import Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from dependencies import get_email
from routers.auth_router import router as auth_router
from pyexpat.errors import messages
from routers.name_router import router as name_router
from routers.rag_router import router as rag_router
from routers.admin_router import router as admin_router
from core.workflow import init_workflow_graph, close_workflow_graph
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("正在初始化 LangGraph...")
    await init_workflow_graph()
    print("LangGraph 初始化完成！")

# 【新增】服务关闭时清理资源
@app.on_event("shutdown")
async def shutdown_event():
    print("正在关闭数据库连接...")
    await close_workflow_graph()

app.include_router(auth_router)
app.include_router(name_router)
app.include_router(rag_router)
app.include_router(admin_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许请求的源列表
    allow_credentials=True,    # 允许携带 Cookie/凭证
    allow_methods=["*"],       # 允许的请求方法（"GET", "POST", "PUT", "DELETE" 等，"*" 表示全部允许）
    allow_headers=["*"],       # 允许的请求头（"*" 表示全部允许）
)

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}



@app.get("/mail/test")
async def mail_test(email:str,mail:FastMail=Depends(get_email)):
   message =MessageSchema(
       subject="ainame验证码",
       recipients=[email],
       body=f"Hello {email}",
       subtype=MessageType.plain)

   await mail.send_message(message)
   return {"message": f"邮件发送成功"}
