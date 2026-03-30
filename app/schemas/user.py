from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Generic, TypeVar, List
from datetime import datetime
from app.schemas.role import RoleResponse

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    role_ids: List[int] = []


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role_ids: List[int] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_user(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            role_ids=[r.id for r in user.roles],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    class Config:
        from_attributes = True


class UserWithRole(UserResponse):
    roles: List[RoleResponse] = []


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None