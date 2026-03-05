# FastAPI JWT 认证示例项目

一个使用 FastAPI 框架构建的高性能 Web API 示例项目，集成了 JWT 认证系统。

## 🚀 特性

- **高性能**：基于 Starlette 和 Pydantic，提供极高的性能
- **JWT 认证**：完整的用户注册、登录和授权系统
- **自动文档**：自动生成交互式 API 文档（Swagger UI 和 ReDoc）
- **类型安全**：使用 Python 类型提示进行数据验证
- **现代化**：支持 async/await 异步编程
- **数据库集成**：使用 SQLAlchemy 进行数据持久化
- **易于测试**：内置测试支持
- **标准化**：遵循 OpenAPI 规范

## 📋 环境要求

- Python 3.8+
- pip 或 poetry

## 🛠️ 安装

### 使用 pip

```bash
# 克隆项目
git clone <repository-url>
cd fastapi

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 使用 poetry

```bash
# 安装 poetry (如果尚未安装)
pip install poetry

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

## 🏃‍♂️ 快速开始

1. **启动开发服务器**

```bash
# 使用 uvicorn 启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 poetry
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **访问 API 文档**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 📁 项目结构

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 应用入口
│   ├── api/                        # API 路由
│   │   ├── __init__.py
│   │   ├── deps.py                 # 依赖项（认证等）
│   │   └── endpoints/              # 端点定义
│   │       ├── __init__.py
│   │       ├── auth.py             # 认证相关端点
│   │       └── items.py            # 项目相关端点
│   ├── core/                       # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py               # 应用配置
│   │   └── security.py             # JWT 安全相关
│   ├── models/                     # 数据库模型
│   │   ├── __init__.py
│   │   └── user.py                 # 用户模型
│   ├── schemas/                    # Pydantic 模式
│   │   ├── __init__.py
│   │   └── user.py                 # 用户模式
│   ├── crud/                       # 数据库操作
│   │   ├── __init__.py
│   │   └── user.py                 # 用户 CRUD 操作
│   └── db/                         # 数据库相关
│       ├── __init__.py
│       └── database.py             # 数据库连接
├── tests/                          # 测试文件
│   ├── __init__.py
│   └── test_auth.py                # 认证测试
├── requirements.txt                 # 依赖列表
├── .env.example                    # 环境变量示例
├── .gitignore
└── README.md
```

## 🔧 配置

### 环境变量

1. **复制环境变量示例文件**

```bash
cp .env.example .env
```

2. **编辑 `.env` 文件并配置以下变量**

```env
# 应用配置
APP_NAME="FastAPI Demo"
APP_VERSION="1.0.0"
DEBUG=true

# JWT 配置
SECRET_KEY="your-super-secret-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL="sqlite:///./app.db"
```

**⚠️ 重要**：在生产环境中，请务必修改 `SECRET_KEY` 为一个强随机字符串！

## 🔐 认证系统

### JWT 认证流程

1. **用户注册**
   ```bash
   POST /auth/register
   {
     "username": "your_username",
     "email": "your_email@example.com",
     "password": "your_password"
   }
   ```

2. **用户登录**
   ```bash
   POST /auth/login
   Content-Type: application/x-www-form-urlencoded
   
   username=your_username&password=your_password
   ```

3. **访问受保护路由**
   ```bash
   GET /items/
   Authorization: Bearer <your_jwt_token>
   ```

### 认证端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | 无 |
| POST | `/auth/login` | 用户登录 | 无 |
| GET | `/auth/me` | 获取当前用户信息 | JWT |

### 受保护路由

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/items/` | 获取项目列表 | JWT |
| GET | `/items/{item_id}` | 获取单个项目 | JWT |
| POST | `/items/` | 创建项目 | JWT |

### 代码示例

#### JWT 依赖使用

```python
from app.api.deps import get_current_active_user
from app.models.user import User

@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}!"}
```

#### 密码哈希

```python
from app.core.security import get_password_hash, verify_password

# 哈希密码
hashed_password = get_password_hash("plain_password")

# 验证密码
is_valid = verify_password("plain_password", hashed_password)
```

## 🧪 测试

### 运行测试

```bash
# 使用 pytest
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/

# 或使用 poetry
poetry run pytest

# 运行特定测试文件
pytest tests/test_auth.py -v
```

### 测试覆盖的功能

- ✅ 用户注册
- ✅ 用户登录和 JWT 令牌生成
- ✅ 受保护路由的访问控制
- ✅ 无效令牌的处理
- ✅ 用户信息的获取

### 手动测试步骤

1. **启动服务**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **注册新用户**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
   -H "Content-Type: application/json" \
   -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
   ```

3. **登录获取令牌**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
   -H "Content-Type: application/x-www-form-urlencoded" \
   -d "username=testuser&password=password123"
   ```

4. **使用令牌访问受保护路由**
   ```bash
   curl -X GET "http://localhost:8000/items/" \
   -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

## 🚀 部署

### Docker 部署

1. **创建 Dockerfile**

```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

2. **构建和运行**

```bash
# 构建镜像
docker build -t fastapi-app .

# 运行容器
docker run -d --name my-fastapi-app -p 80:80 fastapi-app
```

### 云服务部署

支持部署到以下平台：
- AWS (Elastic Beanstalk, Lambda)
- Google Cloud (Cloud Run, App Engine)
- Azure (App Service)
- Heroku
- Vercel
- Railway

## 🔍 监控和日志

### 日志配置

```python
import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}
```

### 性能监控

可以集成以下工具进行监控：
- Prometheus + Grafana
- New Relic
- DataDog
- Sentry (错误追踪)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [Starlette 文档](https://www.starlette.io/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)

## 📞 支持

如果您有任何问题或建议，请：
- 创建 [Issue](https://github.com/your-username/fastapi/issues)
- 发送邮件至 your-email@example.com

---

**⭐ 如果这个项目对您有帮助，请给它一个星标！**
