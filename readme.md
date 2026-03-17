# FastAPI JWT Authentication Example Project

A high-performance Web API example project built with FastAPI framework, integrated with JWT authentication system.

## 🚀 Features

- **High Performance**: Built on Starlette and Pydantic for exceptional performance
- **JWT Authentication**: Complete user registration, login, and authorization system
- **Automatic Documentation**: Auto-generated interactive API documentation (Swagger UI and ReDoc)
- **Type Safety**: Data validation using Python type hints
- **Modern**: Support for async/await asynchronous programming
- **Database Integration**: Data persistence using SQLAlchemy
- **Easy Testing**: Built-in testing support
- **Standardized**: Follows OpenAPI specifications

## 📋 Requirements

- Python 3.8+
- pip or poetry

## 🛠️ Installation

### Using pip

```bash
# Clone the project
git clone <repository-url>
cd fastapi

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Using poetry

```bash
# Install poetry (if not already installed)
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## 🏃‍♂️ Quick Start

1. **Start the development server**

```bash
# Start with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using poetry
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access API Documentation**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 📁 Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── api/                        # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependencies (authentication, etc.)
│   │   └── endpoints/              # Endpoint definitions
│   │       ├── __init__.py
│   │       ├── auth.py             # Authentication endpoints
│   │       └── items.py            # Item endpoints
│   ├── core/                       # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Application configuration
│   │   └── security.py             # JWT security
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   └── user.py                 # User model
│   ├── schemas/                    # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py                 # User schema
│   ├── crud/                       # Database operations
│   │   ├── __init__.py
│   │   └── user.py                 # User CRUD operations
│   └── db/                         # Database related
│       ├── __init__.py
│       └── database.py             # Database connection
├── tests/                          # Test files
│   ├── __init__.py
│   └── test_auth.py                # Authentication tests
├── requirements.txt                 # Dependencies list
├── .env.example                    # Environment variables example
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables

1. **Copy the environment variables example file**

```bash
cp .env.example .env
```

2. **Edit the `.env` file and configure the following variables**

```env
# Application configuration
APP_NAME="FastAPI Demo"
APP_VERSION="1.0.0"
DEBUG=true

# JWT configuration
SECRET_KEY="your-super-secret-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database configuration
DATABASE_URL="sqlite:///./app.db"
```

**⚠️ Important**: In production, make sure to change `SECRET_KEY` to a strong random string!

## 🔐 Authentication System

### JWT Authentication Flow

1. **User Registration**
   ```bash
   POST /auth/register
   {
     "username": "your_username",
     "email": "your_email@example.com",
     "password": "your_password"
   }
   ```

2. **User Login**
   ```bash
   POST /auth/login
   Content-Type: application/x-www-form-urlencoded
   
   username=your_username&password=your_password
   ```

3. **Access Protected Routes**
   ```bash
   GET /items/
   Authorization: Bearer <your_jwt_token>
   ```

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | User registration | None |
| POST | `/auth/login` | User login | None |
| GET | `/auth/me` | Get current user info | JWT |

### Protected Routes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/items/` | Get items list | JWT |
| GET | `/items/{item_id}` | Get single item | JWT |
| POST | `/items/` | Create item | JWT |

### Code Examples

#### Using JWT Dependencies

```python
from app.api.deps import get_current_active_user
from app.models.user import User

@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}!"}
```

#### Password Hashing

```python
from app.core.security import get_password_hash, verify_password

# Hash password
hashed_password = get_password_hash("plain_password")

# Verify password
is_valid = verify_password("plain_password", hashed_password)
```

## 🧪 Testing

### Running Tests

```bash
# Using pytest
pytest

# Run tests with coverage report
pytest --cov=app tests/

# Or using poetry
poetry run pytest

# Run specific test file
pytest tests/test_auth.py -v
```

### Test Coverage

- ✅ User registration
- ✅ User login and JWT token generation
- ✅ Protected route access control
- ✅ Invalid token handling
- ✅ User information retrieval

### Manual Testing Steps

1. **Start the service**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Register a new user**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
   -H "Content-Type: application/json" \
   -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
   ```

3. **Login to get token**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
   -H "Content-Type: application/x-www-form-urlencoded" \
   -d "username=testuser&password=password123"
   ```

4. **Access protected route with token**
   ```bash
   curl -X GET "http://localhost:8000/items/" \
   -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile**

```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

2. **Build and Run**

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d --name my-fastapi-app -p 80:80 fastapi-app
```

### Cloud Service Deployment

Supports deployment to the following platforms:
- AWS (Elastic Beanstalk, Lambda)
- Google Cloud (Cloud Run, App Engine)
- Azure (App Service)
- Heroku
- Vercel
- Railway

## 🔍 Monitoring and Logging

### Logging Configuration

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

### Performance Monitoring

Can integrate the following tools for monitoring:
- Prometheus + Grafana
- New Relic
- DataDog
- Sentry (error tracking)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Links

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [Starlette Documentation](https://www.starlette.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

## 📞 Support

If you have any questions or suggestions, please:
- Create an [Issue](https://github.com/your-username/fastapi/issues)
- Send an email to your-email@example.com

---

**⭐ If this project helps you, please give it a star!**
