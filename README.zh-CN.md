# offer-matrix-api

[中文](./README.zh-CN.md) | [English](./README.en.md)

`offer-matrix-api` 是一个面向 AI 模拟面试与岗位训练平台的 FastAPI 后端服务，负责承载用户认证、岗位与资料管理、AI 面试对话、题组生成、收藏、面试记录以及面试分析等核心能力。

## 项目亮点

- 用户注册登录与 JWT 鉴权
- 岗位与用户岗位关系管理
- 角色维度的简历与学习资料管理
- AI 模拟面试对话接口
- 面试记录保存与分析
- AI 题组生成与训练流程支持
- 收藏题目与学习闭环
- 文本转语音能力支持

## 适用场景

- 为 AI 模拟面试产品提供后端基础设施
- 为岗位化训练平台提供题目与记录管理能力
- 为简历驱动提问、面试分析、训练反馈提供服务接口
- 作为 Android、Web 或小程序端的统一面试训练后端

## 技术栈

- FastAPI
- SQLAlchemy
- SQLite（本地开发）
- 可演进到 PostgreSQL 的数据模型
- JWT Authentication
- LLM 能力接入，用于题目生成与面试分析
- Edge TTS 集成

## 核心接口域

- `/api/auth`
  用户认证与令牌签发
- `/api/users`
  用户信息管理
- `/api/roles`
  岗位、岗位分配、简历与资料管理
- `/api/question-sets`
  AI 生成题组
- `/api/interview`
  面试对话、TTS、收藏、记录与分析
- `/api/interviews`
  面试记录 CRUD

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建本地 `.env` 文件：

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
DATABASE_URL=sqlite:///./offer_matrix.db
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ZHIPUAI_API_KEY=
ALIYUN_ACCESS_KEY=
ALIYUN_SECRET_KEY=
ALIYUN_APP_ID=
ALIYUN_APP_KEY=
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务

```bash
python run.py
```

本地启动地址：`http://localhost:8000`

## API 文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

更详细的接口示例可参考 [API文档.md](./API文档.md)。

## 项目结构

```text
app/
├── core/        # 配置、数据库、安全、中间件
├── models/      # SQLAlchemy 模型
├── routers/     # FastAPI 路由模块
├── schemas/     # 请求与响应模型
└── services/    # AI 面试、题组生成、分析、TTS、认证
scripts/         # 本地初始化与辅助脚本
```

## 关联仓库

- Android 客户端：[offer-matrix-android](https://github.com/wangyxs/offer-matrix-android)

## 关键词

AI 模拟面试后端、FastAPI 面试平台、题组生成、面试分析、简历驱动面试、岗位训练、求职准备
