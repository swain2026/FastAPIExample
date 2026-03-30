from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """Get role by ID"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get role by name"""
    return db.query(Role).filter(Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Role]:
    """Get role list"""
    query = db.query(Role)
    if not include_inactive:
        query = query.filter(Role.is_active == True)
    return query.offset(skip).limit(limit).all()


def create_role(db: Session, role: RoleCreate) -> Role:
    """Create new role"""
    db_role = Role(
        name=role.name,
        description=role.description,
        is_active=role.is_active
    )
    try:
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError:
        db.rollback()
        raise ValueError("Role name already exists")


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """Update role"""
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return None
    
    update_data = role_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    try:
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError:
        db.rollback()
        raise ValueError("Role name already exists")


def delete_role(db: Session, role_id: int) -> bool:
    """Delete role"""
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return False
    
    if db_role.users:
        raise ValueError(f"Cannot delete role, {len(db_role.users)} users are still using this role")
    
    db.delete(db_role)
    db.commit()
    return True


def get_role_users(db: Session, role_id: int) -> List[User]:
    """Get all users under role"""
    role = get_role_by_id(db, role_id)
    return role.users if role else []


def count_users_by_role(db: Session, role_id: int) -> int:
    """Count users by role"""
    role = get_role_by_id(db, role_id)
    return len(role.users) if role else 0