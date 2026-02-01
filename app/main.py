from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import engine
from app.core.logger import logger
from app.core.middleware import SecurityMiddleware, rate_limit_exceeded_handler
from app.models import User, Role, UserRole, InterviewRecord, Question, Favorite
from app.routers import api_router

# 创建数据库表
User.metadata.create_all(bind=engine)
Role.metadata.create_all(bind=engine)
UserRole.metadata.create_all(bind=engine)
InterviewRecord.metadata.create_all(bind=engine)
Question.metadata.create_all(bind=engine)
Favorite.metadata.create_all(bind=engine)

# 速率限制器
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="OfferMatrix Backend API"
)

# 添加速率限制中间件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全中间件
app.add_middleware(SecurityMiddleware)

# 包含API路由
app.include_router(api_router)

from fastapi.staticfiles import StaticFiles
import os

# 创建 uploads 目录
uploads_dir = settings.DATA_DIR / "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "OfferMatrix Backend is running!",
        "status": "ok"
    }


@app.get("/ping")
async def ping():
    return {"pong": True}
