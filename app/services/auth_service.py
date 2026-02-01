from datetime import timedelta
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest
from app.services.user_service import authenticate_user
from app.core.security import create_access_token
from app.core.config import settings


def login_user(db: Session, login_request: LoginRequest):
    """用户登录"""
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        return None
    if not user.is_active:
        return None
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # 获取用户角色列表 (包含详细信息)
    roles = [
        {
            "id": ur.role.id,
            "name": ur.role.name,
            "description": ur.role.description,
            "prompt": ur.role.prompt
        } 
        for ur in user.roles if ur.is_active and ur.role.is_active
    ]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "roles": roles
    }