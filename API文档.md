# offer-matrix-api 文档

## 概述

offer-matrix-api 提供用户认证、角色管理、面试记录等功能。所有API接口使用 RESTful 风格，支持 JSON 数据格式。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1.0.0
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证说明

### 获取访问令牌

API认证使用JWT令牌。在登录成功后，服务器会返回一个访问令牌，您需要在后续请求的`Authorization`头中携带该令牌。

```
Authorization: Bearer <your_access_token>
```

## API接口

### 1. 认证相关 (Authentication)

#### 1.1 用户注册

注册新用户账号。

**请求**
```
POST /api/auth/register
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "email": "string (可选)"
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-20位字母、数字或下划线 |
| password | string | 是 | 密码，6-50位字符 |
| email | string | 否 | 邮箱地址 |

**响应**
```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user_id": 1,
        "username": "testuser"
    }
}
```

**错误响应**
```json
{
    "detail": "用户名已存在"
}
```

---

#### 1.2 用户登录

使用用户名和密码登录，获取访问令牌。

**请求**
```
POST /api/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**错误响应**
```json
{
    "detail": "用户名或密码错误"
}
```

---

#### 1.3 获取访问令牌 (OAuth2兼容)

与登录功能相同，使用OAuth2表单格式。

**请求**
```
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=testuser&password=123456
```

**响应**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

---

### 2. 用户相关 (Users)

#### 2.1 获取当前用户信息

获取当前登录用户的详细信息。

**请求**
```
GET /api/users/me
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2024-01-23T00:00:00"
}
```

---

#### 2.2 更新当前用户信息

更新当前登录用户的信息。

**请求**
```
PUT /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "string (可选)",
    "email": "string (可选)",
    "password": "string (可选)"
}
```

**响应**
```json
{
    "success": true,
    "message": "用户信息更新成功",
    "data": {
        "user_id": 1,
        "username": "newusername"
    }
}
```

---

#### 2.3 获取指定用户信息

根据用户ID获取用户信息（仅用于管理员或相关用户）。

**请求**
```
GET /api/users/{user_id}
Authorization: Bearer <access_token>
```

**路径参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |

**响应**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2024-01-23T00:00:00"
}
```

---

### 3. 角色相关 (Roles)

#### 3.1 获取角色列表

获取所有可用的角色列表。

**请求**
```
GET /api/roles/?skip=0&limit=100
Authorization: Bearer <access_token>
```

**查询参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回的最大记录数 |

**响应**
```json
[
    {
        "id": 1,
        "name": "前端工程师",
        "description": "负责前端开发",
        "is_active": true,
        "created_at": "2024-01-23T00:00:00"
    },
    {
        "id": 2,
        "name": "后端工程师",
        "description": "负责后端开发",
        "is_active": true,
        "created_at": "2024-01-23T00:00:00"
    }
]
```

---

#### 3.2 创建角色

创建新的角色。

**请求**
```
POST /api/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "string",
    "description": "string (可选)"
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色名称 |
| description | string | 否 | 角色描述 |

**响应**
```json
{
    "success": true,
    "message": "角色创建成功",
    "data": {
        "role_id": 1,
        "name": "新角色"
    }
}
```

---

#### 3.3 获取角色详情

根据ID获取角色详细信息。

**请求**
```
GET /api/roles/{role_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "id": 1,
    "name": "前端工程师",
    "description": "负责前端开发",
    "is_active": true,
    "created_at": "2024-01-23T00:00:00"
}
```

---

#### 3.4 更新角色

更新角色信息。

**请求**
```
PUT /api/roles/{role_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "string (可选)",
    "description": "string (可选)",
    "is_active": "boolean (可选)"
}
```

**响应**
```json
{
    "success": true,
    "message": "角色信息更新成功",
    "data": {
        "role_id": 1,
        "name": "更新后的角色"
    }
}
```

---

#### 3.5 删除角色

删除指定角色。

**请求**
```
DELETE /api/roles/{role_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "success": true,
    "message": "角色删除成功",
    "data": {
        "role_id": 1
    }
}
```

---

#### 3.6 为用户分配角色

为指定用户分配角色。

**请求**
```
POST /api/roles/assign
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "user_id": 1,
    "role_id": 1
}
```

