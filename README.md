# offer-matrix-api

offer-matrix-api 是 Offer Matrix 项目的后端服务，提供用户认证、角色管理、面试记录等功能。

## 功能特性

- 用户注册和登录
- JWT令牌认证
- 用户信息管理
- 角色管理
- 面试记录管理
- 问题库管理
- 收藏管理

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt

## 项目结构

```
offer-matrix-api/
├── app/
│   ├── main.py                     # FastAPI应用入口
│   ├── core/                       # 配置、数据库、安全与中间件
│   ├── models/                     # SQLAlchemy模型
│   ├── routers/                    # API路由
│   ├── schemas/                    # Pydantic数据模式
│   └── services/                   # 业务服务
├── scripts/                        # 初始化与维护脚本
├── requirements.txt                # 依赖包
├── run.py                          # 启动脚本
├── API文档.md                       # API说明
└── README.md                       # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制并编辑 `.env` 文件，设置必要的环境变量：

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Database Configuration
DATABASE_URL=sqlite:///./offer_matrix.db

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 启动服务

```bash
python run.py
```

服务将在 http://localhost:8000 启动

## API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要API接口

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/token` - 获取访问令牌(OAuth2兼容)

### 用户相关

- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新当前用户信息
- `GET /api/users/{user_id}` - 根据ID获取用户信息

## 默认账户

初始化数据库后，系统会创建一个默认管理员账户：

- 用户名: admin
- 密码: admin123

## 开发说明

### 数据库迁移

如果需要修改数据库结构，可以使用Alembic进行数据库迁移：

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 测试

运行测试：

```bash
pytest
```

## 安全注意事项

1. 生产环境中务必修改 `SECRET_KEY`
2. 使用HTTPS协议
3. 定期更新依赖包
4. 限制API访问频率
5. 验证所有输入数据

## 部署

### Docker部署

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

### 生产环境配置

1. 使用PostgreSQL数据库
2. 设置环境变量 `API_RELOAD=false`
3. 配置反向代理(Nginx)
4. 设置SSL证书

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License
