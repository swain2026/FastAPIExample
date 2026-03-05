from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "FastAPI Demo"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # JWT 配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # 数据库配置
    database_url: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"


settings = Settings()