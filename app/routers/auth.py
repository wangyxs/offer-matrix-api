from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.middleware import validate_username, validate_email, validate_password
from app.schemas.auth import Token, LoginRequest, RegisterRequest, LoginResponse
from app.schemas.common import ResponseModel
from app.services import create_user, login_user, get_user_by_username, get_user_by_email
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=ResponseModel)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 验证用户名
    if not validate_username(user_data.username):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名格式不正确，应为3-20位字母、数字或下划线"
        )
    
    # 验证邮箱
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式不正确"
        )
    
    # 验证密码
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度应在3-50位之间"
        )
    
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建新用户
    user = create_user(db, user_data)
    
    return ResponseModel(
        success=True,
        message="注册成功",
        data={"user_id": user.id, "username": user.username}
    )


@router.post("/login", response_model=LoginResponse)
async def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    login_result = login_user(db, user_data)
    if not login_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return login_result


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """获取访问令牌（OAuth2兼容）"""
    from app.services import authenticate_user
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}