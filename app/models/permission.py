from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum

# Many-to-many: roles <-> permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class PermissionType(str, enum.Enum):
    api = "api"
    menu = "menu"
    button = "button"


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="Permission identifier, e.g. user.create")
    display_name = Column(String(100), nullable=True, comment="Human-readable name, e.g. Create User")
    description = Column(Text, nullable=True, comment="Permission description")
    type = Column(Enum(PermissionType), default=PermissionType.api, comment="Permission type: api, menu, or button")
    path = Column(String(255), nullable=True, comment="Associated API path or frontend route")
    method = Column(String(10), nullable=True, comment="HTTP method, e.g. GET, POST, PUT, DELETE")
    parent_id = Column(Integer, default=0, comment="Parent permission ID for tree structure")
    sort_order = Column(Integer, default=0, comment="Sort order")
    icon = Column(String(50), nullable=True, comment="Icon identifier")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