**响应**
```json
{
    "success": true,
    "message": "角色分配成功",
    "data": {
        "user_role_id": 1,
        "user_id": 1,
        "role_id": 1
    }
}
```

---

#### 3.7 移除用户角色

移除用户的指定角色。

**请求**
```
DELETE /api/roles/remove/{user_id}/{role_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "success": true,
    "message": "角色移除成功",
    "data": {
        "user_id": 1,
        "role_id": 1
    }
}
```

---

### 4. 面试记录相关 (Interviews)

#### 4.1 获取面试记录列表

获取当前用户的面试记录列表。

**请求**
```
GET /api/interviews/?skip=0&limit=100
Authorization: Bearer <access_token>
```

**查询参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回的最大记录数 |

**响应**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "role_id": 1,
        "title": "前端工程师面试",
        "content": "面试内容描述",
        "score": 85.5,
        "feedback": "表现优秀",
        "is_completed": true,
        "created_at": "2024-01-23T00:00:00"
    }
]
```

---

#### 4.2 创建面试记录

创建新的面试记录。

**请求**
```
POST /api/interviews/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "string",
    "content": "string (可选)",
    "role_id": "integer (可选)"
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 面试记录标题 |
| content | string | 否 | 面试记录内容 |
| role_id | integer | 否 | 关联的角色ID |

**响应**
```json
{
    "success": true,
    "message": "面试记录创建成功",
    "data": {
        "record_id": 1,
        "title": "前端工程师面试"
    }
}
```

---

#### 4.3 获取面试记录详情

根据ID获取面试记录详情。

**请求**
```
GET /api/interviews/{record_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "id": 1,
    "user_id": 1,
    "role_id": 1,
    "title": "前端工程师面试",
    "content": "面试内容描述",
    "score": 85.5,
    "feedback": "表现优秀",
    "is_completed": true,
    "created_at": "2024-01-23T00:00:00",
    "updated_at": "2024-01-23T00:00:00"
}
```

---

#### 4.4 更新面试记录

更新面试记录信息。

**请求**
```
PUT /api/interviews/{record_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "string (可选)",
    "content": "string (可选)",
    "score": "number (可选)",
    "feedback": "string (可选)",
    "is_completed": "boolean (可选)",
    "role_id": "integer (可选)"
}
```

**响应**
```json
{
    "success": true,
    "message": "面试记录更新成功",
    "data": {
        "record_id": 1,
        "title": "更新后的标题"
    }
}
```

---

#### 4.5 删除面试记录

删除指定的面试记录。

**请求**
```
DELETE /api/interviews/{record_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "success": true,
    "message": "面试记录删除成功",
    "data": {
        "record_id": 1
    }
}
```

---

### 5. 问题相关 (Questions)

#### 5.1 获取问题列表

获取所有可用的面试问题。

**请求**
```
GET /api/questions/?role_id=1&skip=0&limit=100
Authorization: Bearer <access_token>
```

**查询参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| role_id | integer | 否 | - | 筛选指定角色的问题 |
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回的最大记录数 |

**响应**
```json
[
    {
        "id": 1,
        "role_id": 1,
        "question_text": "请介绍一下你的项目经验",
        "answer_text": "参考答案",
        "difficulty": "medium",
        "category": "项目经验",
        "is_active": true,
        "created_at": "2024-01-23T00:00:00"
    }
]
```

---

#### 5.2 创建问题

创建新的面试问题。

