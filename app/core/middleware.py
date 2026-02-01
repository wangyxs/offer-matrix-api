from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import re

# 速率限制器
limiter = Limiter(key_func=get_remote_address)


from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next):
        print(f"DEBUG: Middleware Request: {request.scope['type']} {request.url.path}")
        # Skip WebSocket requests to prevent interference
        if request.scope.get("type") == "websocket":
            print("DEBUG: Skipping SecurityMiddleware for WebSocket")
            return await call_next(request)

        # 在这里可以添加各种安全检查
        
        # 调用下一个中间件或路由处理器
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username:
        return False
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        return False
    return True


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email:
        return True  # 邮箱是可选的
    if len(email) > 100:
        return False
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    return True


def validate_password(password: str) -> bool:
    """验证密码强度"""
    if not password:
        return False
    if len(password) < 3 or len(password) > 50:
        return False
    return True


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """速率限制超出处理器"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "message": "请求过于频繁，请稍后再试",
            "error_code": "RATE_LIMIT_EXCEEDED"
        }
    )