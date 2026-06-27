from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.auth import AuthHandler
from dependencies import get_session
from models.user import User
from repository.user_repo import UserRepository
from schemas.user_schemas import AdminResetPasswordIn, AdminUserListOut, AdminUserOut, AdminUserUpdateIn, LoginIn, LoginOut


router = APIRouter(prefix="/admin", tags=["admin"])
auth_handler = AuthHandler()


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
    }


async def get_current_admin(
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_repository = UserRepository(session=session)
    user = await user_repository.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="管理员账号不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="管理员账号已被冻结")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@router.post("/auth/login", response_model=LoginOut)
async def admin_login(
    userinfo: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    user = await user_repository.get_user_by_email(userinfo.email)
    if not user:
        raise HTTPException(status_code=400, detail="管理员账号不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="管理员账号已被冻结")
    if not user.check_password(userinfo.password):
        raise HTTPException(status_code=400, detail="密码输入错误，请核对后输入")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="该账号不是管理员账号")
    tokens = auth_handler.encode_login_token(user.id)
    return {
        "user": serialize_user(user),
        "token": tokens["access_token"],
    }


@router.get("/users", response_model=AdminUserListOut)
async def list_users(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    keyword: str | None = None,
    is_active: bool | None = None,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    total, users = await user_repository.list_users(page=page, page_size=page_size, keyword=keyword, is_active=is_active)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [serialize_user(user) for user in users],
    }


@router.get("/users/stats")
async def get_user_stats(
    keyword: str | None = None,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    return await user_repository.count_users_by_status(keyword=keyword)


@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return serialize_user(user)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
async def update_user(
    user_id: int,
    data: AdminUserUpdateIn,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    values = data.model_dump(exclude_unset=True)
    if "email" in values and await user_repository.email_is_exist_except_user(values["email"], user_id):
        raise HTTPException(status_code=400, detail="该邮箱已被其他用户使用")
    if user_id == admin.id and values.get("is_admin") is False:
        raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")
    if user_id == admin.id and values.get("is_active") is False:
        raise HTTPException(status_code=400, detail="不能冻结自己的管理员账号")

    updated_user = await user_repository.update_user(user_id, values)
    return serialize_user(updated_user)


@router.post("/users/{user_id}/freeze", response_model=AdminUserOut)
async def freeze_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能冻结自己的管理员账号")
    user_repository = UserRepository(session=session)
    user = await user_repository.update_user(user_id, {"is_active": False})
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return serialize_user(user)


@router.post("/users/{user_id}/unfreeze", response_model=AdminUserOut)
async def unfreeze_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    user = await user_repository.update_user(user_id, {"is_active": True})
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return serialize_user(user)


@router.post("/users/{user_id}/reset-password", response_model=AdminUserOut)
async def reset_password(
    user_id: int,
    data: AdminResetPasswordIn,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session=session)
    user = await user_repository.update_user(user_id, {"password": data.password})
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return serialize_user(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己的管理员账号")
    user_repository = UserRepository(session=session)
    deleted = await user_repository.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "用户删除成功"}
