from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.permission import PermissionCreate, PermissionUpdate

def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.name == name).first()


def get_permissions(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_perm = Permission(**permission.model_dump())
    try:
        db.add(db_perm)
        db.commit()
        db.refresh(db_perm)
        return db_perm
    except IntegrityError:
        db.rollback()
        raise ValueError("Permission name already exists")


def update_permission(
    db: Session, permission_id: int, permission_update: PermissionUpdate
) -> Optional[Permission]:
    db_perm = get_permission_by_id(db, permission_id)
    if not db_perm:
        return None
    for field, value in permission_update.model_dump(exclude_unset=True).items():
        setattr(db_perm, field, value)
    try:
        db.commit()
        db.refresh(db_perm)
        return db_perm
    except IntegrityError:
        db.rollback()
        raise ValueError("Permission name already exists")


def delete_permission(db: Session, permission_id: int) -> bool:
    db_perm = get_permission_by_id(db, permission_id)
    if not db_perm:
        return False
    db.delete(db_perm)
    db.commit()
    return True


def assign_permissions_to_role(db: Session, role_id: int, permission_ids: List[int]) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise ValueError("Role not found")
    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    if len(permissions) != len(permission_ids):
        raise ValueError("One or more permissions not found")
    role.permissions = permissions
    db.commit()
    db.refresh(role)
    return role


def get_role_permissions(db: Session, role_id: int) -> List[Permission]:
    role = db.query(Role).filter(Role.id == role_id).first()
    return role.permissions if role else []


def remove_permission_from_role(db: Session, role_id: int, permission_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise ValueError("Role not found")
    role.permissions = [p for p in role.permissions if p.id != permission_id]
    db.commit()
    db.refresh(role)
    return role
