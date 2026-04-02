from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    permissions: Optional[List[int]] = Field(default_factory=list, description="List of permission IDs")


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[int]] = Field(default=None, description="List of permission IDs")


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleUserSummary(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class RolePermissionSummary(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    type: str
    path: Optional[str] = None
    method: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class RoleWithUsers(RoleResponse):
    users: List[RoleUserSummary] = Field(default_factory=list)


class RoleWithDetails(RoleResponse):
    users: List[RoleUserSummary] = Field(default_factory=list)
    permissions: List[RolePermissionSummary] = Field(default_factory=list)