**请求**
```
POST /api/questions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "question_text": "string",
    "answer_text": "string (可选)",
    "difficulty": "string (可选)",
    "category": "string (可选)",
    "role_id": "integer (可选)"
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_text | string | 是 | 问题内容 |
| answer_text | string | 否 | 参考答案 |
| difficulty | string | 否 | 难度: easy/medium/hard |
| category | string | 否 | 问题分类 |
| role_id | integer | 否 | 关联的角色ID |

**响应**
```json
{
    "success": true,
    "message": "问题创建成功",
    "data": {
        "question_id": 1
    }
}
```

---

#### 5.3 获取问题详情

根据ID获取问题详情。

**请求**
```
GET /api/questions/{question_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "id": 1,
    "role_id": 1,
    "question_text": "请介绍一下你的项目经验",
    "answer_text": "参考答案",
    "difficulty": "medium",
    "category": "项目经验",
    "is_active": true,
    "created_at": "2024-01-23T00:00:00"
}
```

---

#### 5.4 更新问题

更新问题信息。

**请求**
```
PUT /api/questions/{question_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "question_text": "string (可选)",
    "answer_text": "string (可选)",
    "difficulty": "string (可选)",
    "category": "string (可选)",
    "is_active": "boolean (可选)",
    "role_id": "integer (可选)"
}
```

**响应**
```json
{
    "success": true,
    "message": "问题更新成功",
    "data": {
        "question_id": 1
    }
}
```

---

#### 5.5 删除问题

删除指定的问题。

**请求**
```
DELETE /api/questions/{question_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "success": true,
    "message": "问题删除成功",
    "data": {
        "question_id": 1
    }
}
```

---

### 6. 收藏相关 (Favorites)

#### 6.1 获取收藏列表

获取当前用户的收藏列表。

**请求**
```
GET /api/favorites/?skip=0&limit=100
Authorization: Bearer <access_token>
```

**查询参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回的最大记录数 |

**响应**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "question_id": 1,
        "created_at": "2024-01-23T00:00:00"
    }
]
```

---

#### 6.2 添加收藏

将问题添加到收藏列表。

**请求**
```
POST /api/favorites/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "question_id": 1
}
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_id | integer | 是 | 问题ID |

**响应**
```json
{
    "success": true,
    "message": "收藏添加成功",
    "data": {
        "favorite_id": 1
    }
}
```

---

#### 6.3 取消收藏

从收藏列表中移除问题。

**请求**
```
DELETE /api/favorites/{question_id}
Authorization: Bearer <access_token>
```

**响应**
```json
{
    "success": true,
    "message": "收藏取消成功",
    "data": {
        "question_id": 1
    }
}
```

---

## 错误响应格式

所有错误响应都遵循以下格式：

```json
{
    "detail": "错误描述信息"
}
```

常见HTTP状态码：
- `200 OK` - 请求成功
- `201 Created` - 创建成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未授权，需要登录
- `403 Forbidden` - 无权访问
- `404 Not Found` - 资源不存在
- `429 Too Many Requests` - 请求过于频繁
- `500 Internal Server Error` - 服务器内部错误

---

## 前后端联调指南

### 1. 注册流程

```javascript
// 1. 调用注册接口
const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'testuser',
        password: '123456',
        email: 'test@example.com'
    })
});

const result = await response.json();

if (result.success) {
    // 注册成功，跳转到登录页面或角色选择页面
    console.log('注册成功:', result.data);
} else {
    // 注册失败，显示错误信息
    console.error('注册失败:', result.message);
}
```

### 2. 登录流程

```javascript
// 1. 调用登录接口
const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'testuser',
        password: '123456'
    })
});

const result = await response.json();

if (result.access_token) {
    // 登录成功，保存令牌
    localStorage.setItem('access_token', result.access_token);
    
    // 跳转到主页面
    console.log('登录成功');
} else {
    // 登录失败，显示错误信息
    console.error('登录失败:', result.detail);
}
```

### 3. 携带令牌的请求

```javascript
// 获取保存的令牌
const token = localStorage.getItem('access_token');

// 发起需要认证的请求
const response = await fetch('http://localhost:8000/api/users/me', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    }
});

const user = await response.json();
console.log('当前用户:', user);
```

### 4. 创建面试记录

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/interviews/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        title: '前端工程师面试',
        content: '面试内容描述',
        role_id: 1
    })
});

const result = await response.json();
console.log('创建面试记录:', result);
```

---

## 注意事项

1. **令牌有效期**: JWT令牌默认有效期为30分钟，过期后需要重新登录
2. **速率限制**: API接口有速率限制，避免频繁请求
3. **输入验证**: 所有输入数据都会进行验证，请确保数据格式正确
4. **密码安全**: 密码使用bcrypt加密存储，不会明文保存
5. **CORS配置**: 当前允许所有来源访问，生产环境请配置具体域名

---

## 联系支持

如有问题，请联系开发团队或查看项目README文档。
