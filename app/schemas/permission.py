from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.permission import PermissionType


class PermissionBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    type: PermissionType = PermissionType.api
    path: Optional[str] = None
    method: Optional[str] = None
    parent_id: int = 0
    sort_order: int = 0
    icon: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[PermissionType] = None
    path: Optional[str] = None
    method: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
